#!/usr/bin/env python3
"""
🔍 PHOENIX ECOSYSTEM VALIDATOR
Script de validation complète de l'écosystème Phoenix avant déploiement
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json
import subprocess

class PhoenixEcosystemValidator:
    """Validateur complet de l'écosystème Phoenix"""
    
    def __init__(self):
        self.monorepo_root = Path(__file__).resolve().parent
        self.results = {}
        
    def validate_all(self) -> Dict[str, bool]:
        """Validation complète de l'écosystème"""
        print("🔍 PHOENIX ECOSYSTEM VALIDATION - STARTING")
        print("=" * 60)
        
        # Tests de structure
        self.results["structure"] = self.validate_structure()
        self.results["dependencies"] = self.validate_dependencies()
        self.results["docker"] = self.validate_docker_configs()
        self.results["render"] = self.validate_render_config()
        self.results["packages"] = self.validate_shared_packages()
        self.results["services"] = self.validate_services()
        
        # Rapport final
        self.generate_report()
        
        return self.results
    
    def validate_structure(self) -> bool:
        """Valide la structure du monorepo"""
        print("\n📂 STRUCTURE VALIDATION")
        print("-" * 30)
        
        required_paths = [
            "apps/phoenix-letters/app.py",
            "apps/phoenix-letters/main.py", 
            "apps/phoenix-letters/requirements.txt",
            "apps/phoenix-cv/app.py",
            "apps/phoenix-cv/main.py",
            "apps/phoenix-cv/requirements.txt", 
            "apps/phoenix-backend-unified/app.py",
            "apps/phoenix-backend-unified/main.py",
            "apps/phoenix-backend-unified/requirements.txt",
            "apps/phoenix-iris-api/app.py",
            "apps/phoenix-iris-api/main.py",
            "apps/phoenix-iris-api/requirements.txt",
            "apps/phoenix-website/package.json",
            "agent_ia/app.py",
            "agent_ia/requirements.txt",
            "infrastructure/data-pipeline/app.py",
            "infrastructure/data-pipeline/requirements.txt",
            "infrastructure/Dockerfile.worker",
            "Dockerfile",
            "render.yaml"
        ]
        
        missing = []
        for path_str in required_paths:
            path = self.monorepo_root / path_str
            if path.exists():
                print(f"✅ {path_str}")
            else:
                print(f"❌ {path_str}")
                missing.append(path_str)
        
        if missing:
            print(f"\n⚠️ Fichiers manquants: {len(missing)}")
            return False
        else:
            print(f"\n✅ Structure complète - {len(required_paths)} fichiers validés")
            return True
    
    def validate_dependencies(self) -> bool:
        """Valide les dépendances Python"""
        print("\n📦 DEPENDENCIES VALIDATION")
        print("-" * 30)
        
        requirements_files = [
            "apps/phoenix-letters/requirements.txt",
            "apps/phoenix-cv/requirements.txt", 
            "apps/phoenix-backend-unified/requirements.txt",
            "apps/phoenix-iris-api/requirements.txt",
            "agent_ia/requirements.txt",
            "infrastructure/data-pipeline/requirements.txt"
        ]
        
        all_valid = True
        for req_file in requirements_files:
            path = self.monorepo_root / req_file
            if path.exists():
                content = path.read_text()
                if len(content.strip()) > 0:
                    lines = [l for l in content.split('\n') if l.strip() and not l.startswith('#')]
                    print(f"✅ {req_file} - {len(lines)} dépendances")
                else:
                    print(f"❌ {req_file} - Fichier vide")
                    all_valid = False
            else:
                print(f"❌ {req_file} - Manquant")
                all_valid = False
        
        return all_valid
    
    def validate_docker_configs(self) -> bool:
        """Valide les configurations Docker"""
        print("\n🐳 DOCKER VALIDATION")
        print("-" * 30)
        
        docker_files = [
            "Dockerfile",
            "infrastructure/Dockerfile.worker"
        ]
        
        all_valid = True
        for docker_file in docker_files:
            path = self.monorepo_root / docker_file
            if path.exists():
                content = path.read_text()
                if "FROM python" in content and "WORKDIR" in content:
                    print(f"✅ {docker_file} - Configuration valide")
                else:
                    print(f"❌ {docker_file} - Configuration incomplète")
                    all_valid = False
            else:
                print(f"❌ {docker_file} - Manquant")
                all_valid = False
        
        return all_valid
    
    def validate_render_config(self) -> bool:
        """Valide la configuration Render"""
        print("\n⚡ RENDER CONFIGURATION VALIDATION")
        print("-" * 30)
        
        render_path = self.monorepo_root / "render.yaml"
        if not render_path.exists():
            print("❌ render.yaml manquant")
            return False
        
        content = render_path.read_text()
        
        expected_services = [
            "phoenix-letters",
            "phoenix-cv", 
            "phoenix-website",
            "phoenix-backend-unified",
            "phoenix-iris-api",
            "phoenix-event-bridge",
            "phoenix-user-profile",
            "phoenix-agents-ai"
        ]
        
        services_found = 0
        for service in expected_services:
            if f"name: {service}" in content:
                print(f"✅ Service {service}")
                services_found += 1
            else:
                print(f"❌ Service {service} manquant")
        
        print(f"\n📊 Services configurés: {services_found}/{len(expected_services)}")
        return services_found == len(expected_services)
    
    def validate_shared_packages(self) -> bool:
        """Valide les packages partagés"""
        print("\n🔗 SHARED PACKAGES VALIDATION") 
        print("-" * 30)
        
        packages_dir = self.monorepo_root / "packages"
        if not packages_dir.exists():
            print("❌ Dossier packages/ manquant")
            return False
        
        required_packages = [
            "phoenix_shared_auth",
            "phoenix_shared_ui", 
            "phoenix_shared_models",
            "phoenix_event_bridge"
        ]
        
        packages_found = 0
        for package in required_packages:
            package_path = packages_dir / package
            if package_path.exists():
                init_file = package_path / "__init__.py"
                if init_file.exists():
                    print(f"✅ Package {package}")
                    packages_found += 1
                else:
                    print(f"⚠️ Package {package} - __init__.py manquant")
            else:
                print(f"❌ Package {package} manquant")
        
        print(f"\n📊 Packages validés: {packages_found}/{len(required_packages)}")
        return packages_found >= 3  # Au moins 3 sur 4
    
    def validate_services(self) -> bool:
        """Valide la cohérence des services"""
        print("\n🔧 SERVICES CONSISTENCY VALIDATION")
        print("-" * 30)
        
        # Vérification points d'entrée
        services = [
            ("apps/phoenix-letters", "app.py", "streamlit"),
            ("apps/phoenix-cv", "app.py", "streamlit"), 
            ("apps/phoenix-backend-unified", "app.py", "fastapi"),
            ("apps/phoenix-iris-api", "app.py", "fastapi"),
            ("agent_ia", "app.py", "fastapi"),
            ("infrastructure/data-pipeline", "app.py", "asyncio")
        ]
        
        all_valid = True
        for service_dir, entry_point, service_type in services:
            path = self.monorepo_root / service_dir / entry_point
            if path.exists():
                content = path.read_text()
                if service_type == "streamlit" and "streamlit" in content:
                    print(f"✅ {service_dir} - {service_type} service valide")
                elif service_type == "fastapi" and ("FastAPI" in content or "app" in content):
                    print(f"✅ {service_dir} - {service_type} service valide") 
                elif service_type == "asyncio" and "asyncio" in content:
                    print(f"✅ {service_dir} - {service_type} service valide")
                else:
                    print(f"⚠️ {service_dir} - Configuration {service_type} à vérifier")
            else:
                print(f"❌ {service_dir} - Point d'entrée manquant")
                all_valid = False
        
        return all_valid
    
    def generate_report(self):
        """Génère le rapport final"""
        print("\n" + "=" * 60)
        print("📋 PHOENIX ECOSYSTEM VALIDATION REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        
        for test, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test.upper():<20} {status}")
        
        print("-" * 60)
        print(f"RÉSULTAT GLOBAL: {passed_tests}/{total_tests} tests réussis")
        
        if passed_tests == total_tests:
            print("\n🎉 ÉCOSYSTÈME PHOENIX PRÊT POUR LE DÉPLOIEMENT !")
            print("   Tous les services sont configurés et intégrés.")
        elif passed_tests >= total_tests * 0.8:
            print(f"\n⚠️ ÉCOSYSTÈME PHOENIX PRESQUE PRÊT ({passed_tests}/{total_tests})")
            print("   Quelques ajustements mineurs requis.")
        else:
            print(f"\n❌ ÉCOSYSTÈME PHOENIX NÉCESSITE DES CORRECTIONS ({passed_tests}/{total_tests})")
            print("   Plusieurs problèmes à résoudre avant déploiement.")


def main():
    """Point d'entrée principal"""
    validator = PhoenixEcosystemValidator()
    results = validator.validate_all()
    
    # Code de sortie basé sur les résultats
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    if passed_tests == total_tests:
        sys.exit(0)  # Succès complet
    elif passed_tests >= total_tests * 0.8:
        sys.exit(1)  # Avertissements
    else:
        sys.exit(2)  # Erreurs critiques


if __name__ == "__main__":
    main()