# 🤖 Alessio Client - Agent IA Phoenix Ecosystem

Le client officiel pour intégrer l'agent Alessio dans toutes les applications de l'écosystème Phoenix.

## 🌟 Vue d'ensemble

Alessio est l'intelligence artificielle conversationnelle qui accompagne les utilisateurs dans leur transformation professionnelle à travers tout l'écosystème Phoenix. Ce package fournit des interfaces unifiées pour Streamlit et React/Next.js.

### 🎯 Spécialisations d'Alessio par Application

| Application | Spécialisation | Icon | Contexte |
|-------------|----------------|------|----------|
| **Phoenix Letters** | Lettres de motivation & reconversions | ✍️ | Génération de lettres personnalisées, optimisation ATS |
| **Phoenix CV** | Optimisation CV & carrière | 📋 | Analyse CV, templates, trajectoire professionnelle |
| **Phoenix Rise** | Développement personnel | 🌱 | Coaching émotionnel, objectifs, gestion stress |
| **Phoenix Website** | Guide écosystème | 🚀 | Navigation, recommandations, support |

## 📦 Installation

```bash
# Dans le monorepo Phoenix
cd packages/alessio-client
poetry install

# Ou via pip (une fois publié)
pip install phoenix-alessio-client
```

## 🚀 Démarrage rapide

### Pour Streamlit (Phoenix Letters, CV, Rise)

```python
from alessio_client import AlessioStreamlitClient, AlessioAppContext, render_alessio_chat

# Configuration
client = AlessioStreamlitClient(
    app_context=AlessioAppContext.LETTERS,  # ou CV, RISE
    api_url="http://localhost:8003/api/v1/chat"
)

# Interface simple
render_alessio_chat(AlessioAppContext.LETTERS)

# Interface avancée avec contexte
client.render_chat_interface(additional_context={
    "current_page": "letter_generation",
    "has_cv_data": True,
    "user_context": {"stage": "experienced"}
})
```

### Pour React/Next.js (Phoenix Website)

```tsx
import { AlessioChat, useAlessio } from '@/components/alessio';

function MyComponent() {
  const alessioConfig = {
    apiUrl: 'http://localhost:8003/api/v1/chat',
    appContext: 'phoenix-website',
    timeout: 60000
  };

  return (
    <AlessioChat 
      config={alessioConfig}
      authToken={authToken}
      className="max-w-2xl mx-auto"
    />
  );
}
```

## 🏗️ Architecture

```
alessio-client/
├── alessio_client/
│   ├── __init__.py              # Exports principaux
│   ├── base_client.py           # Client de base partagé
│   ├── streamlit_client.py      # Interface Streamlit
│   ├── react_client.py          # Générateur composants React
│   ├── config.py                # Configuration écosystème
│   └── navigation.py            # Navigation inter-apps
├── README.md                    # Ce fichier
└── pyproject.toml              # Configuration package
```

## 🎨 Interfaces disponibles

### 1. Client Streamlit

#### Interface de chat de base
```python
from alessio_client import render_alessio_chat, AlessioAppContext

render_alessio_chat(AlessioAppContext.CV, additional_context={
    "cv_data": user_cv,
    "template_type": "modern"
})
```

#### Client avancé avec gestion d'état
```python
from alessio_client import AlessioStreamlitClient

client = AlessioStreamlitClient(AlessioAppContext.RISE)

# Chat avec contexte coaching
client.render_personal_coaching_chat(
    journal_entries=recent_entries,
    mood_data=current_mood
)

# Statut dans la sidebar
client.render_sidebar_status()
```

### 2. Composants React

#### Hook personnalisé
```tsx
import { useAlessio } from './alessio/useAlessio';

const { messages, isLoading, sendMessage } = useAlessio(config);

const handleSend = async () => {
  await sendMessage("Comment optimiser mon CV ?", authToken);
};
```

#### Composant complet
```tsx
import { AlessioChat } from '@/components/alessio';

<AlessioChat 
  config={alessioConfig}
  authToken={userToken}
  className="w-full max-w-4xl"
/>
```

#### Widget flottant
```tsx
import { AlessioWidget } from '@/components/alessio';

<AlessioWidget authToken={authToken} />
```

