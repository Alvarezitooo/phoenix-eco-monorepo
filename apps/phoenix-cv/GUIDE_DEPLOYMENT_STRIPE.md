# 🚀 GUIDE DÉPLOIEMENT STRIPE - PHOENIX CV
## Configuration Production Complete

---

## 🎯 **SOMMAIRE**
1. [Configuration Stripe Dashboard](#1-configuration-stripe-dashboard)
2. [Configuration Streamlit Cloud](#2-configuration-streamlit-cloud)
3. [Configuration Phoenix Auth Service](#3-configuration-phoenix-auth-service)
4. [Tests & Validation](#4-tests--validation)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. 🔥 **CONFIGURATION STRIPE DASHBOARD**

### **Étape 1.1 - Créer le Webhook**

1. **Connecte-toi sur Stripe Dashboard**
   ```
   URL: https://dashboard.stripe.com
   ```

2. **Naviguer vers Webhooks**
   ```
   Menu gauche → Developers → Webhooks → Add endpoint
   ```

3. **Configuration du Webhook**
   ```
   Endpoint URL: https://phoenix-cv.streamlit.app/?webhook=stripe
   Description: Phoenix CV Subscription Webhooks
   ```

4. **Sélectionner les Événements**
   ```
   ✅ checkout.session.completed
   ✅ customer.subscription.created
   ✅ customer.subscription.updated
   ✅ customer.subscription.deleted
   ✅ invoice.payment_succeeded
   ✅ invoice.payment_failed
   ```

5. **Finaliser la Création**
   - Cliquer "Add endpoint"
   - **IMPORTANT**: Noter le "Signing secret" qui commence par `whsec_...`

### **Étape 1.2 - Récupérer les Clés API**

1. **Clé Secrète Stripe**
   ```
   Dashboard → Developers → API keys
   Secret key (commence par sk_live_... ou sk_test_...)
   ```

2. **Secret Webhook**
   ```
   Dashboard → Developers → Webhooks → [ton webhook] → Signing secret
   Commence par whsec_...
   ```

### **Étape 1.3 - Configuration Produits (Optionnel)**
Si tu veux créer les produits directement dans Stripe:
```
Dashboard → Products → Add product

Produit 1:
- Name: Phoenix CV Premium
- Price: 7.99 EUR (recurring monthly)
- ID: phoenix_cv_premium
```

---

## 2. ⚙️ **CONFIGURATION STREAMLIT CLOUD**

### **Étape 2.1 - Accéder aux Secrets**

1. **Aller sur Streamlit Cloud**
   ```
   URL: https://share.streamlit.io
   ```

2. **Sélectionner ton App Phoenix CV**
   ```
   Apps → Phoenix-cv → ⚙️ Settings → Secrets
   ```

### **Étape 2.2 - Ajouter les Variables d'Environnement**

Copie-colle cette configuration dans "Secrets" (remplace par tes vraies valeurs):

```toml
# === STRIPE CONFIGURATION ===
STRIPE_SECRET_KEY = "sk_live_OU_sk_test_TON_SECRET_KEY_ICI"
STRIPE_WEBHOOK_SECRET = "whsec_TON_WEBHOOK_SECRET_ICI"

# === PHOENIX AUTH INTEGRATION ===
PHOENIX_AUTH_SERVICE_URL = "https://phoenix-auth.herokuapp.com"
PHOENIX_AUTH_API_KEY = "TON_API_KEY_PHOENIX_AUTH_ICI"

# === AI CONFIGURATION ===
GEMINI_API_KEY = "TON_GEMINI_API_KEY_ICI"

# === APP CONFIGURATION ===
BASE_URL = "https://phoenix-cv.streamlit.app"
DEBUG_MODE = "false"
LOG_LEVEL = "INFO"

# === SECURITY ===
ENCRYPTION_KEY = "une_cle_de_32_caracteres_exactement"
```

### **Étape 2.3 - Redémarrer l'Application**

1. **Sauvegarder les Secrets**
   - Cliquer "Save"

2. **Redémarrer l'App**
   ```
   Settings → Reboot app
   ```

3. **Vérifier le Démarrage**
   - Aller sur ton app et vérifier qu'elle charge sans erreur
   - Tester la page tarification

---

## 3. 🔗 **CONFIGURATION PHOENIX AUTH SERVICE**

### **Étape 3.1 - Endpoints API Requis**

Ton service Phoenix Auth doit avoir ces endpoints. Si ils n'existent pas, voici le code à ajouter:

#### **A. Endpoint Mise à Jour Subscription**
```python
# POST /api/subscription/update
@app.route('/api/subscription/update', methods=['POST'])
@require_api_key
def update_user_subscription():
    data = request.get_json()
    
    phoenix_user_id = data.get('phoenix_user_id')
    subscription_plan = data.get('subscription_plan')  # 'pro' ou 'enterprise'
    subscription_id = data.get('subscription_id')
    subscription_status = data.get('subscription_status')
    service = data.get('service')  # 'phoenix_cv'
    
    # Logique de mise à jour de l'utilisateur dans ta DB
    # Exemple avec SQLAlchemy:
    user = User.query.filter_by(phoenix_user_id=phoenix_user_id).first()
    if user:
        user.subscription_plan = subscription_plan
        user.subscription_id = subscription_id
        user.subscription_status = subscription_status
        user.subscription_service = service
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"status": "success", "user_id": phoenix_user_id})
    
    return jsonify({"status": "error", "message": "User not found"}), 404
```

#### **B. Endpoint Récupération Statut**
```python
# GET /api/user/{user_id}/subscription
@app.route('/api/user/<user_id>/subscription', methods=['GET'])
@require_api_key
def get_user_subscription(user_id):
    user = User.query.filter_by(phoenix_user_id=user_id).first()
    
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    return jsonify({
        "phoenix_user_id": user.phoenix_user_id,
        "subscription_plan": user.subscription_plan,
        "subscription_id": user.subscription_id,
        "subscription_status": user.subscription_status,
        "subscription_service": user.subscription_service
    })
```

#### **C. Endpoint Annulation**
```python
# POST /api/subscription/cancel
@app.route('/api/subscription/cancel', methods=['POST'])
@require_api_key
def cancel_user_subscription():
    data = request.get_json()
    
    phoenix_user_id = data.get('phoenix_user_id')
    subscription_id = data.get('subscription_id')
    
    user = User.query.filter_by(phoenix_user_id=phoenix_user_id).first()
    if user:
        user.subscription_status = 'cancelled'
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error", "message": "User not found"}), 404
```

#### **D. Endpoint Audit (Optionnel)**
```python
# POST /api/audit/subscription-event
@app.route('/api/audit/subscription-event', methods=['POST'])
@require_api_key
def log_subscription_event():
    data = request.get_json()
    
    # Log l'événement dans ta table d'audit
    audit_log = AuditLog(
        phoenix_user_id=data.get('phoenix_user_id'),
        service=data.get('service'),
        event_type=data.get('event_type'),
        details=json.dumps(data.get('details')),
        timestamp=datetime.utcnow()
    )
    db.session.add(audit_log)
    db.session.commit()
    
    return jsonify({"status": "success"})
```

### **Étape 3.2 - Génération API Key**

1. **Générer une API Key Sécurisée**
   ```python
   import secrets
   api_key = secrets.token_urlsafe(32)
   print(f"PHOENIX_AUTH_API_KEY={api_key}")
   ```

2. **Ajouter la Vérification API Key**
   ```python
   from functools import wraps
   
   def require_api_key(f):
       @wraps(f)
       def decorated_function(*args, **kwargs):
           api_key = request.headers.get('Authorization')
           if not api_key or not api_key.startswith('Bearer '):
               return jsonify({'error': 'API key required'}), 401
           
           token = api_key.split(' ')[1]
           if token != os.getenv('PHOENIX_AUTH_API_KEY'):
               return jsonify({'error': 'Invalid API key'}), 401
           
           return f(*args, **kwargs)
       return decorated_function
   ```

### **Étape 3.3 - Modèle Base de Données**

Si pas encore fait, ajouter ces champs à ton modèle User:

```python
class User(db.Model):
    # ... tes champs existants ...
    
    # Nouveaux champs pour Stripe
    subscription_plan = db.Column(db.String(50), default='free')
    subscription_id = db.Column(db.String(100), nullable=True)
    subscription_status = db.Column(db.String(50), default='inactive')
    subscription_service = db.Column(db.String(50), nullable=True)
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 4. 🧪 **TESTS & VALIDATION**

### **Étape 4.1 - Test Webhook Local**

1. **Installer Stripe CLI**
   ```bash
   # macOS
   brew install stripe/stripe-cli/stripe
   
   # Linux/Windows
   # Télécharger depuis https://github.com/stripe/stripe-cli/releases
   ```

2. **Tester le Webhook**
   ```bash
   # Login Stripe CLI
   stripe login
   
   # Forward vers ton app locale
   stripe listen --forward-to https://phoenix-cv.streamlit.app/?webhook=stripe
   
   # Trigger un test
   stripe trigger checkout.session.completed
   ```

### **Étape 4.2 - Test Flow Complet**

1. **Test Abonnement Pro**
   ```
   1. Aller sur https://phoenix-cv.streamlit.app
   2. Naviguer vers page tarification
   3. Cliquer "Passer Pro Sécurisé"
   4. Utiliser carte test: 4242 4242 4242 4242
   5. Vérifier redirection après paiement
   6. Vérifier dans Phoenix Auth que user est "pro"
   ```

2. **Test Webhook Reception**
   ```
   Dashboard Stripe → Webhooks → [ton endpoint] → Recent deliveries
   Vérifier que les webhooks arrivent avec status 200
   ```

### **Étape 4.3 - Cartes de Test Stripe**

```
Succès: 4242 4242 4242 4242
Échec: 4000 0000 0000 0002
3D Secure: 4000 0000 0000 3220
Expiration: N'importe quelle date future
CVC: N'importe quel 3 chiffres
```

---

## 5. 🔍 **TROUBLESHOOTING**

### **Problème: Webhook ne fonctionne pas**

**Solution:**
```bash
# Vérifier les logs Streamlit
https://share.streamlit.io → ton app → View logs

# Vérifier configuration webhook Stripe
Dashboard → Webhooks → ton endpoint → Recent deliveries
```

### **Problème: Erreur API Phoenix Auth**

**Solution:**
```python
# Tester manuellement l'endpoint
import requests

response = requests.post(
    'https://phoenix-auth.herokuapp.com/api/subscription/update',
    headers={'Authorization': 'Bearer TON_API_KEY'},
    json={
        'phoenix_user_id': 'test_user',
        'subscription_plan': 'pro',
        'subscription_id': 'sub_test',
        'subscription_status': 'active',
        'service': 'phoenix_cv'
    }
)
print(response.status_code, response.text)
```

### **Problème: Variables d'environnement**

**Solution:**
```python
# Tester dans Streamlit
import streamlit as st
st.write("STRIPE_SECRET_KEY:", bool(st.secrets.get("STRIPE_SECRET_KEY")))
st.write("WEBHOOK_SECRET:", bool(st.secrets.get("STRIPE_WEBHOOK_SECRET")))
```

---

## ✅ **CHECKLIST FINALE**

### **Stripe Dashboard**
- [ ] Webhook créé avec bonne URL
- [ ] Événements cochés (6 événements)
- [ ] Signing secret récupéré
- [ ] API keys récupérées

### **Streamlit Cloud**
- [ ] Toutes variables ajoutées dans Secrets
- [ ] App redémarrée
- [ ] Pas d'erreurs au démarrage
- [ ] Page tarification accessible

### **Phoenix Auth**
- [ ] Endpoints API créés
- [ ] API Key générée et sécurisée
- [ ] Base de données mise à jour
- [ ] Tests API réussis

### **Tests Fonctionnels**
- [ ] Flow paiement complet testé
- [ ] Webhooks reçus (status 200)
- [ ] Statut user mis à jour correctement
- [ ] Gestion erreurs validée

---

## 🚀 **GO LIVE!**

Une fois tous les points validés:
1. **Basculer en mode Live** dans Stripe (clés `sk_live_...`)
2. **Communiquer** sur les nouveaux plans premium
3. **Monitorer** les premiers paiements
4. **Célébrer** le lancement ! 🎉

---

**Support:** En cas de problème, check les logs Streamlit et Stripe Dashboard en premier !