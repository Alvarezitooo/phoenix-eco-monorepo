# tests/test_ui_imports.py
# Smoke test: s'assure que les composants UI sont découvrables.
# Nécessite que sitecustomize.py soit à la racine du repo
# OU pyproject.toml -> [tool.pytest.ini_options] pythonpath=["packages"]

import importlib.util as u

def test_cv_components_discoverable():
    assert u.find_spec("phoenix_cv.ui.components.phoenix_header"), "phoenix_header introuvable"
    assert u.find_spec("phoenix_cv.ui.components.premium_components"), "premium_components introuvable"
    assert u.find_spec("phoenix_cv.ui.components.navigation_component"), "navigation_component introuvable"