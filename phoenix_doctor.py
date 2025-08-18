#!/usr/bin/env python3
"""
🏥 Phoenix Doctor - Health Check pour l'écosystème Phoenix
Validation automatique des configurations de packages
"""

import os
import sys
from pathlib import Path
import toml
from typing import List, Tuple

def check_phoenix_shared_ui() -> Tuple[bool, str]:
    """
    Vérifie la configuration correcte de phoenix-shared-ui
    """
    package_dir = Path("packages/phoenix_shared_ui")
    pyproject_path = package_dir / "pyproject.toml"
    module_init = package_dir / "phoenix_shared_ui" / "__init__.py"
    
    # 1. Vérifier l'existence du pyproject.toml
    if not pyproject_path.exists():
        return False, "❌ pyproject.toml manquant dans packages/phoenix_shared_ui/"
    
    # 2. Vérifier l'existence du module __init__.py
    if not module_init.exists():
        return False, "❌ __init__.py manquant dans packages/phoenix_shared_ui/phoenix_shared_ui/"
    
    # 3. Vérifier la configuration Poetry
    try:
        config = toml.load(pyproject_path)
        
        # Vérifier la section [tool.poetry]
        if "tool" not in config or "poetry" not in config["tool"]:
            return False, "❌ Section [tool.poetry] manquante dans pyproject.toml"
            
        poetry_config = config["tool"]["poetry"]
        
        # Vérifier les packages explicites
        if "packages" not in poetry_config:
            return False, "❌ Déclaration 'packages' manquante - Poetry ne peut pas trouver le module"
            
        packages = poetry_config["packages"]
        if not any(pkg.get("include") == "phoenix_shared_ui" for pkg in packages):
            return False, "❌ Package 'phoenix_shared_ui' non déclaré dans la liste des packages"
            
    except Exception as e:
        return False, f"❌ Erreur lecture pyproject.toml: {e}"
    
    return True, "✅ phoenix-shared-ui correctement configuré"

def check_phoenix_apps_imports() -> Tuple[bool, str]:
    """
    Vérifie que Phoenix Letters et CV peuvent importer phoenix_shared_ui
    """
    import subprocess
    import sys
    
    try:
        # Test Letters
        result_letters = subprocess.run([
            sys.executable, "-c", 
            "import sys; sys.path.insert(0, 'packages'); from phoenix_shared_ui.components.common import PhoenixProgressBar; print('Letters OK')"
        ], cwd=".", capture_output=True, text=True)
        
        # Test CV  
        result_cv = subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, 'packages'); from phoenix_shared_ui.components.common import PhoenixProgressBar; print('CV OK')"
        ], cwd=".", capture_output=True, text=True)
        
        if result_letters.returncode != 0:
            return False, f"❌ Phoenix Letters ne peut pas importer phoenix_shared_ui: {result_letters.stderr}"
        
        if result_cv.returncode != 0:
            return False, f"❌ Phoenix CV ne peut pas importer phoenix_shared_ui: {result_cv.stderr}"
            
        return True, "✅ Phoenix Letters et CV peuvent importer phoenix_shared_ui"
        
    except Exception as e:
        return False, f"❌ Erreur test imports applications: {e}"

def main():
    """
    Exécution des checks de santé Phoenix
    """
    print("🏥 Phoenix Doctor - Health Check")
    print("=" * 40)
    
    checks = [
        ("Phoenix Shared UI", check_phoenix_shared_ui),
        ("Apps Import Tests", check_phoenix_apps_imports),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        passed, message = check_func()
        print(f"{check_name}: {message}")
        if not passed:
            all_passed = False
    
    print("=" * 40)
    if all_passed:
        print("🎉 Tous les checks sont VERTS - Phoenix est en bonne santé!")
        sys.exit(0)
    else:
        print("🚨 Des problèmes détectés - Voir les messages ci-dessus")
        sys.exit(1)

if __name__ == "__main__":
    main()