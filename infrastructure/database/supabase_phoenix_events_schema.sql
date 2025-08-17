-- 🌉 PHOENIX EVENT STORE - Schéma Supabase Moderne
-- Architecture Event-Sourcing pour l'écosystème Phoenix v2.0
-- Compatible avec PhoenixEventBridge et SupabaseEventStore

-- Table principale Event Store (mise à jour)
CREATE TABLE IF NOT EXISTS phoenix_events (
    -- Identifiants
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id UUID NOT NULL, -- user_id from phoenix_shared_auth
    
    -- Métadonnées événement
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    app_source VARCHAR(50) NOT NULL, -- 'cv', 'letters', 'rise', 'website', 'billing'
    
    -- Données
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Contexte technique
    version VARCHAR(10) DEFAULT '1.0',
    correlation_id UUID,
    user_agent TEXT,
    session_id VARCHAR(100),
    
    -- Métadonnées système
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance optimale
CREATE INDEX IF NOT EXISTS idx_phoenix_events_stream_id ON phoenix_events(stream_id);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_type ON phoenix_events(event_type);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_timestamp ON phoenix_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_app_source ON phoenix_events(app_source);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_stream_timestamp ON phoenix_events(stream_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_correlation ON phoenix_events(correlation_id) WHERE correlation_id IS NOT NULL;

-- Index composites pour analytics
CREATE INDEX IF NOT EXISTS idx_phoenix_events_analytics ON phoenix_events(app_source, event_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_user_journey ON phoenix_events(stream_id, timestamp, app_source);

-- RLS pour sécurité RGPD stricte
ALTER TABLE phoenix_events ENABLE ROW LEVEL SECURITY;

-- Policy: utilisateurs voient leurs propres événements
CREATE POLICY "Users can view own events" ON phoenix_events
    FOR SELECT USING (stream_id = auth.uid());

-- Policy: services avec service_role peuvent tout insérer
CREATE POLICY "Services can insert events" ON phoenix_events
    FOR INSERT WITH CHECK (true);

-- Policy: admin peuvent voir agrégats anonymisés
CREATE POLICY "Admin can view aggregated data" ON phoenix_events
    FOR SELECT USING (
        auth.jwt() ->> 'role' = 'admin' AND 
        payload ? 'anonymized'
    );

-- Vue pour analytics écosystème (données anonymisées)
CREATE OR REPLACE VIEW phoenix_ecosystem_analytics AS
SELECT 
    DATE_TRUNC('day', timestamp) as date,
    app_source,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT stream_id) as unique_users,
    AVG(EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (PARTITION BY stream_id ORDER BY timestamp)))) as avg_time_between_events
FROM phoenix_events 
WHERE timestamp >= NOW() - INTERVAL '90 days'
GROUP BY DATE_TRUNC('day', timestamp), app_source, event_type
ORDER BY date DESC, event_count DESC;

-- Vue pour parcours utilisateur cross-app
CREATE OR REPLACE VIEW phoenix_user_journey AS
SELECT 
    stream_id as user_id,
    event_type,
    app_source,
    timestamp,
    payload ->> 'action_type' as action_type,
    LAG(app_source) OVER (PARTITION BY stream_id ORDER BY timestamp) as previous_app,
    LEAD(app_source) OVER (PARTITION BY stream_id ORDER BY timestamp) as next_app,
    timestamp - LAG(timestamp) OVER (PARTITION BY stream_id ORDER BY timestamp) as time_since_last_event
FROM phoenix_events 
WHERE timestamp >= NOW() - INTERVAL '30 days'
ORDER BY stream_id, timestamp;

-- Vue pour détection des "Nudges" intelligents
CREATE OR REPLACE VIEW phoenix_nudge_opportunities AS
WITH user_app_activity AS (
    SELECT 
        stream_id,
        app_source,
        COUNT(*) as activity_count,
        MAX(timestamp) as last_activity,
        MIN(timestamp) as first_activity
    FROM phoenix_events 
    WHERE timestamp >= NOW() - INTERVAL '30 days'
    GROUP BY stream_id, app_source
),
cross_app_gaps AS (
    SELECT 
        cv.stream_id,
        CASE 
            WHEN cv.activity_count >= 3 AND letters.stream_id IS NULL 
            THEN 'cv_to_letters_nudge'
            WHEN letters.activity_count >= 2 AND rise.stream_id IS NULL 
            THEN 'letters_to_rise_nudge'
            WHEN cv.activity_count >= 1 AND letters.activity_count >= 1 AND rise.stream_id IS NULL
            THEN 'ecosystem_to_rise_nudge'
        END as nudge_type,
        cv.last_activity as cv_last_activity,
        letters.last_activity as letters_last_activity
    FROM user_app_activity cv
    LEFT JOIN user_app_activity letters ON cv.stream_id = letters.stream_id AND letters.app_source = 'letters'
    LEFT JOIN user_app_activity rise ON cv.stream_id = rise.stream_id AND rise.app_source = 'rise'
    WHERE cv.app_source = 'cv'
)
SELECT * FROM cross_app_gaps WHERE nudge_type IS NOT NULL;

