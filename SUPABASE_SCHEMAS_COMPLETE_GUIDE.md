# 📊 SUPABASE SCHEMAS - GUIDE COMPLET PHOENIX

## Tous les schémas SQL nécessaires pour ton écosystème Phoenix

---

## 🎯 **RÉSUMÉ EXÉCUTIF**

**6 schémas SQL disponibles** dans `infrastructure/database/` :

✅ **1 schéma ESSENTIEL** pour démarrer (Data Flywheel)  
⚠️ **3 schémas optionnels** (fonctionnalités avancées)  
❌ **2 schémas obsolètes** (ne pas utiliser)

---

## 🚀 **SCHÉMA ESSENTIEL (À EXÉCUTER EN PRIORITÉ)**

### **1. `supabase_phoenix_events_clean.sql` ⭐ PRIORITÉ #1**

**Ce qu'il fait :**
- ✅ **Table `phoenix_events`** - Event Store principal pour Data Flywheel
- ✅ **Table `phoenix_nudges_sent`** - Tracking nudges pour éviter spam
- ✅ **Vues analytics** - `phoenix_ecosystem_analytics`, `phoenix_user_journey`
- ✅ **Functions utiles** - `get_phoenix_ecosystem_stats()`, `cleanup_old_phoenix_events()`
- ✅ **RLS sécurisé** - Politiques RGPD conformes
- ✅ **Index optimisés** - Performance garantie

**Pour :** Data Flywheel CV ↔ Letters, Smart Router, Event Queue Processing

```sql
-- À exécuter dans Supabase SQL Editor
-- Fichier: infrastructure/database/supabase_phoenix_events_clean.sql
```

---

## 🔧 **SCHÉMAS OPTIONNELS (Selon tes besoins)**

### **2. `supabase_phoenix_complete.sql` 📋 OPTIONNEL**

**Ce qu'il ajoute :**
- 📄 **Tables CV** - `cv_generations`, `cv_templates`, `cv_analytics`
- ✉️ **Tables Letters** - `letter_generations`, `job_analyses`, `mirror_matches`  
- 🧘 **Tables Rise** - `journal_entries`, `coaching_sessions`, `mood_tracking`
- 👤 **Table `profiles`** - Extension des users Supabase Auth
- 💰 **Tables Stripe** - `subscriptions`, `payment_history`

**Pour :** Stockage métier complet, analytics détaillées, fonctionnalités avancées

**⚠️ Attention :** Schema très complet (50+ tables) - utiliser seulement si tu veux tout stocker dans Supabase

### **3. `supabase_dojo_schema.sql` 🧘 OPTIONNEL**

**Ce qu'il fait :**
- 🧘 **Tables Phoenix Rise** spécialisées
- 🎯 **Kaizen tracking** et objectifs
- 📊 **Émotions et bien-être**
- 🏆 **Gamification** et achievements

**Pour :** Phoenix Rise uniquement, features bien-être avancées

### **4. `supabase_schema_clean.sql` 🧽 OPTIONNEL**

**Ce qu'il fait :**
- 🔄 **Version simplifiée** du schema complet  
- 📊 **Event Store basique** (ancienne version)
- 👤 **Tables users essentielles**

**Pour :** Version minimaliste si tu ne veux pas le schema complet

---

## ❌ **SCHÉMAS OBSOLÈTES (Ne pas utiliser)**

### **5. `supabase_event_store_schema.sql` ❌ OBSOLÈTE**
- Ancienne version Event Store
- Remplacé par `supabase_phoenix_events_clean.sql`

### **6. `supabase_phoenix_events_schema.sql` ❌ OBSOLÈTE**  
- Version avec bugs syntaxe
- Remplacé par `supabase_phoenix_events_clean.sql`

---

## 🎯 **RECOMMANDATION ARCHITECTURE**

### **DÉMARRAGE MINIMAL (Recommandé) :**
```sql
-- 1. EXÉCUTER UNIQUEMENT:
-- infrastructure/database/supabase_phoenix_events_clean.sql
```
**✅ Suffisant pour :** Data Flywheel, Event Queue, Smart Router, Analytics de base

### **VERSION COMPLÈTE (Si tu veux tout) :**
```sql
-- 1. Exécuter d'abord:
-- infrastructure/database/supabase_phoenix_events_clean.sql

-- 2. Puis ajouter si besoin:
-- infrastructure/database/supabase_phoenix_complete.sql
```
**✅ Tu auras :** Tout l'écosystème Phoenix + stockage métier complet

### **SPÉCIALISÉ RISE (Si Phoenix Rise prioritaire) :**
```sql
-- 1. Events de base:
-- infrastructure/database/supabase_phoenix_events_clean.sql

-- 2. Tables Rise spécialisées:
-- infrastructure/database/supabase_dojo_schema.sql
```

---

## 📋 **ORDRE D'EXÉCUTION RECOMMANDÉ**

### **Phase 1 - Data Flywheel (MAINTENANT)**
```sql
1. supabase_phoenix_events_clean.sql
```
**Résultat :** Data Flywheel CV ↔ Letters opérationnel

### **Phase 2 - Stockage Métier (PLUS TARD)**
```sql
2. supabase_phoenix_complete.sql (optionnel)
```
**Résultat :** Stockage complet données utilisateur

### **Phase 3 - Fonctionnalités Avancées (FUTUR)**
```sql  
3. supabase_dojo_schema.sql (si Phoenix Rise)
```
**Résultat :** Features bien-être complètes

---

## 🔍 **VALIDATION POST-EXÉCUTION**

### **Après `supabase_phoenix_events_clean.sql` :**
```sql
-- Vérifier tables créées
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'phoenix_%';

-- Tester function analytics  
SELECT get_phoenix_ecosystem_stats(7);

-- Vérifier vues
SELECT * FROM phoenix_ecosystem_analytics LIMIT 5;
```

### **Test insertion événement :**
```sql
-- Insérer événement test
INSERT INTO phoenix_events (
    stream_id, event_type, app_source, payload
) VALUES (
    gen_random_uuid(),
    'test.deployment', 
    'system',
    '{"test": "schema_deployment"}'::jsonb
);

-- Vérifier
SELECT * FROM phoenix_events ORDER BY timestamp DESC LIMIT 5;
```

---

## ⚡ **VARIABLES D'ENVIRONNEMENT REQUISES**

Après exécution des schémas :

```bash
# .env pour tes apps
SUPABASE_URL=https://ton-projet.supabase.co
SUPABASE_ANON_KEY=ton_anon_key
SUPABASE_SERVICE_ROLE_KEY=ton_service_key  # Pour agents IA
```

---

## 🎖️ **RÉCAPITULATIF FINAL**

### **Pour démarrer IMMÉDIATEMENT le Data Flywheel :**
1. ✅ **Exécuter** `supabase_phoenix_events_clean.sql`
2. ✅ **Configurer** variables d'environnement  
3. ✅ **Tester** avec guide `DATA_FLYWHEEL_SETUP_GUIDE.md`

### **Pour écosystème complet (plus tard) :**
1. ✅ Ajouter `supabase_phoenix_complete.sql`
2. ✅ Optionnel : `supabase_dojo_schema.sql` pour Rise

### **Schémas à ignorer complètement :**
- ❌ `supabase_event_store_schema.sql`  
- ❌ `supabase_phoenix_events_schema.sql`

**Avec le schéma clean, ton Data Flywheel sera opérationnel en 5 minutes ! 🚀**