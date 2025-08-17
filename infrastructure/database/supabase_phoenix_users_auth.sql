-- 🔐 PHOENIX USERS & AUTH - Schéma Supabase Complet
-- Gestion utilisateurs, abonnements et authentification pour l'écosystème Phoenix
-- À exécuter APRÈS supabase_phoenix_events_clean.sql

-- =====================================================
-- EXTENSIONS REQUISES
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE PROFILES (Extension des users Supabase Auth)
-- =====================================================

CREATE TABLE IF NOT EXISTS profiles (
    -- ID référence auth.users de Supabase
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Informations utilisateur
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    
    -- Abonnement global (pour compatibilité)
    subscription_tier VARCHAR(50) DEFAULT 'free',
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ DEFAULT NOW(),
    
    -- Préférences utilisateur
    preferences JSONB DEFAULT '{
        "email_notifications": true,
        "marketing_emails": false,
        "language": "fr",
        "timezone": "Europe/Paris"
    }'::jsonb,
    
    -- Stats d'engagement
    total_cv_generated INT DEFAULT 0,
    total_letters_generated INT DEFAULT 0,
    total_coaching_sessions INT DEFAULT 0
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON profiles(created_at);

-- =====================================================
-- TABLE ABONNEMENTS GRANULAIRES PAR APP
-- =====================================================

CREATE TABLE IF NOT EXISTS user_subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Application et tier
    app_name VARCHAR(50) NOT NULL, -- 'cv', 'letters', 'rise', 'ecosystem'
    subscription_tier VARCHAR(50) NOT NULL, -- 'free', 'premium', 'pro'
    subscription_status VARCHAR(50) DEFAULT 'active', -- 'active', 'cancelled', 'past_due'
    
    -- Intégration Stripe
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    stripe_product_id VARCHAR(255),
    stripe_price_id VARCHAR(255),
    
    -- Période d'abonnement
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,
    
    -- Facturation
    amount_paid DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    cancelled_at TIMESTAMPTZ,
    
    -- Contraintes
    UNIQUE(user_id, app_name),
    CHECK(app_name IN ('cv', 'letters', 'rise', 'ecosystem')),
    CHECK(subscription_tier IN ('free', 'premium', 'pro')),
    CHECK(subscription_status IN ('active', 'cancelled', 'past_due', 'trialing', 'incomplete'))
);

