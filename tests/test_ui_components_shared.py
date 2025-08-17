# tests/test_ui_components_shared.py
# Test composants UI partagés unifiés

import importlib.util as u
import pytest

def test_shared_ui_components_importable():
    """Test que les composants UI partagés sont découvrables"""
    
    # Composants communs unifiés
    assert u.find_spec("phoenix_shared_ui.components.common.premium_barrier"), "premium_barrier introuvable"
    assert u.find_spec("phoenix_shared_ui.components.common.progress_bar"), "progress_bar introuvable"
    
    print("✅ Composants UI partagés découvrables")

def test_shared_ui_imports():
    """Test imports des composants UI partagés"""
    
    try:
        from phoenix_shared_ui.components.common import (
            PhoenixPremiumBarrier,
            PhoenixProgressBar,
            render_cv_premium_barrier,
            render_letters_premium_barrier
        )
        
        # Vérifications de base
        assert PhoenixPremiumBarrier is not None
        assert PhoenixProgressBar is not None
        assert callable(render_cv_premium_barrier)
        assert callable(render_letters_premium_barrier)
        
        print("✅ Imports composants UI partagés OK")
        
    except ImportError as e:
        pytest.fail(f"Échec import composants UI partagés: {e}")

def test_premium_barrier_api():
    """Test API du premium barrier unifié"""
    
    try:
        from phoenix_shared_ui.components.common import PhoenixPremiumBarrier
        
        # Vérifier que la méthode principale existe
        assert hasattr(PhoenixPremiumBarrier, 'render')
        assert callable(PhoenixPremiumBarrier.render)
        
        print("✅ API Premium Barrier unifié OK")
        
    except Exception as e:
        pytest.fail(f"API Premium Barrier problème: {e}")

def test_progress_bar_api():
    """Test API du progress bar unifié"""
    
    try:
        from phoenix_shared_ui.components.common import PhoenixProgressBar
        
        # Vérifier méthodes principales
        assert hasattr(PhoenixProgressBar, 'render_static')
        assert hasattr(PhoenixProgressBar, 'render_animated')
        assert hasattr(PhoenixProgressBar, 'render_multi_stage')
        
        print("✅ API Progress Bar unifié OK")
        
    except Exception as e:
        pytest.fail(f"API Progress Bar problème: {e}")

def test_compatibility_functions():
    """Test fonctions de compatibilité app-spécifiques"""
    
    try:
        from phoenix_shared_ui.components.common import (
            render_cv_progress,
            render_letters_progress
        )
        
        # Ces fonctions doivent être disponibles pour compatibilité
        assert callable(render_cv_progress)
        assert callable(render_letters_progress)
        
        print("✅ Fonctions compatibilité apps OK")
        
    except ImportError as e:
        pytest.fail(f"Fonctions compatibilité manquantes: {e}")