## 🌐 Configuration inter-applications

### Variables d'environnement

```bash
# Environnement
PHOENIX_ENV=development  # development, staging, production

# API Iris
IRIS_API_URL=http://localhost:8003/api/v1/chat
IRIS_HEALTH_URL=http://localhost:8003/health

# Applications (auto-configurées selon l'environnement)
PHOENIX_LETTERS_URL=http://localhost:8501
PHOENIX_CV_URL=http://localhost:8502
PHOENIX_RISE_URL=http://localhost:8503
PHOENIX_WEBSITE_URL=http://localhost:3000
```

### Navigation inter-apps

```python
from alessio_client.navigation import render_phoenix_navigation

# Dans la sidebar Streamlit
render_phoenix_navigation(
    current_app="phoenix-letters",
    show_iris_links=True
)

# Boutons de bascule entre assistants
render_cross_app_alessio_buttons("phoenix-cv")
```

## 🔧 Intégration par application

### Phoenix Letters
```python
# apps/phoenix-letters/ui/components/alessio_ui.py
from alessio_client import AlessioStreamlitClient, AlessioAppContext

client = AlessioStreamlitClient(AlessioAppContext.LETTERS)
client.render_chat_interface({
    "current_page": "letter_generation",
    "job_offer": job_data,
    "user_cv": cv_data
})
```

### Phoenix CV  
```python
# apps/phoenix-cv/phoenix_cv/ui/alessio_integration.py
from alessio_client import render_alessio_chat, AlessioAppContext

render_alessio_chat(
    AlessioAppContext.CV,
    additional_context={
        "cv_data": current_cv,
        "optimization_type": "ats_keywords"
    }
)
```

### Phoenix Rise
```python
# apps/phoenix-rise/phoenix_rise/ui/alessio_integration.py
client = AlessioStreamlitClient(AlessioAppContext.RISE)
client.render_personal_coaching_chat(
    journal_entries=recent_entries,
    mood_data={"current_mood": "stressed", "energy_level": 6}
)
```

### Phoenix Website
```tsx
// apps/phoenix-website/components/alessio/
import { AlessioSection } from '@/components/alessio';

<AlessioSection 
  title="Rencontrez Alessio"
  authToken={session?.accessToken}
  showFeatures={true}
/>
```

## 🎯 Contextes et spécialisations

### Contextes disponibles
```python
from alessio_client import AlessioAppContext

AlessioAppContext.LETTERS   # ✍️ Lettres de motivation
AlessioAppContext.CV        # 📋 Optimisation CV
AlessioAppContext.RISE      # 🌱 Développement personnel  
AlessioAppContext.WEBSITE   # 🚀 Guide écosystème
```

### Personnalisation par contexte
```python
# Suggestions spécifiques au contexte
suggestions = client.get_app_specific_suggestions("ats")
# → ["Quels mots-clés utiliser ?", "Comment optimiser pour l'ATS ?"]

# Configuration contextuelle
additional_context = {
    "app_context": "phoenix-cv",
    "current_page": "template_selection",
    "user_data": {
        "sector": "tech",
        "experience_level": "senior"
    }
}
```

## 🚦 Gestion d'état et authentification

### Authentification Phoenix
```python
def get_user_auth_token() -> Optional[str]:
    if 'authenticated_user' not in st.session_state:
        return None
    return st.session_state.get('access_token')

# Utilisation
auth_token = get_user_auth_token()
if auth_token:
    render_alessio_chat(AlessioAppContext.LETTERS)
else:
    st.warning("Connectez-vous pour accéder à Alessio")
```

### Gestion des tiers utilisateur
```python
user_tier = st.session_state.get('user_tier', 'FREE')

if user_tier == 'FREE':
    st.info("🎆 Version FREE : 5 messages/jour")
elif user_tier == 'PREMIUM':
    st.success("🎆 Version PREMIUM : Accès illimité")
```

## 🎨 Personnalisation UI

### Styles Streamlit
```python
from alessio_client.navigation import inject_cross_app_css

# Injecter les styles cross-app
inject_cross_app_css()

# Personnalisation couleurs par contexte
context_colors = {
    AlessioAppContext.LETTERS: "#7c3aed",  # Purple
    AlessioAppContext.CV: "#2563eb",       # Blue  
    AlessioAppContext.RISE: "#16a34a",     # Green
    AlessioAppContext.WEBSITE: "#ea580c"   # Orange
}
```

