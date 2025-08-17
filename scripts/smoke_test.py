#!/usr/bin/env python3
"""
🧪 PHOENIX SMOKE TESTS - Vérification rapide architecture
Script de smoke tests pour CI/CD Pipeline
Conforme au Contrat d'Exécution V5

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Smoke Tests
"""

import sys
import os
from pathlib import Path

# Configuration path pour tests (simulate sitecustomize.py)
ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "packages"
for p in (str(ROOT), str(PKG)):
    if p not in sys.path:
        sys.path.insert(0, p)

def test_smoke_components():
    """Test smoke composants UI Phoenix"""
    
    print("🔍 Test composants UI Phoenix CV...")
    try:
        import importlib.util as u
        assert u.find_spec("phoenix_cv.ui.components.phoenix_header")
        assert u.find_spec("phoenix_cv.ui.components.premium_components")
        assert u.find_spec("phoenix_cv.ui.components.navigation_component")
        print("✅ Composants Phoenix CV OK")
    except Exception as e:
        print(f"❌ Composants Phoenix CV FAIL: {e}")
        return False
    
    return True

def test_smoke_packages():
    """Test smoke packages Phoenix"""
    
    print("🔍 Test packages principaux...")
    packages_to_test = [
        "phoenix_cv",
        "phoenix_letters", 
        "phoenix_common",
        "phoenix_common.settings",
        "phoenix_common.clients",
        "phoenix_common.ui_loader"
    ]
    
    for package in packages_to_test:
        try:
            import importlib.util as u
            assert u.find_spec(package), f"Package {package} non trouvé"
            print(f"✅ {package} OK")
        except Exception as e:
            print(f"❌ {package} FAIL: {e}")
            return False
    
    return True

def test_smoke_settings():
    """Test smoke settings unifié"""
    
    print("🔍 Test settings unifié...")
    try:
        from phoenix_common.settings import get_settings
        settings = get_settings()
        
        # Tests de base
        assert hasattr(settings, 'ENV')
        assert hasattr(settings, 'PHOENIX_SAFE_MODE')
        assert callable(settings.has_supabase)
        assert callable(settings.is_development)
        
        print(f"✅ Settings OK (ENV={settings.ENV}, SAFE_MODE={settings.PHOENIX_SAFE_MODE})")
        return True
        
    except Exception as e:
        print(f"❌ Settings FAIL: {e}")
        return False

def test_smoke_ui_loader():
    """Test smoke UI loader sécurisé"""
    
    print("🔍 Test UI loader sécurisé...")
    try:
        from phoenix_common.ui_loader import import_ui_safe, create_ui_fallback
        
        # Test fallback
        fallback = create_ui_fallback("TestComponent")
        assert hasattr(fallback, 'render')
        
        # Test import sécurisé (doit échouer gracieusement)
        result = import_ui_safe("nonexistent_module", ["TestClass"])
        assert result == [None]
        
        print("✅ UI Loader OK")
        return True
        
    except Exception as e:
        print(f"❌ UI Loader FAIL: {e}")
        return False

def test_smoke_main_runners():
    """Test smoke runners principaux"""
    
    print("🔍 Test runners principaux...")
    try:
        from phoenix_cv.main import run as cv_run
        from phoenix_letters.main import run as letters_run
        
        assert callable(cv_run)
        assert callable(letters_run)
        
        print("✅ Runners OK")
        return True
        
    except Exception as e:
        print(f"❌ Runners FAIL: {e}")
        return False

def main():
    """Exécution complète des smoke tests"""
    
    print("🚀 PHOENIX SMOKE TESTS - Démarrage")
    print("=" * 50)
    
    tests = [
        test_smoke_packages,
        test_smoke_components,
        test_smoke_settings,
        test_smoke_ui_loader,
        test_smoke_main_runners
    ]
    
    failed_tests = []
    
    for test in tests:
        try:
            if not test():
                failed_tests.append(test.__name__)
        except Exception as e:
            print(f"❌ {test.__name__} EXCEPTION: {e}")
            failed_tests.append(test.__name__)
    
    print("=" * 50)
    
    if failed_tests:
        print(f"❌ SMOKE TESTS FAILED: {len(failed_tests)}/{len(tests)}")
        print(f"Échecs: {', '.join(failed_tests)}")
        sys.exit(1)
    else:
        print(f"✅ SMOKE TESTS PASSED: {len(tests)}/{len(tests)}")
        print("🎉 Architecture Phoenix prête pour production !")
        sys.exit(0)

if __name__ == "__main__":
    main()