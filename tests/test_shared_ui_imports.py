# tests/test_shared_ui_imports.py
# Test imports des composants UI partagés

import importlib
import pytest

def test_shared_ui_pkg_importable():
    """Test package phoenix_shared_ui importable"""
    m = importlib.import_module("phoenix_shared_ui")
    assert m is not None
    print("✅ phoenix_shared_ui package OK")

def test_components_pkg_importable():
    """Test sous-package components importable"""
    m = importlib.import_module("phoenix_shared_ui.components")
    assert m is not None
    print("✅ phoenix_shared_ui.components package OK")

def test_common_module_importable():
    """Test module common importable"""
    m = importlib.import_module("phoenix_shared_ui.components.common")
    assert m is not None
    print("✅ phoenix_shared_ui.components.common module OK")

def test_common_via_namespace():
    """Test common accessible via namespace components"""
    from phoenix_shared_ui import components
    assert hasattr(components, "common")
    print("✅ common accessible via namespace OK")

def test_premium_barrier_class():
    """Test classe PhoenixPremiumBarrier"""
    from phoenix_shared_ui.components.common import PhoenixPremiumBarrier
    
    # Vérifier méthodes
    assert hasattr(PhoenixPremiumBarrier, 'render')
    assert callable(PhoenixPremiumBarrier.render)
    print("✅ PhoenixPremiumBarrier classe OK")

def test_progress_bar_class():
    """Test classe PhoenixProgressBar"""
    from phoenix_shared_ui.components.common import PhoenixProgressBar
    
    # Vérifier méthodes
    assert hasattr(PhoenixProgressBar, 'render_static')
    assert hasattr(PhoenixProgressBar, 'render_animated')
    assert hasattr(PhoenixProgressBar, 'render_multi_stage')
    assert callable(PhoenixProgressBar.render_static)
    print("✅ PhoenixProgressBar classe OK")

def test_compatibility_functions():
    """Test fonctions de compatibilité app-spécifiques"""
    from phoenix_shared_ui.components.common import (
        render_cv_premium_barrier,
        render_letters_premium_barrier,
        render_cv_progress,
        render_letters_progress
    )
    
    # Toutes doivent être callables
    funcs = [render_cv_premium_barrier, render_letters_premium_barrier, 
             render_cv_progress, render_letters_progress]
    
    for func in funcs:
        assert callable(func)
    
    print("✅ Fonctions compatibilité apps OK")

def test_no_import_side_effects():
    """Test qu'aucun side-effect ne se produit à l'import"""
    
    # L'import ne doit pas lever d'exception liée à Streamlit en mode test
    try:
        from phoenix_shared_ui.components.common import PhoenixPremiumBarrier
        # Si on arrive ici, pas de side-effect problématique
        assert True
        print("✅ Aucun side-effect à l'import")
    except Exception as e:
        if "streamlit" in str(e).lower():
            pytest.fail(f"Side-effect Streamlit détecté: {e}")
        else:
            # Autre erreur
            raise