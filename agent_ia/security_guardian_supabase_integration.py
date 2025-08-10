"""
🛡️ SECURITY GUARDIAN - INTÉGRATION EVENT-SOURCING SUPABASE
Agent de sécurité connecté au Event Store pour audit RGPD en temps réel
Architecture: Sécurité locale + Traçabilité cloud
"""

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import Supabase
from supabase import Client, create_client

# Import de l'agent existant pour réutiliser la logique sécurité
from .security_guardian_agent import (
    SecurityGuardianAgent,
    ThreatLevel,
    ComplianceStatus,
    SecurityThreat,
)

logger = logging.getLogger(__name__)

# ========================================
# 🛡️ STRUCTURES EVENT-SOURCING SÉCURITÉ
# ========================================

class SecurityEventType(Enum):
    """Types d'événements sécurité"""
    PII_DETECTED = "PIIDetected"
    THREAT_BLOCKED = "ThreatBlocked"
    RGPD_VIOLATION = "RGPDViolation"
    SUSPICIOUS_ACTIVITY = "SuspiciousActivity"
    COMPLIANCE_CHECK = "ComplianceCheck"
    DATA_ANONYMIZED = "DataAnonymized"
    SECURITY_SCAN_COMPLETED = "SecurityScanCompleted"

@dataclass
class SecurityEvent:
    """Événement sécurité pour Event Store"""
    event_id: str
    user_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    details: Dict[str, Any]
    app_source: str
    timestamp: datetime
    remediation_taken: bool = False
    compliance_status: ComplianceStatus = ComplianceStatus.COMPLIANT

@dataclass
class SecurityAnalysisResult:
    """Résultat d'analyse sécurité"""
    is_safe: bool
    threat_level: ThreatLevel
    detected_threats: List[SecurityThreat]
    compliance_status: ComplianceStatus
    recommendations: List[str]
    anonymized_content: Optional[str] = None
    analysis_timestamp: datetime = None

# ========================================
# 🛡️ SECURITY GUARDIAN EVENT PUBLISHER
# ========================================

