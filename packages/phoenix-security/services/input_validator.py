"""
Validateur d'entrées sécurisé pour l'écosystème Phoenix.
Protection contre XSS, injection, contenu malveillant.

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Security Hardened
"""

import re
import html
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Niveaux de sévérité pour les violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    """Résultat d'une validation d'entrée."""
    is_valid: bool
    sanitized_value: str
    violations: List[Dict[str, Any]]
    severity: ValidationSeverity
    original_value: str

class KaizenInputValidator:
    """🛡️ Validateur spécialisé pour les entrées Kaizen du Dojo Mental."""
    
    def __init__(self):
        """Initialise le validateur avec règles sécurisées."""
        # Patterns dangereux à détecter
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'eval\s*\(',
            r'document\.',
            r'window\.',
            r'alert\s*\(',
            r'confirm\s*\(',
            r'prompt\s*\('
        ]
        
        # Patterns d'injection SQL/NoSQL
        self.injection_patterns = [
            r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)',
            r'(\$where|\$ne|\$gt|\$lt|\$regex)',
            r'(--|\#|/\*|\*/)',
            r'(\bOR\b.*=.*\bOR\b)',
            r'(\'.*\bOR\b.*\')',
            r'(\;|\|\||&&)',
        ]
        
        # Caractères autorisés pour les actions Kaizen
        self.allowed_chars = re.compile(r'^[a-zA-Z0-9àáâäçéèêëîïôöùúûüÿñæœ\s\.\,\!\?\-\(\)\'\"]*$')
        
        # Mots interdits (contenu inapproprié)
        self.forbidden_words = {
            'hack', 'exploit', 'malware', 'virus', 'trojan',
            'botnet', 'ddos', 'phishing', 'scam', 'fraud'
        }
    
    def validate_kaizen_action(self, action: str, user_id: str = None) -> ValidationResult:
        """
        Valide une action Kaizen avec sécurité renforcée.
        
        Args:
            action: Texte de l'action Kaizen
            user_id: ID utilisateur (pour logging)
            
        Returns:
            ValidationResult avec validation et sanitization
        """
        violations = []
        severity = ValidationSeverity.LOW
        original_value = action
        
        # 1. Validation basique
        if not action or not isinstance(action, str):
            return ValidationResult(
                is_valid=False,
                sanitized_value="",
                violations=[{"type": "empty_input", "message": "Action vide ou invalide"}],
                severity=ValidationSeverity.MEDIUM,
                original_value=original_value
            )
        
        # 2. Limite de longueur sécurisée
        if len(action) > 500:  # Limite réduite pour sécurité
            violations.append({
                "type": "length_exceeded",
                "message": f"Action trop longue: {len(action)} caractères (max 500)",
                "severity": ValidationSeverity.MEDIUM
            })
            action = action[:500]
            severity = ValidationSeverity.MEDIUM
        
        # 3. 🛡️ Détection XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, action, re.IGNORECASE):
                violations.append({
                    "type": "xss_detected",
                    "pattern": pattern,
                    "message": "Tentative XSS détectée",
                    "severity": ValidationSeverity.CRITICAL
                })
                severity = ValidationSeverity.CRITICAL
                logger.critical(f"🚨 XSS attempt detected from user {user_id}: {action}")
        
        # 4. 🛡️ Détection injection SQL/NoSQL
        for pattern in self.injection_patterns:
            if re.search(pattern, action, re.IGNORECASE):
                violations.append({
                    "type": "injection_detected", 
                    "pattern": pattern,
                    "message": "Tentative d'injection détectée",
                    "severity": ValidationSeverity.CRITICAL
                })
                severity = ValidationSeverity.CRITICAL
                logger.critical(f"🚨 Injection attempt detected from user {user_id}: {action}")
        
        # 5. Validation caractères autorisés
        if not self.allowed_chars.match(action):
            violations.append({
                "type": "invalid_characters",
                "message": "Caractères non autorisés détectés",
                "severity": ValidationSeverity.MEDIUM
            })
            severity = max(severity, ValidationSeverity.MEDIUM, key=lambda x: x.value)
        
        # 6. Détection mots interdits
        action_lower = action.lower()
        found_forbidden = [word for word in self.forbidden_words if word in action_lower]
        if found_forbidden:
            violations.append({
                "type": "forbidden_content",
                "words": found_forbidden,
                "message": f"Contenu interdit détecté: {found_forbidden}",
                "severity": ValidationSeverity.HIGH
            })
            severity = max(severity, ValidationSeverity.HIGH, key=lambda x: x.value)
        
        # 7. 🧼 Sanitization sécurisée
        sanitized_action = self._sanitize_kaizen_action(action)
        
        # 8. Déterminer validité finale
        is_valid = severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]
        
        # 9. Logging sécurité
        if violations:
            logger.warning(f"🛡️ Kaizen validation violations for user {user_id}: {len(violations)} issues")
            if severity == ValidationSeverity.CRITICAL:
                logger.critical(f"🚨 SECURITY ALERT: Critical validation failure for user {user_id}")
        
        return ValidationResult(
            is_valid=is_valid,
            sanitized_value=sanitized_action,
            violations=violations,
            severity=severity,
            original_value=original_value
        )
    
    def _sanitize_kaizen_action(self, action: str) -> str:
        """
        Sanitise une action Kaizen en sécurité.
        
        Args:
            action: Action à sanitiser
            
        Returns:
            Action sanitisée et sécurisée
        """
        # 1. Échapper HTML pour prévenir XSS
        sanitized = html.escape(action, quote=True)
        
        # 2. Supprimer balises HTML résiduelles
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # 3. Normaliser espaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # 4. Supprimer caractères de contrôle
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        # 5. Trim sécurisé
        sanitized = sanitized.strip()
        
        # 6. Limite finale de sécurité
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        return sanitized
    
    def validate_zazen_duration(self, duration: int, user_id: str = None) -> ValidationResult:
        """
        Valide la durée d'une session Zazen.
        
        Args:
            duration: Durée en secondes
            user_id: ID utilisateur
            
        Returns:
            ValidationResult pour la durée
        """
        violations = []
        severity = ValidationSeverity.LOW
        
        # Limites sécurisées pour durée Zazen
        MIN_DURATION = 30    # 30 secondes minimum
        MAX_DURATION = 3600  # 1 heure maximum
        
        if not isinstance(duration, int) or duration < 0:
            violations.append({
                "type": "invalid_type",
                "message": "Durée doit être un entier positif",
                "severity": ValidationSeverity.HIGH
            })
            severity = ValidationSeverity.HIGH
            duration = MIN_DURATION
        
        elif duration < MIN_DURATION:
            violations.append({
                "type": "duration_too_short",
                "message": f"Durée trop courte: {duration}s (min {MIN_DURATION}s)",
                "severity": ValidationSeverity.MEDIUM
            })
            severity = ValidationSeverity.MEDIUM
            duration = MIN_DURATION
            
        elif duration > MAX_DURATION:
            violations.append({
                "type": "duration_too_long", 
                "message": f"Durée trop longue: {duration}s (max {MAX_DURATION}s)",
                "severity": ValidationSeverity.MEDIUM
            })
            severity = ValidationSeverity.MEDIUM
            duration = MAX_DURATION
        
        is_valid = severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]
        
        return ValidationResult(
            is_valid=is_valid,
            sanitized_value=str(duration),
            violations=violations,
            severity=severity,
            original_value=str(duration)
        )


# Instance globale pour utilisation dans l'API
kaizen_validator = KaizenInputValidator()

def validate_kaizen_input(action: str, user_id: str = None) -> ValidationResult:
    """Helper function pour validation Kaizen."""
    return kaizen_validator.validate_kaizen_action(action, user_id)

def validate_zazen_duration(duration: int, user_id: str = None) -> ValidationResult:
    """Helper function pour validation durée Zazen."""  
    return kaizen_validator.validate_zazen_duration(duration, user_id)