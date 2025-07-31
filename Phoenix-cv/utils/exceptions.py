class SecurityException(Exception):
    """Exception sécurisée sans leak d'information"""
    pass

class ValidationException(Exception):
    """Exception de validation"""
    pass