class SecurityGuardianSupabasePublisher:
    """
    Security Guardian qui publie les événements sécurité dans Supabase
    Combine analyse locale IA avec traçabilité Event-Sourcing
    """

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialise Security Guardian avec connexion Supabase
        
        Args:
            supabase_url: URL Supabase (env SUPABASE_URL si None)
            supabase_key: Clé Supabase (env SUPABASE_KEY si None)
        """
        # Connexion Supabase
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL et SUPABASE_KEY requis")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Agent IA local pour analyse sécurité
        self.security_agent = SecurityGuardianAgent()
        
        # Configuration patterns menaces
        self.threat_patterns = {
            "prompt_injection": [
                r"ignore\s+previous\s+instructions",
                r"you\s+are\s+now\s+a\s+different",
                r"forget\s+your\s+role",
                r"act\s+as\s+if\s+you\s+are",
            ],
            "data_extraction": [
                r"show\s+me\s+all\s+data",
                r"export\s+user\s+information",
                r"list\s+all\s+users",
                r"database\s+contents",
            ],
            "malicious_content": [
                r"<script\s*>",
                r"javascript:",
                r"vbscript:",
                r"onload\s*=",
            ]
        }
        
        logger.info("✅ SecurityGuardianSupabasePublisher initialisé")

    async def analyze_content_security(self, content: str, content_type: str, 
                                     user_id: str, app_source: str) -> SecurityAnalysisResult:
        """
        Analyse sécurité complète d'un contenu avec publication événement
        
        Args:
            content: Contenu à analyser
            content_type: Type de contenu (cv, letter, message)
            user_id: ID utilisateur
            app_source: Application source (cv, letters, rise)
            
        Returns:
            SecurityAnalysisResult: Résultat analyse + publication event
        """
        try:
            # Analyse sécurité locale avec IA
            security_result = await self._perform_local_security_analysis(content, content_type)
            
            # Publication événement sécurité dans Event Store
            await self._publish_security_event(
                user_id=user_id,
                app_source=app_source,
                analysis_result=security_result,
                content_type=content_type
            )
            
            # Log sécurité
            logger.info(f"🛡️ Analyse sécurité - User: {user_id}, Threat: {security_result.threat_level.value}")
            
            return security_result
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse sécurité: {e}")
            # Créer un résultat d'erreur sécurisé
            return SecurityAnalysisResult(
                is_safe=False,
                threat_level=ThreatLevel.HIGH,
                detected_threats=[SecurityThreat(
                    threat_type="analysis_error",
                    confidence=1.0,
                    severity=ThreatLevel.HIGH,
                    description=f"Erreur d'analyse: {str(e)}"
                )],
                compliance_status=ComplianceStatus.ATTENTION_REQUIRED,
                recommendations=["Réessayez l'analyse ou contactez le support"],
                analysis_timestamp=datetime.now()
            )

    async def _perform_local_security_analysis(self, content: str, content_type: str) -> SecurityAnalysisResult:
        """
        Analyse sécurité locale avec patterns et IA
        """
        detected_threats = []
        threat_level = ThreatLevel.NONE
        compliance_status = ComplianceStatus.COMPLIANT
        recommendations = []
        
        # 1. Détection patterns menaces
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    threat = SecurityThreat(
                        threat_type=threat_type,
                        confidence=0.9,
                        severity=ThreatLevel.HIGH,
                        description=f"Pattern malveillant détecté: {pattern}"
                    )
                    detected_threats.append(threat)
                    threat_level = ThreatLevel.HIGH
        
        # 2. Détection PII (données personnelles)
        pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+33|0)[1-9](?:[0-9]{8})\b',
            "ssn": r'\b[1-2][0-9]{2}[0-1][0-9][0-9]{2}[0-9]{3}[0-9]{2}\b'
        }
        
        for pii_type, pattern in pii_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                threat = SecurityThreat(
                    threat_type=f"pii_{pii_type}",
                    confidence=0.8,
                    severity=ThreatLevel.MEDIUM,
                    description=f"Données personnelles détectées: {pii_type}"
                )
                detected_threats.append(threat)
                if threat_level == ThreatLevel.NONE:
                    threat_level = ThreatLevel.MEDIUM
                
                recommendations.append(f"Anonymiser les données {pii_type}")
        
        # 3. Vérification longueur excessive (potentiel DoS)
        if len(content) > 50000:
            threat = SecurityThreat(
                threat_type="excessive_length",
                confidence=0.7,
                severity=ThreatLevel.LOW,
                description="Contenu très volumineux détecté"
            )
            detected_threats.append(threat)
            recommendations.append("Limiter la taille du contenu")
        
        # 4. Déterminer statut conformité RGPD
        pii_threats = [t for t in detected_threats if t.threat_type.startswith('pii_')]
        if pii_threats:
            compliance_status = ComplianceStatus.ATTENTION_REQUIRED
            recommendations.append("Vérifier le consentement pour traitement données personnelles")
        
        # 5. Anonymisation si nécessaire
        anonymized_content = None
        if pii_threats:
            anonymized_content = await self._anonymize_content(content)
        
        # Déterminer sécurité globale
        is_safe = threat_level in [ThreatLevel.NONE, ThreatLevel.LOW]
        
        return SecurityAnalysisResult(
            is_safe=is_safe,
            threat_level=threat_level,
            detected_threats=detected_threats,
            compliance_status=compliance_status,
            recommendations=recommendations,
            anonymized_content=anonymized_content,
            analysis_timestamp=datetime.now()
        )

    async def _anonymize_content(self, content: str) -> str:
        """
        Anonymise le contenu en masquant les PII
        """
        anonymized = content
        
        # Masquer emails
        anonymized = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL_MASQUÉ]',
            anonymized
        )
        
        # Masquer téléphones
        anonymized = re.sub(
            r'\b(?:\+33|0)[1-9](?:[0-9]{8})\b',
            '[TÉLÉPHONE_MASQUÉ]',
            anonymized
        )
        
        # Masquer numéros sécu
        anonymized = re.sub(
            r'\b[1-2][0-9]{2}[0-1][0-9][0-9]{2}[0-9]{3}[0-9]{2}\b',
            '[N°SÉCU_MASQUÉ]',
            anonymized
        )
        
        return anonymized

    async def _publish_security_event(self, user_id: str, app_source: str, 
                                    analysis_result: SecurityAnalysisResult, 
                                    content_type: str) -> bool:
        """
        Publie un événement sécurité dans Supabase Event Store
        """
        try:
            # Déterminer type d'événement
            if analysis_result.threat_level == ThreatLevel.HIGH:
                event_type = SecurityEventType.THREAT_BLOCKED
            elif analysis_result.compliance_status == ComplianceStatus.NON_COMPLIANT:
                event_type = SecurityEventType.RGPD_VIOLATION
            elif any(t.threat_type.startswith('pii_') for t in analysis_result.detected_threats):
                event_type = SecurityEventType.PII_DETECTED
            else:
                event_type = SecurityEventType.SECURITY_SCAN_COMPLETED
            
            # Préparer payload événement
            event_payload = {
                "content_type": content_type,
                "threat_level": analysis_result.threat_level.value,
                "compliance_status": analysis_result.compliance_status.value,
                "threats_detected": len(analysis_result.detected_threats),
                "threat_details": [asdict(threat) for threat in analysis_result.detected_threats],
                "recommendations": analysis_result.recommendations,
                "is_safe": analysis_result.is_safe,
                "has_anonymized_content": analysis_result.anonymized_content is not None
            }
            
            # Insérer dans Event Store
            event_data = {
                "stream_id": user_id,
                "event_type": event_type.value,
                "payload": event_payload,
                "app_source": app_source,
                "metadata": {
                    "security_agent_version": "guardian_v2",
                    "analysis_timestamp": analysis_result.analysis_timestamp.isoformat()
                }
            }
            
            response = self.supabase.table('events').insert(event_data).execute()
            
            logger.info(f"🛡️ Événement sécurité publié: {event_type.value} pour user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur publication événement sécurité: {e}")
            return False

    async def get_user_security_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Récupère l'historique sécurité d'un utilisateur
        
        Args:
            user_id: ID utilisateur
            days: Nombre de jours à récupérer
            
        Returns:
            List[Dict]: Historique des événements sécurité
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            response = self.supabase.table('events')\
                .select('*')\
                .eq('stream_id', user_id)\
                .in_('event_type', [e.value for e in SecurityEventType])\
                .gte('timestamp', cutoff_date.isoformat())\
                .order('timestamp', desc=True)\
                .execute()
            
            security_events = response.data
            
            logger.info(f"📊 Récupéré {len(security_events)} événements sécurité pour user {user_id}")
            return security_events
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération historique sécurité: {e}")
            return []

    async def get_security_dashboard(self) -> Dict[str, Any]:
        """
        Génère un dashboard sécurité global de l'écosystème
        
        Returns:
            Dict: Métriques sécurité globales
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            
            # Récupérer tous les événements sécurité récents
            response = self.supabase.table('events')\
                .select('event_type, payload, app_source, timestamp')\
                .in_('event_type', [e.value for e in SecurityEventType])\
                .gte('timestamp', cutoff_date.isoformat())\
                .execute()
            
            events = response.data
            
            # Calculs métriques
            total_scans = len(events)
            threats_blocked = len([e for e in events if e['event_type'] == SecurityEventType.THREAT_BLOCKED.value])
            pii_detected = len([e for e in events if e['event_type'] == SecurityEventType.PII_DETECTED.value])
            rgpd_violations = len([e for e in events if e['event_type'] == SecurityEventType.RGPD_VIOLATION.value])
            
            # Répartition par app
            app_distribution = {}
            for event in events:
                app = event['app_source']
                app_distribution[app] = app_distribution.get(app, 0) + 1
            
            # Score sécurité global
            security_score = max(0, 100 - (threats_blocked * 10) - (rgpd_violations * 20))
            
            dashboard = {
                "period": "7_days",
                "total_security_scans": total_scans,
                "threats_blocked": threats_blocked,
                "pii_detected": pii_detected,
                "rgpd_violations": rgpd_violations,
                "security_score": security_score,
                "app_distribution": app_distribution,
                "last_updated": datetime.now().isoformat()
            }
            
            logger.info(f"🛡️ Dashboard sécurité: Score {security_score}/100, {threats_blocked} menaces bloquées")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Erreur génération dashboard sécurité: {e}")
            return {}

