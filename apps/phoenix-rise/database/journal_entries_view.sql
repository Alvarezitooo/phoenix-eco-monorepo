-- 📊 Phoenix Rise - Table de Vue Matérialisée pour Journal Entries
-- Stocke les données de lecture optimisées pour Phoenix Rise Dashboard

-- Création de la table pour les entrées de journal (vue matérialisée)
CREATE TABLE IF NOT EXISTS journal_entries_view (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    journal_entry_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Données principales
    mood INTEGER NOT NULL CHECK (mood >= 1 AND mood <= 10),
    confidence INTEGER NOT NULL CHECK (confidence >= 1 AND confidence <= 10), 
    notes TEXT,
    
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    date_logged DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Données calculées pour analytics
    mood_trend VARCHAR(20), -- 'up', 'down', 'stable'
    confidence_trend VARCHAR(20), -- 'up', 'down', 'stable' 
    
    -- Indexation
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE
);

-- Index pour optimiser les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_journal_entries_view_user_id ON journal_entries_view(user_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_view_date_logged ON journal_entries_view(date_logged);
CREATE INDEX IF NOT EXISTS idx_journal_entries_view_user_date ON journal_entries_view(user_id, date_logged);

-- Index pour les analytics
CREATE INDEX IF NOT EXISTS idx_journal_entries_view_mood ON journal_entries_view(mood);
CREATE INDEX IF NOT EXISTS idx_journal_entries_view_confidence ON journal_entries_view(confidence);

-- Vue pour statistiques rapides par utilisateur
CREATE OR REPLACE VIEW user_journal_stats AS
SELECT 
    user_id,
    COUNT(*) as total_entries,
    AVG(mood) as avg_mood,
    AVG(confidence) as avg_confidence,
    MAX(date_logged) as last_entry_date,
    MIN(date_logged) as first_entry_date,
    
    -- Tendances sur les 7 derniers jours
    AVG(CASE WHEN date_logged >= CURRENT_DATE - INTERVAL '7 days' THEN mood END) as mood_7d_avg,
    AVG(CASE WHEN date_logged >= CURRENT_DATE - INTERVAL '7 days' THEN confidence END) as confidence_7d_avg,
    
    -- Tendances sur les 30 derniers jours  
    AVG(CASE WHEN date_logged >= CURRENT_DATE - INTERVAL '30 days' THEN mood END) as mood_30d_avg,
    AVG(CASE WHEN date_logged >= CURRENT_DATE - INTERVAL '30 days' THEN confidence END) as confidence_30d_avg
    
FROM journal_entries_view
GROUP BY user_id;

-- Table pour stocker les objectifs utilisateur
CREATE TABLE IF NOT EXISTS user_objectives_view (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    objective_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Données principales
    title VARCHAR(500) NOT NULL,
    description TEXT,
    objective_type VARCHAR(100) DEFAULT 'personal',
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'paused'
    
    -- Dates
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    target_date DATE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexation
    CONSTRAINT fk_objectives_user_id FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE
);

-- Index pour les objectifs
CREATE INDEX IF NOT EXISTS idx_user_objectives_view_user_id ON user_objectives_view(user_id);
CREATE INDEX IF NOT EXISTS idx_user_objectives_view_status ON user_objectives_view(status);
CREATE INDEX IF NOT EXISTS idx_user_objectives_view_user_status ON user_objectives_view(user_id, status);

-- Table pour les sessions de coaching
CREATE TABLE IF NOT EXISTS coaching_sessions_view (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Données session
    session_type VARCHAR(50) NOT NULL, -- 'free', 'premium'
    user_tier VARCHAR(50) DEFAULT 'free',
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    
    -- Métadonnées
    ai_prompts_used INTEGER DEFAULT 0,
    user_satisfaction INTEGER CHECK (user_satisfaction >= 1 AND user_satisfaction <= 5),
    
    -- Indexation
    CONSTRAINT fk_coaching_user_id FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE
);

-- Index pour sessions coaching
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_view_user_id ON coaching_sessions_view(user_id);
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_view_started_at ON coaching_sessions_view(started_at);
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_view_session_type ON coaching_sessions_view(session_type);

-- Vue pour dashboard metrics
CREATE OR REPLACE VIEW user_dashboard_metrics AS
SELECT 
    p.id as user_id,
    p.email,
    p.full_name,
    
    -- Journal stats
    COALESCE(j.total_entries, 0) as journal_entries_count,
    COALESCE(j.avg_mood, 0) as avg_mood,
    COALESCE(j.avg_confidence, 0) as avg_confidence,
    j.last_entry_date,
    
    -- Objectives stats
    COALESCE(o.total_objectives, 0) as total_objectives,
    COALESCE(o.active_objectives, 0) as active_objectives,
    COALESCE(o.completed_objectives, 0) as completed_objectives,
    
    -- Coaching stats
    COALESCE(c.total_sessions, 0) as total_coaching_sessions,
    COALESCE(c.recent_sessions, 0) as recent_coaching_sessions,
    c.last_session_date
    
FROM profiles p
LEFT JOIN user_journal_stats j ON p.id = j.user_id
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as total_objectives,
        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_objectives,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_objectives
    FROM user_objectives_view 
    GROUP BY user_id
) o ON p.id = o.user_id
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as total_sessions,
        COUNT(CASE WHEN started_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as recent_sessions,
        MAX(started_at) as last_session_date
    FROM coaching_sessions_view 
    GROUP BY user_id
) c ON p.id = c.user_id;

-- Commentaires pour documentation
COMMENT ON TABLE journal_entries_view IS 'Vue matérialisée pour les entrées de journal Phoenix Rise - optimisée pour lecture';
COMMENT ON TABLE user_objectives_view IS 'Vue matérialisée pour les objectifs utilisateur Phoenix Rise';
COMMENT ON TABLE coaching_sessions_view IS 'Vue matérialisée pour les sessions de coaching Phoenix Rise';
COMMENT ON VIEW user_dashboard_metrics IS 'Vue consolidée pour le dashboard Phoenix Rise avec toutes les métriques utilisateur';