#!/usr/bin/env python3
"""
🔗 Phoenix Agents Client - Pour apps déployées
Code à intégrer dans vos apps Railway/Streamlit Cloud
"""

import httpx
import asyncio
import os
import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class PhoenixAgentsClient:
    """
    🧠 Client pour agents IA Phoenix depuis apps déployées
    Utilise le tunnel cloudflared pour accéder aux agents locaux
    """
    
    def __init__(self, 
                 agents_url: Optional[str] = None,
                 fallback_enabled: bool = True,
                 timeout: int = 30):
        """
        Initialisation client agents IA
        
        Args:
            agents_url: URL du tunnel agents (ex: https://xxx.trycloudflare.com)
            fallback_enabled: Utiliser fallback si agents indisponibles
            timeout: Timeout requêtes (secondes)
        """
        self.agents_url = agents_url or os.getenv("AGENTS_API_URL")
        self.fallback_enabled = fallback_enabled
        self.timeout = timeout
        self.agents_available = False
        
        if not self.agents_url:
            logger.warning("⚠️ AGENTS_API_URL non configurée - agents IA désactivés")
    
    async def check_agents_health(self) -> bool:
        """Vérification santé agents IA"""
        if not self.agents_url:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.agents_url}/health",
                    timeout=5.0
                )
                self.agents_available = response.status_code == 200
                return self.agents_available
        except Exception as e:
            logger.warning(f"⚠️ Agents IA indisponibles: {e}")
            self.agents_available = False
            return False
    
    async def analyze_security(self, 
                             content: str, 
                             content_type: str = "cv") -> Dict[str, Any]:
        """
        Analyse sécurité RGPD avec agents IA
        
        Args:
            content: Contenu à analyser
            content_type: Type de contenu (cv, letter, etc.)
            
        Returns:
            Dict avec résultat analyse ou fallback
        """
        if not await self.check_agents_health():
            if self.fallback_enabled:
                return await self._security_fallback(content, content_type)
            else:
                return {"error": "Agents IA indisponibles", "fallback": False}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.agents_url}/security/analyze",
                    json={
                        "content": content,
                        "content_type": content_type
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    result["source"] = "local_agents"
                    return result
                else:
                    logger.warning(f"⚠️ Erreur agents sécurité: {response.status_code}")
                    if self.fallback_enabled:
                        return await self._security_fallback(content, content_type)
                    
        except Exception as e:
            logger.error(f"❌ Erreur requête agents sécurité: {e}")
            if self.fallback_enabled:
                return await self._security_fallback(content, content_type)
        
        return {"error": "Analyse sécurité échouée", "fallback": False}
    
    async def generate_insights(self, 
                              data: Dict[str, Any],
                              task: str = "general") -> Dict[str, Any]:
        """
        Génération insights avec agents IA
        
        Args:
            data: Données à analyser
            task: Type de tâche (cv_optimization, coaching, etc.)
            
        Returns:
            Dict avec insights ou fallback
        """
        if not await self.check_agents_health():
            if self.fallback_enabled:
                return await self._insights_fallback(data, task)
            else:
                return {"error": "Agents IA indisponibles", "fallback": False}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.agents_url}/data/insights",
                    json={
                        "data": data,
                        "task": task
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    result["source"] = "local_agents"
                    return result
                else:
                    logger.warning(f"⚠️ Erreur agents insights: {response.status_code}")
                    if self.fallback_enabled:
                        return await self._insights_fallback(data, task)
                    
        except Exception as e:
            logger.error(f"❌ Erreur requête agents insights: {e}")
            if self.fallback_enabled:
                return await self._insights_fallback(data, task)
        
        return {"error": "Génération insights échouée", "fallback": False}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Status système agents IA"""
        if not self.agents_url:
            return {"status": "disabled", "reason": "AGENTS_API_URL non configurée"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.agents_url}/system/status",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": "error", "code": response.status_code}
                    
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}
    
    async def _security_fallback(self, content: str, content_type: str) -> Dict[str, Any]:
        """Fallback analyse sécurité (règles basiques)"""
        logger.info("🔄 Utilisation fallback analyse sécurité")
        
        # Détection PII basique
        pii_detected = []
        if "@" in content:
            pii_detected.append({"type": "email", "risk_level": "medium"})
        
        # Simulation analyse RGPD basique
        return {
            "compliance_status": "attention_required",
            "pii_detected": pii_detected,
            "rgpd_violations": [],
            "anonymization_required": len(pii_detected) > 0,
            "recommendations": ["Utiliser agents IA locaux pour analyse complète"],
            "source": "fallback",
            "risk_assessment": "medium"
        }
    
    async def _insights_fallback(self, data: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Fallback génération insights (réponse générique)"""
        logger.info("🔄 Utilisation fallback génération insights")
        
        return {
            "insights": ["Connectez les agents IA locaux pour des insights personnalisés"],
            "recommendations": ["Démarrer le tunnel agents IA"],
            "confidence": 0.3,
            "source": "fallback",
            "task": task
        }

# =======================================
# 🔗 FONCTIONS UTILITAIRES STREAMLIT
# =======================================

def init_agents_client() -> PhoenixAgentsClient:
    """Initialisation client agents pour Streamlit"""
    return PhoenixAgentsClient(
        agents_url=os.getenv("AGENTS_API_URL"),
        fallback_enabled=True,
        timeout=30
    )

async def check_agents_status() -> Dict[str, Any]:
    """Vérification rapide status agents pour UI"""
    client = init_agents_client()
    return await client.get_system_status()

# =======================================
# 📋 EXEMPLE D'UTILISATION DANS VOS APPS
# =======================================

"""
EXEMPLE DANS UNE APP STREAMLIT:

import streamlit as st
from agents_client_for_apps import init_agents_client, check_agents_status

# Initialisation
if 'agents_client' not in st.session_state:
    st.session_state.agents_client = init_agents_client()

# Utilisation
async def analyze_cv_security(cv_content):
    client = st.session_state.agents_client
    result = await client.analyze_security(cv_content, "cv")
    return result

# Status agents dans sidebar
with st.sidebar:
    if st.button("🔍 Check Agents Status"):
        status = asyncio.run(check_agents_status())
        st.json(status)

CONFIGURATION REQUISE DANS VOS APPS RAILWAY/STREAMLIT:
- Variable d'environnement: AGENTS_API_URL=https://votre-tunnel.trycloudflare.com
- Import: from agents_client_for_apps import init_agents_client
"""