# ========================================
# 🚀 INTERFACE API SECURITY
# ========================================

class SecurityGuardianAPI:
    """
    API REST pour Security Guardian avec Event-Sourcing
    """
    
    def __init__(self):
        self.guardian = SecurityGuardianSupabasePublisher()
    
    async def scan_content(self, content: str, content_type: str, 
                          user_id: str, app_source: str) -> Dict[str, Any]:
        """Endpoint: Scan sécurité contenu"""
        result = await self.guardian.analyze_content_security(
            content, content_type, user_id, app_source
        )
        return asdict(result)
    
    async def get_user_security_status(self, user_id: str) -> Dict[str, Any]:
        """Endpoint: Statut sécurité utilisateur"""
        history = await self.guardian.get_user_security_history(user_id)
        
        # Résumé statut
        recent_threats = [h for h in history if h['payload'].get('threat_level') in ['high', 'critical']]
        
        return {
            "user_id": user_id,
            "security_level": "high" if not recent_threats else "attention",
            "recent_scans": len(history),
            "threats_detected": len(recent_threats),
            "last_scan": history[0]['timestamp'] if history else None
        }
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Endpoint: Dashboard sécurité global"""
        return await self.guardian.get_security_dashboard()

# ========================================
# 🧪 TESTS & EXEMPLES
# ========================================

async def test_security_integration():
    """Test de l'intégration Security Guardian Event-Sourcing"""
    try:
        guardian = SecurityGuardianSupabasePublisher()
        
        # Test contenu sécurisé
        safe_content = "Je souhaite créer un CV pour ma reconversion professionnelle"
        result = await guardian.analyze_content_security(
            content=safe_content,
            content_type="cv",
            user_id="test-user-security",
            app_source="cv"
        )
        print(f"✅ Contenu sécurisé: {result.is_safe}, Niveau: {result.threat_level.value}")
        
        # Test contenu avec PII
        pii_content = "Mon email est test@example.com et mon téléphone 0123456789"
        result = await guardian.analyze_content_security(
            content=pii_content,
            content_type="letter",
            user_id="test-user-security",
            app_source="letters"
        )
        print(f"🔍 PII détecté: {len(result.detected_threats)} menaces")
        print(f"📝 Contenu anonymisé: {result.anonymized_content}")
        
        # Dashboard sécurité
        dashboard = await guardian.get_security_dashboard()
        print(f"🛡️ Dashboard: Score {dashboard.get('security_score', 0)}/100")
        
        return True
        
    except Exception as e:
        print(f"❌ Test sécurité échoué: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration sécurité
    asyncio.run(test_security_integration())