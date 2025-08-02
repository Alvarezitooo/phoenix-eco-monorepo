-- PHOENIX EVENT STORE - Clean Schema for Supabase
-- Copy-paste this entire script into Supabase SQL Editor

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own events" ON events;
DROP POLICY IF EXISTS "Services can insert events" ON events;
DROP POLICY IF EXISTS "Users can view own snapshots" ON user_profile_snapshots;

-- Main Event Store table
CREATE TABLE IF NOT EXISTS events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    app_source VARCHAR(50) NOT NULL,
    version INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_stream_id ON events(stream_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_app_source ON events(app_source);
CREATE INDEX IF NOT EXISTS idx_events_stream_timestamp ON events(stream_id, timestamp);

-- Enable RLS
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- User snapshots table (optional)
CREATE TABLE IF NOT EXISTS user_profile_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    snapshot_data JSONB NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, version)
);

-- Snapshots indexes
CREATE INDEX IF NOT EXISTS idx_snapshots_user_id ON user_profile_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_version ON user_profile_snapshots(user_id, version);

-- Enable RLS for snapshots
ALTER TABLE user_profile_snapshots ENABLE ROW LEVEL SECURITY;

-- Security policies
CREATE POLICY "Users can view own events" ON events
    FOR SELECT USING (stream_id = auth.uid());

CREATE POLICY "Services can insert events" ON events
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view own snapshots" ON user_profile_snapshots
    FOR SELECT USING (user_id = auth.uid());

-- Analytics view
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

-- Cleanup function for GDPR compliance
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

-- User snapshot function
CREATE OR REPLACE FUNCTION create_user_snapshot(p_user_id UUID)
RETURNS UUID AS $$
DECLARE
    snapshot_uuid UUID;
    current_version INTEGER;
    user_events JSONB;
BEGIN
    SELECT COALESCE(MAX(version), 0) + 1 
    INTO current_version 
    FROM user_profile_snapshots 
    WHERE user_id = p_user_id;
    
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
    
    INSERT INTO user_profile_snapshots (user_id, snapshot_data, version)
    VALUES (p_user_id, user_events, current_version)
    RETURNING snapshot_id INTO snapshot_uuid;
    
    RETURN snapshot_uuid;
END;
$$ LANGUAGE plpgsql;