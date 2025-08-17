# tests/test_settings.py
# Smoke test: vérifie que le loader settings fonctionne hors Streamlit.

from phoenix_common.settings import get_settings, validate_env

def test_settings_loads_and_validates():
    S = get_settings()
    assert S is not None
    # La validation retourne une liste (éventuellement vide) d'erreurs lisibles
    errs = validate_env(S)
    assert isinstance(errs, list)