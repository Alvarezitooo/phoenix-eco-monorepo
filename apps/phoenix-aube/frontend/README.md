# 🚀 Phoenix Aube Frontend

Interface React moderne pour l'exploration de carrière Phoenix Aube, basée sur les composants de haute qualité de Bolt.new.

## 🎯 **Architecture**

```
phoenix-aube/
├── frontend/ (NOUVEAU - React/TypeScript)
│   ├── src/
│   │   ├── components/     # Composants UI extraits de Bolt.new
│   │   ├── context/        # Contexte d'authentification Phoenix
│   │   ├── data/          # Questions diagnostic (Big Five + RIASEC)
│   │   ├── types/         # Types TypeScript
│   │   └── utils/         # Logique d'analyse des réponses
│   ├── vite.config.ts     # Configuration avec proxy FastAPI
│   └── package.json       # Dépendances React/Vite
└── phoenix_aube/ (EXISTANT - Backend Python)
    ├── api/main.py        # FastAPI + Event Store
    ├── services/          # IA Validator, Data Aggregation
    └── core/              # Models, Event Store, Orchestrator
```

## 🛠️ **Installation & Démarrage**

### **Option 1: Démarrage automatique (Recommandé)**
```bash
cd apps/phoenix-aube/
./start_full_stack.sh
```

### **Option 2: Démarrage manuel**

**Terminal 1 - Backend FastAPI:**
```bash
cd apps/phoenix-aube/phoenix_aube/
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend React:**
```bash
cd apps/phoenix-aube/frontend/
npm install
npm run dev
```

## 🌐 **URLs d'accès**

- **Frontend React:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentation API:** http://localhost:8000/docs

## 🎨 **Fonctionnalités UI Intégrées**

### **✅ Déjà Intégré de Bolt.new**
- ✅ **Quiz Diagnostic** : Interface moderne avec animations fluides
- ✅ **Profil d'Aspiration** : Visualisation des traits dominants
- ✅ **Logique Big Five + RIASEC** : Analyse complète de personnalité
- ✅ **Design Responsive** : Tailwind CSS optimisé
- ✅ **TypeScript complet** : Type safety et autocomplete

### **🔄 En Cours d'Intégration**
- 🔄 **Event Bridge API** : Connexion aux événements Phoenix
- 🔄 **Auth Phoenix** : Integration avec le système d'auth unifié
- 🔄 **API IA Validator** : Connexion aux services métier existants

### **📋 À Intégrer**
- ⏳ **Résultats Carrière** : API de recommandations métiers
- ⏳ **Analytics Dashboard** : Métriques utilisateur temps réel
- ⏳ **Payment Integration** : Stripe pour Premium

## 🔧 **Configuration Technique**

### **Proxy API (Vite)**
```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false
  }
}
```

### **Event Bridge Integration**
```typescript
// App.tsx
const sendEventToBridge = async (eventType: string, data: any) => {
  const response = await fetch('/api/events', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      event_type: eventType,
      data,
      user_id: user?.id
    })
  });
};
```

## 📊 **Comparaison Avant/Après**

| Aspect | Streamlit (Avant) | React (Maintenant) |
|--------|------------------|-------------------|
| **Performance** | ⚡ Moyen | ⚡⚡⚡ Excellent |
| **UX/UI** | 📱 Basique | 📱📱📱 Moderne |
| **Maintenance** | 🔧 Complexe | 🔧🔧 Structuré |
| **Déploiement** | 🚀 Streamlit Cloud | 🚀🚀🚀 CDN/Vercel |
| **Scalabilité** | 📈 Limitée | 📈📈📈 Excellent |

## 🎯 **Prochaines Étapes**

1. **Test de l'installation** avec `./start_full_stack.sh`
2. **Connexion Event Bridge** réel vers Supabase
3. **Intégration Auth Phoenix** avec JWT partagé
4. **Migration DNS** vers le nouveau frontend
5. **Décommissioning Streamlit** interface

## 🤝 **Contribution**

Pour contribuer au frontend Phoenix Aube :

1. Lancer `npm run dev` en mode développement
2. Modifier les composants dans `src/components/`
3. Tester avec le backend FastAPI connecté
4. Vérifier TypeScript avec `npm run lint`

---

**✨ L'expérience utilisateur Phoenix Aube est maintenant au niveau des meilleures applications modernes !**