-- Index pour performance et requêtes Stripe
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_app ON user_subscriptions(user_id, app_name);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer ON user_subscriptions(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_subscription ON user_subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON user_subscriptions(subscription_status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_tier ON user_subscriptions(subscription_tier);

-- =====================================================
-- TABLE LIMITES D'USAGE PAR USER
-- =====================================================

CREATE TABLE IF NOT EXISTS user_usage_limits (
    limit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Période (monthly reset)
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    
    -- Limites Phoenix CV
    cv_generations_used INT DEFAULT 0,
    cv_generations_limit INT DEFAULT 3, -- Free: 3, Premium: illimité
    cv_uploads_used INT DEFAULT 0,
    cv_uploads_limit INT DEFAULT 5,
    
    -- Limites Phoenix Letters  
    letters_generated_used INT DEFAULT 0,
    letters_generated_limit INT DEFAULT 2, -- Free: 2, Premium: illimité
    mirror_match_used INT DEFAULT 0,
    mirror_match_limit INT DEFAULT 1, -- Free: 1, Premium: illimité
    
    -- Limites Phoenix Rise
    coaching_sessions_used INT DEFAULT 0,
    coaching_sessions_limit INT DEFAULT 1, -- Free: 1, Premium: illimité
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contrainte période unique par user
    UNIQUE(user_id, period_start, period_end)
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_usage_limits_user_period ON user_usage_limits(user_id, period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_usage_limits_active ON user_usage_limits(user_id, period_end);

-- =====================================================
-- TABLE HISTORIQUE PAIEMENTS
-- =====================================================

CREATE TABLE IF NOT EXISTS payment_history (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES user_subscriptions(subscription_id),
    
    -- Détails paiement
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_invoice_id VARCHAR(255),
    
    -- Montants
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Status et dates
    payment_status VARCHAR(50) NOT NULL, -- 'succeeded', 'failed', 'pending', 'cancelled'
    payment_date TIMESTAMPTZ DEFAULT NOW(),
    
    -- Description
    description TEXT,
    
    -- Métadonnées Stripe
    stripe_metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CHECK(payment_status IN ('succeeded', 'failed', 'pending', 'cancelled', 'refunded'))
);

-- Index pour requêtes Stripe et analytics
CREATE INDEX IF NOT EXISTS idx_payment_history_user ON payment_history(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_stripe_intent ON payment_history(stripe_payment_intent_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_status ON payment_history(payment_status);
CREATE INDEX IF NOT EXISTS idx_payment_history_date ON payment_history(payment_date);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Activer RLS sur toutes les tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_usage_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_history ENABLE ROW LEVEL SECURITY;

-- Politiques pour profiles
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Politiques pour subscriptions
CREATE POLICY "Users can view own subscriptions" ON user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- Politiques pour usage limits
CREATE POLICY "Users can view own usage limits" ON user_usage_limits
    FOR SELECT USING (auth.uid() = user_id);

-- Politiques pour payment history
CREATE POLICY "Users can view own payment history" ON payment_history
    FOR SELECT USING (auth.uid() = user_id);

-- Politiques pour services (avec service_role)
CREATE POLICY "Services can manage all data" ON profiles
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Services can manage subscriptions" ON user_subscriptions
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Services can manage usage limits" ON user_usage_limits
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Services can manage payments" ON payment_history
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- FUNCTIONS UTILITAIRES
-- =====================================================

-- Function pour récupérer le tier d'une app pour un user
CREATE OR REPLACE FUNCTION get_user_app_tier(p_user_id UUID, p_app_name VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    user_tier VARCHAR;
BEGIN
    SELECT subscription_tier 
    INTO user_tier
    FROM user_subscriptions 
    WHERE user_id = p_user_id 
    AND app_name = p_app_name 
    AND subscription_status = 'active'
    AND (current_period_end IS NULL OR current_period_end > NOW());
    
    -- Si pas d'abonnement spécifique, retourner 'free'
    RETURN COALESCE(user_tier, 'free');
END;
$$ LANGUAGE plpgsql;

-- Function pour vérifier les limites d'usage
CREATE OR REPLACE FUNCTION check_usage_limit(
    p_user_id UUID, 
    p_feature VARCHAR, 
    p_increment INT DEFAULT 1
)
RETURNS JSONB AS $$
DECLARE
    current_usage INT;
    usage_limit INT;
    period_start TIMESTAMPTZ;
    period_end TIMESTAMPTZ;
    can_use BOOLEAN;
    result JSONB;
BEGIN
    -- Calculer période courante (mois en cours)
    period_start := DATE_TRUNC('month', NOW());
    period_end := period_start + INTERVAL '1 month';
    
    -- Récupérer ou créer les limites pour cette période
    INSERT INTO user_usage_limits (user_id, period_start, period_end)
    VALUES (p_user_id, period_start, period_end)
    ON CONFLICT (user_id, period_start, period_end) DO NOTHING;
    
    -- Récupérer usage actuel et limite
    EXECUTE format('SELECT %I_used, %I_limit FROM user_usage_limits WHERE user_id = $1 AND period_start = $2',
                   p_feature, p_feature)
    INTO current_usage, usage_limit
    USING p_user_id, period_start;
    
    -- Vérifier si peut utiliser
    can_use := (current_usage + p_increment <= usage_limit) OR (usage_limit = -1); -- -1 = illimité
    
    -- Si peut utiliser, incrémenter
    IF can_use AND p_increment > 0 THEN
        EXECUTE format('UPDATE user_usage_limits SET %I_used = %I_used + $1, updated_at = NOW() WHERE user_id = $2 AND period_start = $3',
                       p_feature, p_feature)
        USING p_increment, p_user_id, period_start;
        current_usage := current_usage + p_increment;
    END IF;
    
    -- Construire résultat
    result := jsonb_build_object(
        'can_use', can_use,
        'current_usage', current_usage,
        'usage_limit', usage_limit,
        'remaining', CASE WHEN usage_limit = -1 THEN -1 ELSE usage_limit - current_usage END,
        'period_start', period_start,
        'period_end', period_end
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function pour mise à jour limites selon abonnement
CREATE OR REPLACE FUNCTION update_usage_limits_for_tier(p_user_id UUID, p_app_name VARCHAR, p_tier VARCHAR)
RETURNS VOID AS $$
DECLARE
    new_limits JSONB;
BEGIN
    -- Définir les limites selon le tier
    CASE p_tier
        WHEN 'free' THEN
            new_limits := '{
                "cv_generations_limit": 3,
                "cv_uploads_limit": 5,
                "letters_generated_limit": 2,
                "mirror_match_limit": 1,
                "coaching_sessions_limit": 1
            }'::jsonb;
        WHEN 'premium' THEN
            new_limits := '{
                "cv_generations_limit": -1,
                "cv_uploads_limit": -1,
                "letters_generated_limit": -1,
                "mirror_match_limit": -1,
                "coaching_sessions_limit": -1
            }'::jsonb;
        WHEN 'pro' THEN
            new_limits := '{
                "cv_generations_limit": -1,
                "cv_uploads_limit": -1,
                "letters_generated_limit": -1,
                "mirror_match_limit": -1,
                "coaching_sessions_limit": -1
            }'::jsonb;
    END CASE;
    
    -- Mettre à jour les limites pour la période courante
    UPDATE user_usage_limits SET
        cv_generations_limit = (new_limits->>'cv_generations_limit')::int,
        cv_uploads_limit = (new_limits->>'cv_uploads_limit')::int,
        letters_generated_limit = (new_limits->>'letters_generated_limit')::int,
        mirror_match_limit = (new_limits->>'mirror_match_limit')::int,
        coaching_sessions_limit = (new_limits->>'coaching_sessions_limit')::int,
        updated_at = NOW()
    WHERE user_id = p_user_id 
    AND period_start = DATE_TRUNC('month', NOW());
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS POUR AUTOMATISATION
-- =====================================================

-- Trigger pour créer un profil automatiquement lors de l'inscription
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    
    -- Créer abonnements gratuits par défaut
    INSERT INTO user_subscriptions (user_id, app_name, subscription_tier, subscription_status)
    VALUES 
        (NEW.id, 'cv', 'free', 'active'),
        (NEW.id, 'letters', 'free', 'active'),
        (NEW.id, 'rise', 'free', 'active');
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Créer le trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer le trigger aux tables nécessaires
CREATE TRIGGER profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

CREATE TRIGGER subscriptions_updated_at BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

CREATE TRIGGER usage_limits_updated_at BEFORE UPDATE ON user_usage_limits
    FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

-- =====================================================
-- VUES POUR FACILITER LES REQUÊTES
-- =====================================================

-- Vue pour utilisateurs avec abonnements actifs
CREATE OR REPLACE VIEW user_active_subscriptions AS
SELECT 
    p.id as user_id,
    p.email,
    p.full_name,
    p.subscription_tier as global_tier,
    us.app_name,
    us.subscription_tier as app_tier,
    us.subscription_status,
    us.current_period_end,
    CASE WHEN us.current_period_end > NOW() OR us.current_period_end IS NULL 
         THEN true 
         ELSE false 
    END as is_active
FROM profiles p
LEFT JOIN user_subscriptions us ON p.id = us.user_id
WHERE us.subscription_status = 'active';

-- Vue pour analytics abonnements
CREATE OR REPLACE VIEW subscription_analytics AS
SELECT 
    app_name,
    subscription_tier,
    subscription_status,
    COUNT(*) as user_count,
    SUM(amount_paid) as total_revenue,
    AVG(amount_paid) as avg_revenue_per_user
FROM user_subscriptions
GROUP BY app_name, subscription_tier, subscription_status;

-- =====================================================
-- DONNÉES DE TEST (OPTIONNEL)
-- =====================================================

-- Fonction pour créer des données de test
CREATE OR REPLACE FUNCTION create_test_user_data()
RETURNS VARCHAR AS $$
DECLARE
    test_user_id UUID;
BEGIN
    -- Créer un utilisateur de test (simulation)
    test_user_id := gen_random_uuid();
    
    INSERT INTO profiles (id, email, full_name, subscription_tier)
    VALUES (test_user_id, 'test@phoenix.dev', 'Test User', 'free');
    
    -- Créer abonnements de test
    INSERT INTO user_subscriptions (user_id, app_name, subscription_tier, subscription_status)
    VALUES 
        (test_user_id, 'cv', 'premium', 'active'),
        (test_user_id, 'letters', 'free', 'active');
    
    RETURN 'Test user created with ID: ' || test_user_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTAIRES DOCUMENTATION
-- =====================================================

COMMENT ON TABLE profiles IS 'Profils utilisateurs Phoenix - Extension de auth.users avec données métier';
COMMENT ON TABLE user_subscriptions IS 'Abonnements granulaires par application Phoenix avec intégration Stripe';
COMMENT ON TABLE user_usage_limits IS 'Limites d''usage par utilisateur et période avec reset mensuel automatique';
COMMENT ON TABLE payment_history IS 'Historique des paiements avec intégration Stripe complète';

COMMENT ON FUNCTION get_user_app_tier(UUID, VARCHAR) IS 'Récupère le tier d''abonnement d''un utilisateur pour une app spécifique';
COMMENT ON FUNCTION check_usage_limit(UUID, VARCHAR, INT) IS 'Vérifie et incrémente les limites d''usage avec retour JSON détaillé';
COMMENT ON FUNCTION update_usage_limits_for_tier(UUID, VARCHAR, VARCHAR) IS 'Met à jour les limites selon le tier d''abonnement';

-- =====================================================
-- VALIDATION FINALE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Phoenix Users & Auth Schema déployé avec succès!';
    RAISE NOTICE 'Tables créées: profiles, user_subscriptions, user_usage_limits, payment_history';
    RAISE NOTICE 'Functions créées: get_user_app_tier, check_usage_limit, update_usage_limits_for_tier';
    RAISE NOTICE 'Triggers créés: auto-creation profils, auto-update timestamps';
    RAISE NOTICE 'RLS activé avec politiques sécurisées';
    RAISE NOTICE 'Prêt pour intégration Phoenix Shared Auth!';
END $$;