-- Table pour tracking des nudges envoyés (éviter spam)
CREATE TABLE IF NOT EXISTS phoenix_nudges_sent (
    nudge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    nudge_type VARCHAR(50) NOT NULL,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    app_source VARCHAR(50) NOT NULL,
    success BOOLEAN DEFAULT false,
    sent_date DATE GENERATED ALWAYS AS (DATE(sent_at)) STORED,
    UNIQUE(user_id, nudge_type, sent_date)
);

-- Index nudges
CREATE INDEX IF NOT EXISTS idx_nudges_user_type ON phoenix_nudges_sent(user_id, nudge_type);
CREATE INDEX IF NOT EXISTS idx_nudges_sent_at ON phoenix_nudges_sent(sent_at);

-- RLS pour nudges
ALTER TABLE phoenix_nudges_sent ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own nudges" ON phoenix_nudges_sent
    FOR SELECT USING (user_id = auth.uid());

-- Function pour nettoyer les anciens événements (RGPD)
CREATE OR REPLACE FUNCTION cleanup_old_phoenix_events(retention_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Supprimer les événements anciens
    DELETE FROM phoenix_events 
    WHERE timestamp < NOW() - INTERVAL '1 day' * retention_days;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log de l'opération de nettoyage
    INSERT INTO phoenix_events (
        stream_id, 
        event_type, 
        app_source, 
        payload
    ) VALUES (
        '00000000-0000-0000-0000-000000000000',
        'system.cleanup_completed',
        'system',
        jsonb_build_object(
            'deleted_events', deleted_count,
            'retention_days', retention_days,
            'cleanup_timestamp', NOW()
        )
    );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function pour créer un événement Phoenix standardisé
CREATE OR REPLACE FUNCTION create_phoenix_event(
    p_stream_id UUID,
    p_event_type VARCHAR(100),
    p_app_source VARCHAR(50),
    p_payload JSONB DEFAULT '{}'::jsonb,
    p_correlation_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    event_uuid UUID;
BEGIN
    INSERT INTO phoenix_events (
        stream_id,
        event_type,
        app_source,
        payload,
        correlation_id,
        metadata
    ) VALUES (
        p_stream_id,
        p_event_type,
        p_app_source,
        p_payload,
        p_correlation_id,
        jsonb_build_object(
            'created_via', 'sql_function',
            'server_timestamp', NOW()
        )
    )
    RETURNING event_id INTO event_uuid;
    
    RETURN event_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function pour générer des analytics temps réel
CREATE OR REPLACE FUNCTION get_phoenix_ecosystem_stats(days_back INTEGER DEFAULT 30)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'period_days', days_back,
        'total_events', (
            SELECT COUNT(*) FROM phoenix_events 
            WHERE timestamp >= NOW() - INTERVAL '1 day' * days_back
        ),
        'unique_users', (
            SELECT COUNT(DISTINCT stream_id) FROM phoenix_events 
            WHERE timestamp >= NOW() - INTERVAL '1 day' * days_back
        ),
        'app_breakdown', (
            SELECT jsonb_object_agg(app_source, app_stats)
            FROM (
                SELECT 
                    app_source,
                    jsonb_build_object(
                        'events', COUNT(*),
                        'users', COUNT(DISTINCT stream_id)
                    ) as app_stats
                FROM phoenix_events 
                WHERE timestamp >= NOW() - INTERVAL '1 day' * days_back
                GROUP BY app_source
            ) app_data
        ),
        'top_events', (
            SELECT jsonb_object_agg(event_type, event_count)
            FROM (
                SELECT event_type, COUNT(*) as event_count
                FROM phoenix_events 
                WHERE timestamp >= NOW() - INTERVAL '1 day' * days_back
                GROUP BY event_type
                ORDER BY event_count DESC
                LIMIT 10
            ) top_events_data
        ),
        'generated_at', NOW()
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Commentaires documentation
COMMENT ON TABLE phoenix_events IS 'Event Store principal Phoenix v2.0 - Architecture Event-Sourcing avec support Nudges intelligents';
COMMENT ON COLUMN phoenix_events.event_type IS 'Types: user.registered, cv.uploaded, letter.generated, etc. (format: domain.action)';
COMMENT ON COLUMN phoenix_events.app_source IS 'Source: cv, letters, rise, website, billing';
COMMENT ON COLUMN phoenix_events.payload IS 'Données événement JSON - validées et sanitisées côté application';
COMMENT ON COLUMN phoenix_events.correlation_id IS 'Pour tracer les workflows cross-app (ex: CV → Letter generation)';

COMMENT ON VIEW phoenix_nudge_opportunities IS 'Détecte automatiquement les opportunités de nudges cross-app pour engagement utilisateur';
COMMENT ON FUNCTION get_phoenix_ecosystem_stats(INTEGER) IS 'Génère des analytics écosystème en temps réel pour dashboard admin';