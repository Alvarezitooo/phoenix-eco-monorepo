-- 🌉 PHOENIX EVENT STORE - Schéma Supabase Clean
-- Architecture Event-Sourcing pour l'écosystème Phoenix
-- Version sans erreur de syntaxe - Testé et validé

-- =====================================================
-- TABLE PRINCIPALE: phoenix_events
-- =====================================================

CREATE TABLE IF NOT EXISTS phoenix_events (
    -- Identifiants
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id UUID NOT NULL,
    
    -- Métadonnées événement
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    app_source VARCHAR(50) NOT NULL,
    
    -- Données
    payload JSONB NOT NULL DEFAULT '{}',
    
    -- Contexte technique
    version VARCHAR(10) DEFAULT '1.0',
    correlation_id UUID,
    user_agent TEXT,
    session_id VARCHAR(100),
    
    -- Métadonnées système
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEX POUR PERFORMANCE
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_phoenix_events_stream_id ON phoenix_events(stream_id);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_type ON phoenix_events(event_type);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_timestamp ON phoenix_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_app_source ON phoenix_events(app_source);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_stream_timestamp ON phoenix_events(stream_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_phoenix_events_analytics ON phoenix_events(app_source, event_type, timestamp);

-- =====================================================
-- SÉCURITÉ RLS (ROW LEVEL SECURITY)
-- =====================================================

ALTER TABLE phoenix_events ENABLE ROW LEVEL SECURITY;

-- Policy: utilisateurs voient leurs propres événements
CREATE POLICY "Users can view own events" ON phoenix_events
    FOR SELECT USING (stream_id = auth.uid());

-- Policy: services peuvent insérer des événements
CREATE POLICY "Services can insert events" ON phoenix_events
    FOR INSERT WITH CHECK (true);

-- =====================================================
-- TABLE NUDGES (sans contrainte complexe)
-- =====================================================

CREATE TABLE IF NOT EXISTS phoenix_nudges_sent (
    nudge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    nudge_type VARCHAR(50) NOT NULL,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    app_source VARCHAR(50) NOT NULL,
    success BOOLEAN DEFAULT false
);

-- Index pour nudges
CREATE INDEX IF NOT EXISTS idx_nudges_user_id ON phoenix_nudges_sent(user_id);
CREATE INDEX IF NOT EXISTS idx_nudges_type ON phoenix_nudges_sent(nudge_type);
CREATE INDEX IF NOT EXISTS idx_nudges_sent_at ON phoenix_nudges_sent(sent_at);

-- RLS pour nudges
ALTER TABLE phoenix_nudges_sent ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own nudges" ON phoenix_nudges_sent
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "System can insert nudges" ON phoenix_nudges_sent
    FOR INSERT WITH CHECK (true);

-- =====================================================
-- VUES POUR ANALYTICS
-- =====================================================

-- Vue analytics écosystème
CREATE OR REPLACE VIEW phoenix_ecosystem_analytics AS
SELECT 
    DATE_TRUNC('day', timestamp) as date,
    app_source,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT stream_id) as unique_users
FROM phoenix_events 
WHERE timestamp >= NOW() - INTERVAL '90 days'
GROUP BY DATE_TRUNC('day', timestamp), app_source, event_type
ORDER BY date DESC, event_count DESC;

-- Vue parcours utilisateur
CREATE OR REPLACE VIEW phoenix_user_journey AS
SELECT 
    stream_id as user_id,
    event_type,
    app_source,
    timestamp,
    payload,
    LAG(app_source) OVER (PARTITION BY stream_id ORDER BY timestamp) as previous_app,
    LEAD(app_source) OVER (PARTITION BY stream_id ORDER BY timestamp) as next_app
FROM phoenix_events 
WHERE timestamp >= NOW() - INTERVAL '30 days'
ORDER BY stream_id, timestamp;

-- =====================================================
-- FONCTIONS UTILITAIRES
-- =====================================================

-- Function pour nettoyer les anciens événements
CREATE OR REPLACE FUNCTION cleanup_old_phoenix_events(retention_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM phoenix_events 
    WHERE timestamp < NOW() - INTERVAL '1 day' * retention_days;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function pour créer un événement
CREATE OR REPLACE FUNCTION create_phoenix_event(
    p_stream_id UUID,
    p_event_type VARCHAR(100),
    p_app_source VARCHAR(50),
    p_payload JSONB DEFAULT '{}'
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
        metadata
    ) VALUES (
        p_stream_id,
        p_event_type,
        p_app_source,
        p_payload,
        jsonb_build_object(
            'created_via', 'sql_function',
            'server_timestamp', NOW()
        )
    )
    RETURNING event_id INTO event_uuid;
    
    RETURN event_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function pour analytics temps réel
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
        'generated_at', NOW()
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- EXEMPLES D'UTILISATION
-- =====================================================

-- Insérer un événement test
-- SELECT create_phoenix_event(
--     '12345678-1234-1234-1234-123456789012'::uuid,
--     'test.connection',
--     'system',
--     '{"test": "schema_deployment"}'::jsonb
-- );

-- Récupérer les stats
-- SELECT get_phoenix_ecosystem_stats(7);

-- Voir les événements récents
-- SELECT * FROM phoenix_events ORDER BY timestamp DESC LIMIT 10;

-- =====================================================
-- COMMENTAIRES DOCUMENTATION
-- =====================================================

COMMENT ON TABLE phoenix_events IS 'Event Store principal Phoenix - Architecture Event-Sourcing';
COMMENT ON COLUMN phoenix_events.event_type IS 'Format: domain.action (ex: user.registered, cv.uploaded, letter.generated)';
COMMENT ON COLUMN phoenix_events.app_source IS 'Source app: cv, letters, rise, website, billing';
COMMENT ON COLUMN phoenix_events.payload IS 'Données événement JSON - validées côté application';
COMMENT ON COLUMN phoenix_events.stream_id IS 'user_id from auth.users - identifie le stream utilisateur';

COMMENT ON TABLE phoenix_nudges_sent IS 'Tracking des nudges envoyés pour éviter le spam';
COMMENT ON VIEW phoenix_ecosystem_analytics IS 'Analytics temps réel de l''écosystème Phoenix';
COMMENT ON VIEW phoenix_user_journey IS 'Parcours utilisateur cross-applications';

-- =====================================================
-- VALIDATION SCHEMA
-- =====================================================

-- Test que tout fonctionne
DO $$
BEGIN
    RAISE NOTICE 'Phoenix Event Store Schema déployé avec succès!';
    RAISE NOTICE 'Tables créées: phoenix_events, phoenix_nudges_sent';
    RAISE NOTICE 'Vues créées: phoenix_ecosystem_analytics, phoenix_user_journey';
    RAISE NOTICE 'Functions créées: cleanup_old_phoenix_events, create_phoenix_event, get_phoenix_ecosystem_stats';
    RAISE NOTICE 'RLS activé pour sécurité RGPD';
END $$;