### Styles React/Tailwind
```css
/* Classe utilitaires pour Alessio */
.alessio-chat { @apply bg-white rounded-lg shadow-lg; }
.alessio-message-user { @apply bg-blue-500 text-white rounded-lg px-4 py-2; }
.alessio-message-assistant { @apply bg-gray-100 text-gray-800 rounded-lg px-4 py-2; }

/* Couleurs par contexte */
.alessio-purple { @apply bg-purple-100 text-purple-700; }
.alessio-blue { @apply bg-blue-100 text-blue-700; }
.alessio-green { @apply bg-green-100 text-green-700; }
.alessio-orange { @apply bg-orange-100 text-orange-700; }
```

## 🔒 Sécurité

### Protection contre prompt injection
Le client intègre automatiquement les protections de sécurité d'Alessio :
- Détection patterns malveillants
- Sanitisation des inputs
- Rate limiting par utilisateur
- Validation des tokens JWT

### Gestion des erreurs
```python
# Codes de statut gérés automatiquement
response_status = {
    "success": "✅ Réponse générée",
    "auth_error": "🔒 Session expirée", 
    "quota_exceeded": "📊 Limite quotidienne atteinte",
    "rate_limited": "⏳ Trop de requêtes",
    "access_denied": "💫 Accès refusé",
    "service_unavailable": "😢 Service indisponible"
}
```

## 📈 Monitoring et métriques

### Métriques d'utilisation
```python
# Tracking automatique des métriques
with st.sidebar:
    st.metric("Messages aujourd'hui", f"{messages_used}/5")
    st.metric("Temps de réponse moyen", "1.2s")
    
    if user_tier == "FREE" and messages_used >= 4:
        st.warning("⚠️ Bientôt à la limite")
```

## 🛠️ Développement et contribution

### Setup environnement de développement
```bash
# Cloner le monorepo
git clone https://github.com/votre-org/phoenix-eco-monorepo.git
cd packages/alessio-client

# Installer les dépendances
poetry install

# Lancer l'agent Alessio en local
cd ../alessio-agent
python start_alessio.py

# Tester l'intégration
cd ../../apps/phoenix-letters
streamlit run app.py
```

### Tests
```bash
# Tests unitaires
pytest tests/

# Tests d'intégration avec Alessio
pytest tests/integration/

# Tests de sécurité
bandit -r alessio_client/
```

## 🗺️ Roadmap

### ✅ Version 0.1.0 (Actuelle)
- [x] Client Streamlit de base
- [x] Composants React/Next.js
- [x] Navigation inter-applications
- [x] Configuration centralisée
- [x] Intégration 4 applications Phoenix

### 🚧 Version 0.2.0 (En cours)
- [ ] Cache intelligent des conversations
- [ ] Synchronisation cross-app des sessions
- [ ] Métriques avancées d'utilisation
- [ ] Support multi-langues

### 🔮 Version 0.3.0 (Planifiée)
- [ ] Mode hors-ligne avec cache local
- [ ] Intégration vocal (speech-to-text)
- [ ] Personnalisation avancée de l'interface
- [ ] API webhooks pour notifications

## 📚 Documentation complète

- [Guide d'intégration Streamlit](docs/streamlit-integration.md)
- [Guide d'intégration React](docs/react-integration.md) 
- [Configuration avancée](docs/advanced-config.md)
- [Sécurité et bonnes pratiques](docs/security.md)
- [Contribution et développement](docs/contributing.md)

## 🤝 Support

- **Issues GitHub** : [phoenix-eco-monorepo/issues](https://github.com/votre-org/phoenix-eco-monorepo/issues)
- **Discord communauté** : [phoenix-community](https://discord.gg/phoenix)
- **Documentation** : [docs.phoenix-ecosystem.com](https://docs.phoenix-ecosystem.com)

---

**🚀 Prêt à intégrer Alessio dans votre application Phoenix ? Suivez le guide de démarrage rapide ci-dessus !**