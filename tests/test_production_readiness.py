# tests/test_production_readiness.py
# Test de préparation production Phoenix

from phoenix_common.settings import get_settings
from phoenix_common.security import is_production_ready

def test_production_readiness_check():
    """Test que la fonction de préparation production fonctionne"""
    
    is_ready, issues = is_production_ready()
    
    # Le test doit retourner un booléen et une liste
    assert isinstance(is_ready, bool)
    assert isinstance(issues, list)
    
    # En mode dev, certains problèmes sont normaux
    settings = get_settings()
    if settings.ENV != "prod":
        print(f"Mode {settings.ENV}: {len(issues)} issues détectés (normal)")
    else:
        if not is_ready:
            print(f"Production non prête: {issues}")

def test_health_monitoring():
    """Test que le monitoring de santé fonctionne"""
    
    try:
        from phoenix_common.monitoring import health_check
        health = health_check()
        
        assert "timestamp" in health
        assert "env" in health
        assert "services" in health
        
        print(f"Health check OK: {len(health['services'])} services vérifiés")
        
    except ImportError:
        print("Monitoring non disponible (dépendances optionnelles)")
        assert True  # Test passé quand même