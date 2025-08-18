"""UI Components pour Phoenix Letters."""

# Import conditionnel pour éviter les erreurs si iris_widget n'existe pas
try:
    from .iris_widget import IrisFloatingWidget, render_iris_floating_widget
    __all__ = ["IrisFloatingWidget", "render_iris_floating_widget"]
except ImportError:
    # iris_widget n'existe pas - mode dégradé
    __all__ = []