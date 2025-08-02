# 🚀 Phoenix Letters - Guide de Déploiement Production

**Author:** Claude Phoenix DevSecOps Guardian  
**Version:** 1.0.0 - Production Ready  
**Date:** Vendredi 1er Août 2025

---

## 🎯 **CHECKLIST CRITIQUE - LANCEMENT DIMANCHE**

### ✅ **ÉTAPE 1 : Configuration Stripe (OBLIGATOIRE)**

1. **Créer compte Stripe**
   ```bash
   # Aller sur https://dashboard.stripe.com/register
   # Activer le compte avec documents requis
   ```

2. **Récupérer les clés API**
   ```bash
   # Dashboard Stripe > Développeurs > Clés API
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_SECRET_KEY=sk_live_...
   ```

3. **Créer les produits d'abonnement**
   ```bash
   # Dashboard Stripe > Produits > Créer produit
   # Plan Premium : 9.99€/mois
   # Noter les PRIX_ID pour chaque plan
   ```

4. **Configurer webhook**
   ```bash
   # Dashboard Stripe > Développeurs > Webhooks
   # URL : https://your-webhook-app.herokuapp.com/stripe/webhook
   # Événements : customer.subscription.*, checkout.session.completed, invoice.*
   ```

### ✅ **ÉTAPE 2 : Configuration Supabase (OBLIGATOIRE)**

1. **Créer projet Supabase**
   ```bash
   # Aller sur https://supabase.com/dashboard
   # Créer nouveau projet "phoenix-letters"
   ```

2. **Exécuter le schéma SQL**
   ```sql
   -- Copier/coller le contenu de infrastructure/database/schema.sql
   -- Dans Supabase > SQL Editor
   ```

3. **Récupérer les clés**
   ```bash
   # Supabase > Paramètres > API
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### ✅ **ÉTAPE 3 : Déploiement Streamlit Cloud**

1. **Préparer le repository**
   ```bash
   git add .
   git commit -m "🚀 Phoenix Letters Production Ready"
   git push origin main
   ```

2. **Déployer sur Streamlit Cloud**
   ```bash
   # Aller sur https://share.streamlit.io/
   # Connecter GitHub repo
   # Choisir branch: main
   # Main file path: app.py
   ```

3. **Configurer les secrets**
   ```toml
   # Dans Streamlit Cloud > Advanced settings > Secrets
   # Copier le contenu de .streamlit/secrets.toml
   # REMPLACER par les vraies valeurs !
   ```

### ✅ **ÉTAPE 4 : Déploiement Webhook (OBLIGATOIRE)**

1. **Créer app Heroku pour webhook**
   ```bash
   # Créer requirements.txt pour webhook
   echo "Flask==2.3.3" > webhook_requirements.txt
   echo "stripe>=5.0.0" >> webhook_requirements.txt
   echo "supabase>=1.0.0" >> webhook_requirements.txt
   
   # Créer Procfile
   echo "web: python stripe_webhook.py" > Procfile
   ```

2. **Déployer webhook**
   ```bash
   # Sur Heroku ou autre plateforme
   # Configurer les mêmes variables d'environnement
   ```

---

## 🔧 **CONFIGURATION COMPLÈTE**

### **Variables d'environnement requises**

```bash
# OBLIGATOIRES
GOOGLE_API_KEY=your_gemini_key
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_supabase_key
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_PREMIUM=price_xxx
STRIPE_PRICE_ID_PREMIUM_PLUS=price_xxx

# AUTHENTIFICATION
AUTH_ENABLED=true
JWT_SECRET_KEY=your_32_char_secret
JWT_REFRESH_SECRET=your_32_char_refresh_secret

# OPTIONNELS
FRANCETRAVAIL_CLIENT_ID=your_client_id
FRANCETRAVAIL_CLIENT_SECRET=your_client_secret
```

### **URLs de Production**
- **App principale** : https://phoenix-letters.streamlit.app/
- **Webhook Stripe** : https://phoenix-webhook.herokuapp.com/stripe/webhook
- **Health check** : https://phoenix-webhook.herokuapp.com/health

---

## 🛡️ **SÉCURITÉ PRODUCTION**

### **Checklist Sécurité**
- [ ] Clés Stripe en mode LIVE (pas TEST)
- [ ] Secrets JWT générés aléatoirement (32+ caractères)
- [ ] HTTPS forcé partout
- [ ] Validation webhook Stripe activée
- [ ] Row Level Security Supabase activée
- [ ] Logs sensibles filtrés

### **Monitoring**
```bash
# URLs à surveiller
https://phoenix-letters.streamlit.app/ (200 OK)
https://phoenix-webhook.herokuapp.com/health (200 OK)

# Métriques Stripe
- Nombre d'abonnements actifs
- Revenus mensuel récurrent (MRR)
- Taux de conversion checkout
```

---

## 🚨 **ACTIONS IMMÉDIATES VENDREDI SOIR**

### **Priorité 1 - Stripe & Paiements**
1. Créer compte Stripe business
2. Valider identité avec documents
3. Créer produit Premium (9.99€)
4. Tester paiement en mode test
5. Basculer en mode live

### **Priorité 2 - Base de données**
1. Créer projet Supabase
2. Importer schéma SQL complet
3. Tester connexion depuis l'app
4. Configurer backups automatiques

### **Priorité 3 - Déploiement**
1. Pousser code sur GitHub
2. Déployer sur Streamlit Cloud
3. Configurer tous les secrets
4. Déployer webhook Heroku
5. Tester end-to-end

---

## 🎯 **VALIDATION FINALE**

### **Tests critiques avant lancement**
```bash
# Test 1 : Inscription utilisateur
✅ Créer compte gratuit
✅ Générer lettre gratuite
✅ Voir limite atteinte

# Test 2 : Upgrade Premium
✅ Cliquer "Passer à Premium"
✅ Compléter paiement Stripe
✅ Vérifier upgrade automatique
✅ Générer lettre Premium

# Test 3 : Fonctionnalités Premium
✅ Mirror Match fonctionne
✅ ATS Analyzer actif
✅ Smart Coach répond
✅ Pas de barrières Premium

# Test 4 : Gestion abonnement
✅ Voir facturation dans profil
✅ Annuler abonnement
✅ Vérifier downgrade auto
```

---

## 📞 **SUPPORT & URGENCES**

### **Contacts d'urgence**
- **Stripe Support** : https://support.stripe.com/
- **Supabase Support** : https://supabase.com/support
- **Streamlit Support** : https://discuss.streamlit.io/

### **Procédure d'urgence**
1. **App down** : Vérifier Streamlit Cloud status
2. **Paiements KO** : Vérifier webhook Heroku
3. **BDD inaccessible** : Vérifier Supabase dashboard
4. **Rollback** : `git revert` + redéploiement

---

## 🏆 **MÉTRIQUES DE SUCCÈS**

### **Objectifs Semaine 1**
- [ ] 100+ utilisateurs inscrits
- [ ] 10+ abonnements Premium
- [ ] 1000€+ MRR
- [ ] 0 bugs critiques
- [ ] 99%+ uptime

### **KPIs à surveiller**
- Taux de conversion gratuit → Premium
- Churn rate abonnements
- Support tickets
- Performance app (temps chargement)

---

🔥 **Phoenix Letters est PRÊT pour le lancement !** 🚀

*Dernière mise à jour : Vendredi 1er Août 2025 - Claude Phoenix DevSecOps Guardian*