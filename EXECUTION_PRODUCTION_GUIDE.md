# 🚀 GUIDE D'EXÉCUTION PRODUCTION PHOENIX

## ORDRE EXACT D'EXÉCUTION POUR PRODUCTION PARFAITE

---

## 🎯 **RÉSUMÉ EXÉCUTIF**

**Tu as 2 schémas OBLIGATOIRES + 1 optionnel pour une production complète.**

**Temps total : 10 minutes maximum**

---

## 📋 **ÉTAPE 1 : EVENT STORE DATA FLYWHEEL** ⭐ OBLIGATOIRE

### **Fichier à exécuter :**
```
infrastructure/database/supabase_phoenix_events_clean.sql
```

### **Ce que ça créé :**
- ✅ **Table `phoenix_events`** - Event Store principal Data Flywheel
- ✅ **Table `phoenix_nudges_sent`** - Anti-spam système
- ✅ **Vues analytics** - `phoenix_ecosystem_analytics`, `phoenix_user_journey`
- ✅ **Functions** - `get_phoenix_ecosystem_stats()`, cleanup automatique
- ✅ **RLS sécurisé** - Politiques RGPD

### **Validation post-exécution :**
```sql
-- Vérifier tables créées
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE 'phoenix_%';

-- Tester function
SELECT get_phoenix_ecosystem_stats(7);
```

---

## 👤 **ÉTAPE 2 : USERS & AUTHENTIFICATION** ⭐ OBLIGATOIRE

### **Fichier à exécuter :**
```
infrastructure/database/supabase_phoenix_users_auth.sql
```

### **Ce que ça créé :**
- ✅ **Table `profiles`** - Extension auth.users Supabase
- ✅ **Table `user_subscriptions`** - Abonnements granulaires par app
- ✅ **Table `user_usage_limits`** - Limites Free/Premium avec reset mensuel
- ✅ **Table `payment_history`** - Historique Stripe complet
- ✅ **Functions** - `get_user_app_tier()`, `check_usage_limit()`
- ✅ **Triggers** - Auto-création profils, auto-update timestamps

### **Validation post-exécution :**
```sql
-- Vérifier users
SELECT * FROM profiles LIMIT 3;
SELECT * FROM user_subscriptions LIMIT 3;

-- Tester functions
SELECT get_user_app_tier(auth.uid(), 'cv');
SELECT check_usage_limit(auth.uid(), 'cv_generations', 1);
```

---

## 📊 **ÉTAPE 3 : STOCKAGE MÉTIER COMPLET** 📋 OPTIONNEL

### **Fichier à exécuter :**
```
infrastructure/database/supabase_phoenix_complete.sql
```

### **Ce que ça ajoute :**
- 📄 **Tables CV** - Stockage générations, templates, analytics
- ✉️ **Tables Letters** - Stockage lettres, analyses job
- 🧘 **Tables Rise** - Journal, coaching, humeur
- 📊 **Analytics avancées** - Rapports détaillés par app

### **Quand l'exécuter :**
- ✅ **Maintenant** si tu veux stocker toutes les données dans Supabase
- ⏸️ **Plus tard** si Data Flywheel suffit pour commencer

---

## 🔐 **VARIABLES D'ENVIRONNEMENT REQUISES**

### **Configuration minimale :**
```bash
# .env pour toutes tes apps
SUPABASE_URL=https://ton-projet.supabase.co
SUPABASE_ANON_KEY=ton_anon_key
SUPABASE_SERVICE_ROLE_KEY=ton_service_key
```

### **Configuration Stripe (si abonnements) :**
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_PREMIUM=price_...
```

---

## 🧪 **TESTS DE VALIDATION COMPLÈTE**

### **Test 1 : Data Flywheel**
```sql
-- Insérer événement test
INSERT INTO phoenix_events (stream_id, event_type, app_source, payload)
VALUES (gen_random_uuid(), 'test.production', 'system', '{"test": "ok"}'::jsonb);

-- Vérifier
SELECT * FROM phoenix_events ORDER BY timestamp DESC LIMIT 5;
```

### **Test 2 : Gestion utilisateurs**
```sql
-- Créer utilisateur test
SELECT create_test_user_data();

-- Vérifier abonnements
SELECT * FROM user_active_subscriptions LIMIT 5;
```

### **Test 3 : Applications Phoenix**
```bash
# Test Phoenix CV
cd apps/phoenix-cv
streamlit run phoenix_cv/main.py
# → Upload CV → Vérifier events dans Supabase

# Test Phoenix Letters
cd apps/phoenix-letters  
streamlit run main.py
# → Générer lettre → Vérifier events dans Supabase
```

---

## 🎖️ **ARCHITECTURE FINALE OBTENUE**

```
🌐 PHOENIX APPS (Cloud - Streamlit/Railway)
    ↓ (Events + Auth)
📊 SUPABASE PRODUCTION
    ├── phoenix_events          ← Data Flywheel Event Store
    ├── profiles                ← Users auth.users extension
    ├── user_subscriptions      ← Free/Premium par app
    ├── user_usage_limits       ← Limites avec reset mensuel
    ├── payment_history         ← Stripe intégration
    └── [Tables métier]         ← CV/Letters/Rise (optionnel)
    ↓ (Queue processing)
🐳 AGENTS IA (Local Docker)
    ├── Smart Router            ← Traite events
    ├── Event Queue Processor   ← Batch intelligent
    └── Data Flywheel Engine    ← Insights cross-app
```

---

## ✅ **RÉSULTAT FINAL PRODUCTION**

Après exécution des 2 schémas obligatoires, tu auras :

1. **Data Flywheel opérationnel** - CV ↔ Letters avec analytics temps réel
2. **Gestion utilisateurs complète** - Free/Premium par app avec limites automatiques
3. **Intégration Stripe ready** - Abonnements et paiements
4. **Architecture hybride** - Cloud apps + Supabase + Local AI agents
5. **Sécurité RGPD** - RLS sur toutes les tables sensibles
6. **Performance optimisée** - Index et functions optimisées
7. **Monitoring intégré** - Analytics et health checks

**Temps d'exécution : 5-10 minutes maximum**
**Résultat : Production-ready à 100% ! 🚀**