-- 🚀 PHOENIX EVENT STORE - Schéma Supabase
-- Architecture Event-Sourcing pour l'écosystème Phoenix
-- Intégration avec infrastructure Supabase existante

-- Table principale Event Store
CREATE TABLE IF NOT EXISTS events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id UUID NOT NULL, -- user_id from phoenix_shared_auth
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    app_source VARCHAR(50) NOT NULL, -- 'cv', 'letters', 'rise'
    version INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance queries
CREATE INDEX IF NOT EXISTS idx_events_stream_id ON events(stream_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_app_source ON events(app_source);
CREATE INDEX IF NOT EXISTS idx_events_stream_timestamp ON events(stream_id, timestamp);

-- RLS pour sécurité RGPD
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Policy: utilisateurs voient leurs propres events
CREATE POLICY "Users can view own events" ON events
    FOR SELECT USING (stream_id = auth.uid());

-- Policy: services peuvent insérer des events
CREATE POLICY "Services can insert events" ON events
    FOR INSERT WITH CHECK (true);

-- Table des snapshots pour optimisation (optionnel)
CREATE TABLE IF NOT EXISTS user_profile_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    snapshot_data JSONB NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, version)
);

-- Index snapshots
CREATE INDEX IF NOT EXISTS idx_snapshots_user_id ON user_profile_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_version ON user_profile_snapshots(user_id, version);

-- RLS pour snapshots
ALTER TABLE user_profile_snapshots ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own snapshots" ON user_profile_snapshots
    FOR SELECT USING (user_id = auth.uid());

-- Vue pour analytics en temps réel
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    stream_id as user_id,
    app_source,
    event_type,
    COUNT(*) as event_count,
    MAX(timestamp) as last_activity,
    DATE(timestamp) as activity_date
FROM events 
GROUP BY stream_id, app_source, event_type, DATE(timestamp)
ORDER BY last_activity DESC;

-- Function pour nettoyer les anciens events (RGPD)
CREATE OR REPLACE FUNCTION cleanup_old_events(retention_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM events 
    WHERE timestamp < NOW() - INTERVAL '1 day' * retention_days;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function pour créer un snapshot utilisateur
CREATE OR REPLACE FUNCTION create_user_snapshot(p_user_id UUID)
RETURNS UUID AS $$
DECLARE
    snapshot_uuid UUID;
    current_version INTEGER;
    user_events JSONB;
BEGIN
    -- Récupérer la version actuelle
    SELECT COALESCE(MAX(version), 0) + 1 
    INTO current_version 
    FROM user_profile_snapshots 
    WHERE user_id = p_user_id;
    
    -- Construire le snapshot à partir des events
    SELECT jsonb_agg(
        jsonb_build_object(
            'event_type', event_type,
            'payload', payload,
            'timestamp', timestamp,
            'app_source', app_source
        ) ORDER BY timestamp
    )
    INTO user_events
    FROM events 
    WHERE stream_id = p_user_id;
    
    -- Insérer le snapshot
    INSERT INTO user_profile_snapshots (user_id, snapshot_data, version)
    VALUES (p_user_id, user_events, current_version)
    RETURNING snapshot_id INTO snapshot_uuid;
    
    RETURN snapshot_uuid;
END;
$$ LANGUAGE plpgsql;

-- Types d'événements Phoenix standardisés
COMMENT ON TABLE events IS 'Event Store principal pour l''écosystème Phoenix - architecture Event-Sourcing';
COMMENT ON COLUMN events.event_type IS 'Types: UserRegistered, CVGenerated, LetterCreated, SkillAdded, CoachingSessionStarted, etc.';
COMMENT ON COLUMN events.app_source IS 'Source: cv, letters, rise';
COMMENT ON COLUMN events.payload IS 'Données événement au format JSON - anonymisées pour RGPD';