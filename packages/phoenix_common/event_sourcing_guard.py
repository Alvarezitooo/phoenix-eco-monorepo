# packages/phoenix_common/event_sourcing_guard.py
# 🏛️ ORACLE PATTERN: Guard contre mutations directes - force event-sourcing

import logging
from typing import Any, Dict, List
from functools import wraps

logger = logging.getLogger(__name__)

class EventSourcingViolation(Exception):
    """Exception levée lors de mutations directes non autorisées"""
    pass

class EventSourcingGuard:
    """
    Garde-fou pour garantir l'event-sourcing dans tout l'écosystème Phoenix
    Interdit les mutations directes de state sans événement
    """
    
    FORBIDDEN_PATTERNS = [
        # Mutations directes Supabase
        "table().update(",
        "table().delete(",
        "table().insert(",
        # Mutations directes SQL
        "UPDATE ",
        "DELETE ",
        "INSERT INTO",
        # Mutations state local sans event
        "st.session_state[",  # Streamlit state mutation
    ]
    
    ALLOWED_EXCEPTIONS = [
        # Event bridge lui-même
        "phoenix_event_bridge",
        "event_bridge",
        # Tests
        "test_",
        "conftest",
        # Setup/migration
        "migration",
        "setup",
        "schema",
    ]
    
    @classmethod
    def validate_code_compliance(cls, code: str, file_path: str) -> List[str]:
        """
        Valide qu'un code respecte l'event-sourcing
        Retourne une liste des violations détectées
        """
        violations = []
        
        # Skip si exception autorisée
        if any(exception in file_path.lower() for exception in cls.ALLOWED_EXCEPTIONS):
            return violations
        
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            line_clean = line.strip()
            
            for pattern in cls.FORBIDDEN_PATTERNS:
                if pattern.lower() in line_clean.lower():
                    violation = f"Line {line_num}: Direct state mutation detected: '{line_clean}'"
                    violations.append(violation)
                    logger.warning(f"🚨 Event-sourcing violation in {file_path}: {violation}")
        
        return violations
    
    @staticmethod
    def require_event_publication(operation_name: str):
        """
        Décorateur qui force la publication d'un événement avant mutation
        Usage: @EventSourcingGuard.require_event_publication("UserProfileUpdate")
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Vérifier qu'un événement a été publié
                if not hasattr(wrapper, '_event_published'):
                    raise EventSourcingViolation(
                        f"Operation '{operation_name}' requires event publication before execution. "
                        f"Use phoenix_event_bridge.publish_event() first."
                    )
                
                result = func(*args, **kwargs)
                
                # Reset flag pour prochaine invocation
                wrapper._event_published = False
                
                return result
            
            # Méthode pour marquer l'événement comme publié
            def mark_event_published():
                wrapper._event_published = True
            
            wrapper.mark_event_published = mark_event_published
            return wrapper
        return decorator
    
    @staticmethod
    def safe_state_mutation(event_type: str, payload: Dict[str, Any]):
        """
        Wrapper sécurisé pour mutations d'état via événements
        
        Usage:
        EventSourcingGuard.safe_state_mutation(
            "user.profile_updated", 
            {"user_id": "123", "field": "email", "new_value": "new@email.com"}
        )
        """
        try:
            from phoenix_event_bridge import PhoenixEventBridge, PhoenixEventType, PhoenixEventData
            
            bridge = PhoenixEventBridge()
            
            event_data = PhoenixEventData(
                event_type=PhoenixEventType(event_type),
                stream_id=payload.get('user_id', 'system'),
                payload=payload,
                app_source="event_sourcing_guard"
            )
            
            # Publier l'événement au lieu de muter directement
            event_id = bridge.publish_event(event_data)
            logger.info(f"✅ State mutation via event: {event_id}")
            
            return event_id
            
        except Exception as e:
            logger.error(f"❌ Failed to publish event for state mutation: {e}")
            raise EventSourcingViolation(f"Cannot perform state mutation: {e}")

# Utilitaires pour migration progressive
def migrate_direct_mutation_to_event(
    mutation_func,
    event_type: str,
    extract_payload_func
):
    """
    Helper pour migrer du code legacy avec mutations directes vers event-sourcing
    
    Args:
        mutation_func: Fonction originale qui fait la mutation directe
        event_type: Type d'événement à publier à la place
        extract_payload_func: Fonction qui extrait le payload de l'événement
    """
    @wraps(mutation_func)
    def wrapper(*args, **kwargs):
        logger.warning(f"🔄 Migrating direct mutation to event-sourcing: {mutation_func.__name__}")
        
        # Extraire payload depuis les arguments
        payload = extract_payload_func(*args, **kwargs)
        
        # Publier événement au lieu de mutation directe
        return EventSourcingGuard.safe_state_mutation(event_type, payload)
    
    return wrapper