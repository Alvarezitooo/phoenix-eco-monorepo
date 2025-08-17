# tests/test_ui_imports.py
# 🧪 TESTS IMPORT UI - Conforme Contrat d'Exécution V5
# Verrouillage contre les régressions d'import Phoenix CV

import sys
import os
from pathlib import Path

# Configuration path pour tests (simulate sitecustomize.py)
ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "packages"
for p in (str(ROOT), str(PKG)):
    if p not in sys.path:
        sys.path.insert(0, p)

import importlib.util
import pytest


def test_components_discoverable():
    """Test que tous les composants UI sont découvrables"""
    
    # Composants principaux
    assert importlib.util.find_spec("phoenix_cv.ui.components.phoenix_header")
    assert importlib.util.find_spec("phoenix_cv.ui.components.premium_components") 
    assert importlib.util.find_spec("phoenix_cv.ui.components.navigation_component")
    
    # Package principal
    assert importlib.util.find_spec("phoenix_cv")
    assert importlib.util.find_spec("phoenix_cv.ui")
    assert importlib.util.find_spec("phoenix_cv.ui.components")


def test_main_module_importable():
    """Test que le module principal est importable"""
    
    assert importlib.util.find_spec("phoenix_cv.main")


def test_components_imports():
    """Test que les imports de composants fonctionnent"""
    
    try:
        from phoenix_cv.ui.components import (
            PhoenixCVHeader,
            PhoenixCVPremiumBarrier,
            PhoenixCVNavigation
        )
        
        # Vérification que les classes sont bien importées
        assert PhoenixCVHeader is not None
        assert PhoenixCVPremiumBarrier is not None  
        assert PhoenixCVNavigation is not None
        
        # Vérification des méthodes principales
        assert hasattr(PhoenixCVHeader, 'render')
        assert hasattr(PhoenixCVPremiumBarrier, 'render')
        assert hasattr(PhoenixCVNavigation, 'render_main_nav')
        
    except ImportError as e:
        pytest.fail(f"Échec import composants: {e}")


def test_main_run_function():
    """Test que la fonction run principale est disponible"""
    
    try:
        from phoenix_cv.main import run
        assert callable(run)
        
    except ImportError as e:
        pytest.fail(f"Échec import main.run: {e}")


def test_phoenix_common_settings():
    """Test que le settings unifié fonctionne"""
    
    try:
        from phoenix_common.settings import get_settings
        settings = get_settings()
        
        # Vérifications de base
        assert hasattr(settings, 'ENV')
        assert hasattr(settings, 'PHOENIX_SAFE_MODE')
        assert hasattr(settings, 'has_supabase')
        assert callable(settings.has_supabase)
        
    except ImportError as e:
        pytest.fail(f"Échec import phoenix_common.settings: {e}")


def test_phoenix_common_clients():
    """Test que les clients optimisés sont disponibles"""
    
    try:
        from phoenix_common.clients import get_cached_client_status
        status = get_cached_client_status()
        
        # Vérifications de base
        assert isinstance(status, dict)
        assert 'safe_mode' in status
        
    except ImportError as e:
        pytest.fail(f"Échec import phoenix_common.clients: {e}")


def test_phoenix_common_ui_loader():
    """Test que l'UI loader sécurisé fonctionne"""
    
    try:
        from phoenix_common.ui_loader import import_ui_safe, create_ui_fallback
        
        # Test création fallback
        fallback = create_ui_fallback("TestComponent")
        assert hasattr(fallback, 'render')
        
        # Test import sécurisé (module inexistant)
        result = import_ui_safe("nonexistent_module", ["TestClass"])
        assert result == [None]
        
    except ImportError as e:
        pytest.fail(f"Échec import phoenix_common.ui_loader: {e}")


def test_phoenix_letters_runner():
    """Test que le runner Phoenix Letters est disponible"""
    
    try:
        from phoenix_letters.main import run
        assert callable(run)
        
    except ImportError as e:
        pytest.fail(f"Échec import phoenix_letters.main: {e}")


if __name__ == "__main__":
    # Exécution directe pour debug
    test_components_discoverable()
    test_main_module_importable() 
    test_components_imports()
    test_main_run_function()
    test_phoenix_common_settings()
    test_phoenix_common_clients()
    test_phoenix_common_ui_loader()
    test_phoenix_letters_runner()
    print("✅ Tous les tests d'import UI réussis")