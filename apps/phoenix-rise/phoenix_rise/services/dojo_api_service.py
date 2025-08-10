"""
Service API Dojo Mental - Clean Architecture
Centralise toute la logique réseau et les appels API pour le Dojo Mental.

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Clean Architecture Pattern
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, date
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class KaizenEntry:
    """Modèle de données pour une entrée Kaizen"""
    user_id: str
    action: str
    date: date
    completed: bool = False
    id: Optional[int] = None


@dataclass
class ZazenSession:
    """Modèle de données pour une session Zazen"""
    user_id: str
    timestamp: datetime
    duration: int
    triggered_by: Optional[str] = None
    id: Optional[int] = None


@dataclass
class DojoApiResponse:
    """Réponse standardisée de l'API Dojo"""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None


class DojoApiService:
    """
    Service API pour le Dojo Mental
    
    Encapsule toute la logique réseau et les appels API.
    Respecte les principes de Clean Architecture.
    """
    
    def __init__(self, api_base_url: Optional[str] = None):
        """
        Initialisation du service API Dojo
        
        Args:
            api_base_url: URL de base de l'API (optionnel)
        """
        self.api_base_url = api_base_url or os.environ.get(
            "NEXT_PUBLIC_DOJO_API_URL", 
            "http://127.0.0.1:8000"
        )
        logger.info(f"DojoApiService initialisé avec URL: {self.api_base_url}")
    
    async def create_kaizen_entry(self, kaizen: KaizenEntry) -> DojoApiResponse:
        """
        Crée une nouvelle entrée Kaizen
        
        Args:
            kaizen: Données de l'entrée Kaizen à créer
            
        Returns:
            DojoApiResponse: Réponse de l'API avec les données créées
        """
        try:
            # Import dynamique pour éviter les dépendances au niveau module
            import aiohttp
            import json
            
            payload = {
                "user_id": kaizen.user_id,
                "action": kaizen.action.strip(),
                "date": kaizen.date.isoformat(),
                "completed": kaizen.completed
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/kaizen",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload)
                ) as response:
                    
                    if response.status == 201:
                        data = await response.json()
                        logger.info(f"✅ Kaizen créé avec succès: {data.get('id')}")
                        return DojoApiResponse(
                            success=True,
                            data=data,
                            status_code=response.status
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erreur création Kaizen: {response.status} - {error_text}")
                        return DojoApiResponse(
                            success=False,
                            error_message=f"Erreur HTTP {response.status}: {error_text}",
                            status_code=response.status
                        )
                        
        except ImportError:
            # Fallback vers requests si aiohttp n'est pas disponible
            return await self._create_kaizen_entry_sync(kaizen)
        except Exception as e:
            logger.error(f"❌ Exception création Kaizen: {e}")
            return DojoApiResponse(
                success=False,
                error_message=f"Erreur technique: {str(e)}",
                status_code=500
            )
    
    async def _create_kaizen_entry_sync(self, kaizen: KaizenEntry) -> DojoApiResponse:
        """Fallback synchrone pour création Kaizen"""
        try:
            import requests
            import json
            
            payload = {
                "user_id": kaizen.user_id,
                "action": kaizen.action.strip(),
                "date": kaizen.date.isoformat(),
                "completed": kaizen.completed
            }
            
            response = requests.post(
                f"{self.api_base_url}/kaizen",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                logger.info(f"✅ Kaizen créé (sync): {data.get('id')}")
                return DojoApiResponse(
                    success=True,
                    data=data,
                    status_code=response.status_code
                )
            else:
                logger.error(f"❌ Erreur création Kaizen (sync): {response.status_code}")
                return DojoApiResponse(
                    success=False,
                    error_message=f"Erreur HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
        except Exception as e:
            logger.error(f"❌ Exception création Kaizen (sync): {e}")
            return DojoApiResponse(
                success=False,
                error_message=f"Erreur réseau: {str(e)}",
                status_code=500
            )
    
    async def create_zazen_session(self, session: ZazenSession) -> DojoApiResponse:
        """
        Crée une nouvelle session Zazen
        
        Args:
            session: Données de la session Zazen à créer
            
        Returns:
            DojoApiResponse: Réponse de l'API avec les données créées
        """
        try:
            # Import dynamique
            import aiohttp
            import json
            
            payload = {
                "user_id": session.user_id,
                "timestamp": session.timestamp.isoformat(),
                "duration": session.duration,
                "triggered_by": session.triggered_by or "user_request"
            }
            
            async with aiohttp.ClientSession() as client:
                async with client.post(
                    f"{self.api_base_url}/zazen-session",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload)
                ) as response:
                    
                    if response.status == 201:
                        data = await response.json()
                        logger.info(f"✅ Session Zazen créée: {data.get('id')}")
                        return DojoApiResponse(
                            success=True,
                            data=data,
                            status_code=response.status
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erreur création session Zazen: {response.status}")
                        return DojoApiResponse(
                            success=False,
                            error_message=f"Erreur HTTP {response.status}: {error_text}",
                            status_code=response.status
                        )
                        
        except ImportError:
            # Fallback synchrone
            return await self._create_zazen_session_sync(session)
        except Exception as e:
            logger.error(f"❌ Exception session Zazen: {e}")
            return DojoApiResponse(
                success=False,
                error_message=f"Erreur technique: {str(e)}",
                status_code=500
            )
    
    async def _create_zazen_session_sync(self, session: ZazenSession) -> DojoApiResponse:
        """Fallback synchrone pour session Zazen"""
        try:
            import requests
            import json
            
            payload = {
                "user_id": session.user_id,
                "timestamp": session.timestamp.isoformat(),
                "duration": session.duration,
                "triggered_by": session.triggered_by or "user_request"
            }
            
            response = requests.post(
                f"{self.api_base_url}/zazen-session",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                logger.info(f"✅ Session Zazen créée (sync): {data.get('id')}")
                return DojoApiResponse(
                    success=True,
                    data=data,
                    status_code=response.status_code
                )
            else:
                logger.error(f"❌ Erreur session Zazen (sync): {response.status_code}")
                return DojoApiResponse(
                    success=False,
                    error_message=f"Erreur HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
        except Exception as e:
            logger.error(f"❌ Exception session Zazen (sync): {e}")
            return DojoApiResponse(
                success=False,
                error_message=f"Erreur réseau: {str(e)}",
                status_code=500
            )
    
    async def get_user_kaizens(self, user_id: str) -> DojoApiResponse:
        """
        Récupère les entrées Kaizen d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            DojoApiResponse: Liste des entrées Kaizen de l'utilisateur
        """
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/kaizen/{user_id}"
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Kaizens récupérés pour {user_id}: {len(data)} entrées")
                        return DojoApiResponse(
                            success=True,
                            data=data,
                            status_code=response.status
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erreur récupération Kaizens: {response.status}")
                        return DojoApiResponse(
                            success=False,
                            error_message=f"Erreur HTTP {response.status}: {error_text}",
                            status_code=response.status
                        )
                        
        except ImportError:
            # Fallback synchrone
            return await self._get_user_kaizens_sync(user_id)
        except Exception as e:
            logger.error(f"❌ Exception récupération Kaizens: {e}")
            return DojoApiResponse(
                success=False,
                error_message=f"Erreur technique: {str(e)}",
                status_code=500
            )
    
    async def _get_user_kaizens_sync(self, user_id: str) -> DojoApiResponse:
        """Fallback synchrone pour récupération Kaizens"""
        try:
            import requests
            
            response = requests.get(
                f"{self.api_base_url}/kaizen/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Kaizens récupérés (sync) pour {user_id}: {len(data)} entrées")
                return DojoApiResponse(
                    success=True,
                    data=data,
                    status_code=response.status_code
                )
            else:
                logger.error(f"❌ Erreur récupération Kaizens (sync): {response.status_code}")
                return DojoApiResponse(
                    success=False,
                    error_message=f"Erreur HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
        except Exception as e:
            logger.error(f"❌ Exception récupération Kaizens (sync): {e}")
            return DojoApiResponse(
                success=False,
                error_message=f"Erreur réseau: {str(e)}",
                status_code=500
            )
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        Retourne le statut du service API Dojo
        
        Returns:
            Dict: Informations sur le statut du service
        """
        return {
            "service": "DojoApiService",
            "api_base_url": self.api_base_url,
            "version": "1.0.0",
            "status": "operational"
        }


# Instance globale pour utilisation facile
default_dojo_api_service = DojoApiService()