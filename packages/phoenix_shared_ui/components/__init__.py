# packages/phoenix_shared_ui/components/__init__.py
# 🧩 PHOENIX SHARED UI COMPONENTS

# Rendre accessibles les symboles du module common
from . import common  # permet `from phoenix_shared_ui.components import common`

# Optionnel : réexporter quelques composants phares
from .common import PhoenixPremiumBarrier, PhoenixProgressBar

__all__ = ["common", "PhoenixPremiumBarrier", "PhoenixProgressBar"]