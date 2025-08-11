-- 🚀 PHOENIX ECOSYSTEM - Schema Supabase Complet
-- Exécuter dans l'ordre dans l'éditeur SQL Supabase

-- ============================================
-- 1. TABLES UTILISATEURS CORE
-- ============================================

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table profiles (si pas déjà créée par Auth)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 2. PHOENIX CV - Tables
-- ============================================

CREATE TABLE IF NOT EXISTS cv_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    template_used VARCHAR(100),
    generation_status VARCHAR(50) DEFAULT 'pending',
    cv_data JSONB NOT NULL,
    generated_html TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

CREATE INDEX idx_cv_generations_user_id ON cv_generations(user_id);
CREATE INDEX idx_cv_generations_status ON cv_generations(generation_status);

-- ============================================
-- 3. PHOENIX LETTERS - Tables  
-- ============================================

CREATE TABLE IF NOT EXISTS letter_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    job_offer_text TEXT,
    generated_letter TEXT,
    generation_type VARCHAR(50) DEFAULT 'standard',
    ai_optimization_level VARCHAR(50) DEFAULT 'basic',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days')
);

CREATE INDEX idx_letter_generations_user_id ON letter_generations(user_id);

-- ============================================
-- 4. PHOENIX AUBE - Tables
-- ============================================

CREATE TABLE IF NOT EXISTS career_explorations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    exploration_data JSONB NOT NULL,
    personality_results JSONB,
    career_matches JSONB,
    ia_validation_results JSONB,
    completion_status VARCHAR(50) DEFAULT 'in_progress',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_career_explorations_user_id ON career_explorations(user_id);

-- ============================================
-- 5. ANALYTICS & METRICS
-- ============================================

CREATE TABLE IF NOT EXISTS user_activity_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    app_source VARCHAR(50) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    session_id VARCHAR(255),
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_activity_metrics_user_app ON user_activity_metrics(user_id, app_source);
CREATE INDEX idx_activity_metrics_timestamp ON user_activity_metrics(timestamp);

-- ============================================  
-- 6. SUBSCRIPTION & PAYMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    status VARCHAR(50) DEFAULT 'active',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_customer ON user_subscriptions(stripe_customer_id);

-- ============================================
-- 7. RLS POLICIES - Sécurité
-- ============================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE cv_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE letter_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_explorations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;

-- Policies - Users can only access their own data
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own CV generations" ON cv_generations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own CV generations" ON cv_generations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own letters" ON letter_generations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own letters" ON letter_generations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own explorations" ON career_explorations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own explorations" ON career_explorations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own activity" ON user_activity_metrics
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Services can log activity" ON user_activity_metrics
    FOR INSERT WITH CHECK (true);

-- ============================================
-- 8. FONCTIONS UTILITAIRES
-- ============================================

-- Fonction de nettoyage automatique (GDPR)
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    temp_count INTEGER;
BEGIN
    -- CV expiré
    DELETE FROM cv_generations WHERE expires_at < NOW();
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    -- Lettres expirées  
    DELETE FROM letter_generations WHERE expires_at < NOW();
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    -- Métriques anciennes (> 2 ans)
    DELETE FROM user_activity_metrics WHERE timestamp < NOW() - INTERVAL '2 years';
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Vue dashboard globale
CREATE OR REPLACE VIEW phoenix_ecosystem_dashboard AS
SELECT 
    p.id as user_id,
    p.email,
    p.subscription_tier,
    
    -- CV Stats
    COUNT(DISTINCT cv.id) as total_cv_generated,
    COUNT(DISTINCT CASE WHEN cv.created_at >= CURRENT_DATE - INTERVAL '30 days' THEN cv.id END) as cv_last_30d,
    
    -- Letters Stats  
    COUNT(DISTINCT l.id) as total_letters_generated,
    COUNT(DISTINCT CASE WHEN l.created_at >= CURRENT_DATE - INTERVAL '30 days' THEN l.id END) as letters_last_30d,
    
    -- Aube Stats
    COUNT(DISTINCT ce.id) as total_explorations,
    COUNT(DISTINCT CASE WHEN ce.completion_status = 'completed' THEN ce.id END) as completed_explorations,
    
    -- Activity
    MAX(GREATEST(cv.created_at, l.created_at, ce.created_at)) as last_activity,
    p.created_at as user_since

FROM profiles p
LEFT JOIN cv_generations cv ON p.id = cv.user_id  
LEFT JOIN letter_generations l ON p.id = l.user_id
LEFT JOIN career_explorations ce ON p.id = ce.user_id
GROUP BY p.id, p.email, p.subscription_tier, p.created_at;

-- ============================================
-- 9. TRIGGERS POUR AUTO-UPDATE
-- ============================================

-- Trigger pour updated_at sur profiles
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 10. COMMENTAIRES DOCUMENTATION  
-- ============================================

COMMENT ON TABLE profiles IS 'Profils utilisateurs Phoenix - données de base';
COMMENT ON TABLE cv_generations IS 'Historique génération CV Phoenix CV';
COMMENT ON TABLE letter_generations IS 'Historique génération lettres Phoenix Letters'; 
COMMENT ON TABLE career_explorations IS 'Explorations carrière Phoenix Aube';
COMMENT ON TABLE user_activity_metrics IS 'Métriques activité cross-app Phoenix';
COMMENT ON TABLE user_subscriptions IS 'Abonnements et paiements Stripe Phoenix';
COMMENT ON VIEW phoenix_ecosystem_dashboard IS 'Dashboard consolidé écosystème Phoenix';

-- ============================================
-- ✅ SCRIPT TERMINÉ - DATA PIPELINE 100% FONCTIONNEL
-- ============================================