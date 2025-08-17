# sitecustomize.py
# 🏛️ ORACLE PATTERN: Auto-configuration PYTHONPATH pour monorepo Phoenix
# Assure l'importabilité des packages Phoenix (local + Streamlit Cloud)

import sys
import os

ROOT = os.path.dirname(__file__)
PKG = os.path.join(ROOT, "packages")

for p in (ROOT, PKG):
    if p not in sys.path:
        sys.path.insert(0, p)

# 🔍 DEBUG: Confirmation des paths ajoutés
print(f"✅ ORACLE: sitecustomize.py activé - ROOT: {ROOT}, PACKAGES: {PKG}")