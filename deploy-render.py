#!/usr/bin/env python3
"""
🚀 PHOENIX ECOSYSTEM - Script de déploiement Render
Déploie tous les services via l'API REST de Render
"""

import requests
import json
import os
import sys
import time
from typing import Dict, List, Optional

class RenderDeployment:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def get_user_info(self) -> Dict:
        """Récupère les informations utilisateur"""
        response = requests.get(f"{self.base_url}/users/me", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erreur authentification: {response.status_code} - {response.text}")
    
    def list_services(self) -> List[Dict]:
        """Liste tous les services existants"""
        response = requests.get(f"{self.base_url}/services", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return []
    
    def create_service(self, service_config: Dict) -> Dict:
        """Crée un service sur Render"""
        print(f"🚀 Création du service: {service_config['name']}")
        
        response = requests.post(
            f"{self.base_url}/services",
            headers=self.headers,
            json=service_config
        )
        
        if response.status_code == 201:
            service = response.json()
            print(f"✅ Service créé: {service['name']} (ID: {service['id']})")
            return service
        else:
            print(f"❌ Erreur création {service_config['name']}: {response.status_code}")
            print(f"   Détails: {response.text}")
            return {}
    
    def get_github_repo_info(self) -> Dict:
        """Configure le repo GitHub pour le déploiement"""
        return {
            "type": "github",
            "repo": "https://github.com/mattvaness/phoenix-eco-monorepo",  # Remplacez par votre repo
            "branch": "main"
        }

def create_phoenix_services() -> List[Dict]:
    """Génère la configuration des services Phoenix"""
    
    # Configuration de base du repo
    repo_config = {
        "type": "github",
        "repo": "https://github.com/mattvaness/phoenix-eco-monorepo",  # À adapter
        "branch": "main"
    }
    
    services = []
    
    # 1. Phoenix Letters - Streamlit App
    services.append({
        "name": "phoenix-letters",
        "type": "web_service",
        "repo": repo_config,
        "env": "docker",
        "dockerfilePath": "./Dockerfile",
        "dockerBuildArgs": ["APP_NAME=phoenix-letters"],
        "region": "oregon",
        "plan": "starter",
        "healthCheckPath": "/_stcore/health",
        "envVars": [
            {"key": "GOOGLE_API_KEY", "value": ""},
            {"key": "SUPABASE_URL", "value": ""},
            {"key": "SUPABASE_ANON_KEY", "value": ""},
            {"key": "STRIPE_SECRET_KEY", "value": ""},
            {"key": "JWT_SECRET_KEY", "value": ""}
        ]
    })
    
    # 2. Phoenix CV - Streamlit App
    services.append({
        "name": "phoenix-cv",
        "type": "web_service",
        "repo": repo_config,
        "env": "docker",
        "dockerfilePath": "./Dockerfile",
        "dockerBuildArgs": ["APP_NAME=phoenix-cv"],
        "region": "oregon", 
        "plan": "starter",
        "healthCheckPath": "/_stcore/health",
        "envVars": [
            {"key": "GOOGLE_API_KEY", "value": ""},
            {"key": "SUPABASE_URL", "value": ""},
            {"key": "SUPABASE_ANON_KEY", "value": ""}
        ]
    })
    
    # 3. Phoenix Backend Unified - FastAPI
    services.append({
        "name": "phoenix-backend-unified",
        "type": "web_service",
        "repo": repo_config,
        "env": "docker",
        "dockerfilePath": "./Dockerfile",
        "dockerBuildArgs": ["APP_NAME=phoenix-backend-unified"],
        "region": "oregon",
        "plan": "starter", 
        "healthCheckPath": "/health",
        "envVars": [
            {"key": "SUPABASE_URL", "value": ""},
            {"key": "SUPABASE_SERVICE_ROLE_KEY", "value": ""},
            {"key": "JWT_SECRET_KEY", "value": ""},
            {"key": "ALLOWED_ORIGINS", "value": "https://phoenix-aube.vercel.app,https://phoenix-rise.vercel.app"},
            {"key": "ENVIRONMENT", "value": "production"}
        ]
    })
    
    return services

def main():
    """Script principal de déploiement"""
    print("🏛️ PHOENIX ECOSYSTEM - Déploiement Render")
    print("=" * 50)
    
    # Récupération de la clé API
    api_key = os.environ.get("RENDER_API_KEY")
    if not api_key:
        print("❌ RENDER_API_KEY manquante dans les variables d'environnement")
        print("💡 Obtenez votre clé API sur: https://dashboard.render.com/account")
        sys.exit(1)
    
    try:
        # Initialisation du client
        deployer = RenderDeployment(api_key)
        
        # Vérification authentification
        user_info = deployer.get_user_info()
        print(f"✅ Connecté en tant que: {user_info.get('email', 'N/A')}")
        
        # Liste des services existants
        existing_services = deployer.list_services()
        existing_names = [s.get('name') for s in existing_services]
        print(f"📋 Services existants: {len(existing_services)}")
        
        # Configuration des services Phoenix
        phoenix_services = create_phoenix_services()
        
        # Déploiement
        deployed_services = []
        for service_config in phoenix_services:
            if service_config['name'] in existing_names:
                print(f"⚠️ Service {service_config['name']} existe déjà, ignoré")
            else:
                deployed = deployer.create_service(service_config)
                if deployed:
                    deployed_services.append(deployed)
                time.sleep(2)  # Éviter le rate limiting
        
        # Résumé
        print("\n" + "=" * 50)
        print(f"🎉 Déploiement terminé: {len(deployed_services)} services créés")
        
        for service in deployed_services:
            print(f"   • {service.get('name')}: {service.get('serviceDetails', {}).get('url', 'En cours...')}")
        
        print("\n💡 Configurez vos variables d'environnement sur:")
        print("   https://dashboard.render.com")
        
    except Exception as e:
        print(f"❌ Erreur déploiement: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()