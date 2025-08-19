#!/usr/bin/env python3
"""
🔍 RENDER DEPLOYMENT CHECKER - Validation Pré-Déploiement
Vérification complète avant déploiement sur Render
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
import json
import subprocess
import re

class RenderDeploymentChecker:
    """Checker spécialisé pour déploiement Render"""
    
    def __init__(self):
        self.monorepo_root = Path(__file__).resolve().parent
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def check_all(self) -> bool:
        """Check complet pré-déploiement"""
        print("🔍 RENDER DEPLOYMENT PRE-CHECK - STARTING")
        print("=" * 60)
        
        # Checks critiques
        self.check_render_yaml()
        self.check_dockerfiles()
        self.check_app_entry_points()
        self.check_requirements()
        self.check_environment_variables()
        self.check_health_endpoints()
        self.check_port_configurations()
        self.check_shared_packages()
        self.check_service_dependencies()
        
        # Rapport final
        self.generate_deployment_report()
        
        return len(self.issues) == 0
    
    def check_render_yaml(self):
        """Vérification approfondie du render.yaml"""
        print("\n⚡ RENDER.YAML VALIDATION")
        print("-" * 30)
        
        render_path = self.monorepo_root / "render.yaml"
        
        if not render_path.exists():
            self.issues.append("render.yaml manquant à la racine")
            return
            
        try:
            with open(render_path) as f:
                config = yaml.safe_load(f)
        except Exception as e:
            self.issues.append(f"render.yaml invalide: {e}")
            return
            
        services = config.get('services', [])
        if not services:
            self.issues.append("Aucun service défini dans render.yaml")
            return
            
        expected_services = {
            'phoenix-letters': {'type': 'web', 'plan': 'starter'},
            'phoenix-cv': {'type': 'web', 'plan': 'starter'},
            'phoenix-website': {'type': 'web', 'plan': 'free'},
            'phoenix-backend-unified': {'type': 'web', 'plan': 'starter'},
            'phoenix-iris-api': {'type': 'web', 'plan': 'starter'},
            'phoenix-agents-ai': {'type': 'web', 'plan': 'starter'},
            'phoenix-event-bridge': {'type': 'worker', 'plan': 'free'},
            'phoenix-user-profile': {'type': 'worker', 'plan': 'free'}
        }
        
        found_services = {}
        for service in services:
            name = service.get('name')
            service_type = service.get('type')
            plan = service.get('plan')
            
            if name in expected_services:
                found_services[name] = {'type': service_type, 'plan': plan}
                expected = expected_services[name]
                
                # Vérifications détaillées
                if service_type != expected['type']:
                    self.issues.append(f"Service {name}: type '{service_type}' != attendu '{expected['type']}'")
                    
                if 'dockerfilePath' not in service:
                    self.issues.append(f"Service {name}: dockerfilePath manquant")
                    
                if service_type == 'web' and 'healthCheckPath' not in service:
                    self.warnings.append(f"Service {name}: healthCheckPath recommandé pour web services")
                    
                if 'envVars' not in service:
                    self.warnings.append(f"Service {name}: envVars vide")
                
                self.successes.append(f"Service {name}: configuré correctement")
        
        # Services manquants
        missing = set(expected_services.keys()) - set(found_services.keys())
        for service in missing:
            self.issues.append(f"Service manquant: {service}")
            
        print(f"Services trouvés: {len(found_services)}/8")
    
    def check_dockerfiles(self):
        """Vérification des Dockerfiles"""
        print("\n🐳 DOCKERFILES VALIDATION")
        print("-" * 30)
        
        dockerfiles = {
            "Dockerfile": "Dockerfile principal monorepo",
            "infrastructure/Dockerfile.worker": "Dockerfile workers"
        }
        
        for dockerfile, description in dockerfiles.items():
            path = self.monorepo_root / dockerfile
            
            if not path.exists():
                self.issues.append(f"{dockerfile} manquant")
                continue
                
            content = path.read_text()
            
            # Vérifications essentielles
            checks = [
                ("FROM python:", "Image de base Python"),
                ("WORKDIR", "Working directory défini"),
                ("COPY", "Copie des fichiers"),
                ("RUN pip install", "Installation dépendances"),
                ("CMD", "Commande de démarrage"),
                ("USER phoenix", "Utilisateur non-root"),
                ("EXPOSE", "Port exposé")
            ]
            
            dockerfile_issues = []
            for check, desc in checks:
                if check not in content:
                    dockerfile_issues.append(f"{desc} manquant")
            
            if dockerfile_issues:
                self.issues.extend([f"{dockerfile}: {issue}" for issue in dockerfile_issues])
            else:
                self.successes.append(f"{dockerfile}: structure valide")
    
    def check_app_entry_points(self):
        """Vérification des points d'entrée app.py"""
        print("\n📱 APP ENTRY POINTS VALIDATION")
        print("-" * 30)
        
        app_paths = [
            "apps/phoenix-letters/app.py",
            "apps/phoenix-cv/app.py", 
            "apps/phoenix-backend-unified/app.py",
            "apps/phoenix-iris-api/app.py",
            "agent_ia/app.py",
            "infrastructure/data-pipeline/app.py"
        ]
        
        for app_path in app_paths:
            path = self.monorepo_root / app_path
            
            if not path.exists():
                self.issues.append(f"Point d'entrée manquant: {app_path}")
                continue
                
            content = path.read_text()
            
            # Vérifications par type d'app
            if "streamlit" in app_path or app_path.endswith(("phoenix-letters/app.py", "phoenix-cv/app.py")):
                if "streamlit" not in content and "main" not in content:
                    self.issues.append(f"{app_path}: Point d'entrée Streamlit invalide")
                else:
                    self.successes.append(f"{app_path}: Point d'entrée Streamlit valide")
                    
            elif "fastapi" in content.lower() or "uvicorn" in content:
                if "app" not in content:
                    self.issues.append(f"{app_path}: Point d'entrée FastAPI invalide")
                else:
                    self.successes.append(f"{app_path}: Point d'entrée FastAPI valide")
            else:
                self.warnings.append(f"{app_path}: Type de point d'entrée non identifié")
    
    def check_requirements(self):
        """Vérification des requirements.txt"""
        print("\n📦 REQUIREMENTS.TXT VALIDATION")
        print("-" * 30)
        
        requirements_paths = [
            "apps/phoenix-letters/requirements.txt",
            "apps/phoenix-cv/requirements.txt",
            "apps/phoenix-backend-unified/requirements.txt", 
            "apps/phoenix-iris-api/requirements.txt",
            "agent_ia/requirements.txt",
            "infrastructure/data-pipeline/requirements.txt"
        ]
        
        for req_path in requirements_paths:
            path = self.monorepo_root / req_path
            
            if not path.exists():
                self.issues.append(f"Requirements manquant: {req_path}")
                continue
                
            content = path.read_text().strip()
            if not content:
                self.issues.append(f"Requirements vide: {req_path}")
                continue
                
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            
            # Vérifications spécifiques par service
            if "streamlit" in req_path:
                if not any("streamlit" in line for line in lines):
                    self.issues.append(f"{req_path}: streamlit manquant")
                    
            elif "fastapi" in req_path or "backend" in req_path or "iris" in req_path:
                has_fastapi = any("fastapi" in line for line in lines)
                has_uvicorn = any("uvicorn" in line for line in lines)
                if not (has_fastapi or has_uvicorn):
                    self.issues.append(f"{req_path}: fastapi/uvicorn manquant")
            
            # Vérification versions
            problematic = []
            for line in lines:
                if "==" not in line and ">=" not in line and not line.startswith("#"):
                    problematic.append(line)
                    
            if problematic:
                self.warnings.append(f"{req_path}: {len(problematic)} dépendances sans version")
            
            self.successes.append(f"{req_path}: {len(lines)} dépendances")
    
    def check_environment_variables(self):
        """Vérification des variables d'environnement"""
        print("\n⚙️ ENVIRONMENT VARIABLES VALIDATION")
        print("-" * 30)
        
        # Variables critiques requises
        critical_vars = [
            "GOOGLE_API_KEY",
            "SUPABASE_URL", 
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY"
        ]
        
        # Variables recommandées
        recommended_vars = [
            "STRIPE_SECRET_KEY",
            "STRIPE_PUBLISHABLE_KEY", 
            "JWT_SECRET_KEY",
            "OPENAI_API_KEY"
        ]
        
        # Vérification .env.example
        for app_dir in ["apps/phoenix-letters", "apps/phoenix-cv"]:
            env_example = self.monorepo_root / app_dir / ".env.example"
            if env_example.exists():
                content = env_example.read_text()
                missing_critical = [var for var in critical_vars if var not in content]
                if missing_critical:
                    self.warnings.append(f"{app_dir}/.env.example: Variables critiques manquantes: {missing_critical}")
                else:
                    self.successes.append(f"{app_dir}/.env.example: Variables critiques présentes")
            else:
                self.warnings.append(f"{app_dir}/.env.example manquant")
        
        # Check render.yaml env vars
        render_path = self.monorepo_root / "render.yaml"
        if render_path.exists():
            content = render_path.read_text()
            for var in critical_vars:
                if var not in content:
                    self.warnings.append(f"render.yaml: Variable critique {var} non configurée")
    
    def check_health_endpoints(self):
        """Vérification des endpoints de santé"""
        print("\n🏥 HEALTH ENDPOINTS VALIDATION")
        print("-" * 30)
        
        # Recherche des health endpoints dans le code
        health_patterns = {
            "apps/phoenix-backend-unified": ["/health", "health"],
            "apps/phoenix-iris-api": ["/health", "health"],
            "agent_ia": ["/health", "health"]
        }
        
        for service_dir, patterns in health_patterns.items():
            found_health = False
            
            # Recherche dans tous les fichiers Python du service
            service_path = self.monorepo_root / service_dir
            if service_path.exists():
                for py_file in service_path.rglob("*.py"):
                    try:
                        content = py_file.read_text()
                        if any(pattern in content for pattern in patterns):
                            found_health = True
                            break
                    except:
                        continue
            
            if found_health:
                self.successes.append(f"{service_dir}: Health endpoint trouvé")
            else:
                self.warnings.append(f"{service_dir}: Health endpoint non trouvé")
    
    def check_port_configurations(self):
        """Vérification des configurations de ports"""
        print("\n🔌 PORT CONFIGURATIONS VALIDATION") 
        print("-" * 30)
        
        # Streamlit apps doivent utiliser 8501
        streamlit_apps = ["apps/phoenix-letters", "apps/phoenix-cv"]
        
        for app_dir in streamlit_apps:
            app_py = self.monorepo_root / app_dir / "app.py"
            main_py = self.monorepo_root / app_dir / "main.py"
            
            found_port_config = False
            for py_file in [app_py, main_py]:
                if py_file.exists():
                    content = py_file.read_text()
                    if "8501" in content or "server.port" in content:
                        found_port_config = True
                        break
            
            if found_port_config:
                self.successes.append(f"{app_dir}: Port Streamlit configuré")
            else:
                self.warnings.append(f"{app_dir}: Port Streamlit non explicitement configuré")
        
        # FastAPI apps doivent utiliser port variable
        fastapi_apps = ["apps/phoenix-backend-unified", "apps/phoenix-iris-api", "agent_ia"]
        
        for app_dir in fastapi_apps:
            app_py = self.monorepo_root / app_dir / "app.py"
            main_py = self.monorepo_root / app_dir / "main.py"
            
            found_port_config = False
            for py_file in [app_py, main_py]:
                if py_file.exists():
                    content = py_file.read_text()
                    if "0.0.0.0" in content and ("8000" in content or "port" in content):
                        found_port_config = True
                        break
            
            if found_port_config:
                self.successes.append(f"{app_dir}: Port FastAPI configuré")
            else:
                self.warnings.append(f"{app_dir}: Port FastAPI à vérifier")
    
    def check_shared_packages(self):
        """Vérification des packages partagés"""
        print("\n🔗 SHARED PACKAGES VALIDATION")
        print("-" * 30)
        
        packages_dir = self.monorepo_root / "packages"
        required_packages = [
            "phoenix_shared_auth",
            "phoenix_shared_ui",
            "phoenix_shared_models", 
            "phoenix_event_bridge"
        ]
        
        for package in required_packages:
            package_path = packages_dir / package
            init_file = package_path / "__init__.py"
            
            if not package_path.exists():
                self.issues.append(f"Package manquant: {package}")
            elif not init_file.exists():
                self.issues.append(f"Package {package}: __init__.py manquant")
            else:
                self.successes.append(f"Package {package}: structure valide")
    
    def check_service_dependencies(self):
        """Vérification des dépendances entre services"""
        print("\n🔄 SERVICE DEPENDENCIES VALIDATION")
        print("-" * 30)
        
        # Vérification que les imports des packages partagés sont corrects
        apps_with_shared_deps = [
            "apps/phoenix-letters",
            "apps/phoenix-cv",
            "apps/phoenix-backend-unified"
        ]
        
        for app_dir in apps_with_shared_deps:
            app_path = self.monorepo_root / app_dir
            has_shared_imports = False
            
            if app_path.exists():
                for py_file in app_path.rglob("*.py"):
                    try:
                        content = py_file.read_text()
                        if "from packages." in content or "packages/" in content:
                            has_shared_imports = True
                            break
                    except:
                        continue
            
            if has_shared_imports:
                self.successes.append(f"{app_dir}: Imports packages partagés détectés")
            else:
                self.warnings.append(f"{app_dir}: Imports packages partagés non détectés")
    
    def generate_deployment_report(self):
        """Génère le rapport final de déploiement"""
        print("\n" + "=" * 60)
        print("📋 RENDER DEPLOYMENT READINESS REPORT")
        print("=" * 60)
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        total_successes = len(self.successes)
        
        # Issues critiques
        if self.issues:
            print(f"\n❌ ISSUES CRITIQUES À CORRIGER ({total_issues}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️ AVERTISSEMENTS À VÉRIFIER ({total_warnings}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        # Succès
        if self.successes:
            print(f"\n✅ VALIDATIONS RÉUSSIES ({total_successes}):")
            for success in self.successes[-10:]:  # Top 10 récents
                print(f"   ✓ {success}")
            if total_successes > 10:
                print(f"   ... et {total_successes - 10} autres validations")
        
        # Verdict final
        print("\n" + "-" * 60)
        
        if total_issues == 0:
            print("🎉 DÉPLOIEMENT AUTORISÉ !")
            print("   Tous les checks critiques sont validés.")
            print("   Tu peux déployer sur Render en toute sécurité.")
            
            if total_warnings > 0:
                print(f"   Note: {total_warnings} avertissements à surveiller post-déploiement.")
                
        elif total_issues <= 3:
            print("⚠️ DÉPLOIEMENT POSSIBLE AVEC PRÉCAUTIONS")
            print(f"   {total_issues} issues mineures à corriger.")
            print("   Recommandation: Corriger puis re-check.")
            
        else:
            print("❌ DÉPLOIEMENT NON RECOMMANDÉ")
            print(f"   {total_issues} issues critiques à résoudre.")
            print("   Correction obligatoire avant déploiement.")
        
        # Actions recommandées
        print(f"\n📋 ACTIONS RECOMMANDÉES:")
        if total_issues > 0:
            print(f"   1. Corriger les {total_issues} issues critiques")
        if total_warnings > 0:
            print(f"   2. Vérifier les {total_warnings} avertissements")
        print("   3. Re-run ce check: python3 render_deployment_checker.py")
        print("   4. Si tout OK: git push origin main")
        
        return total_issues == 0


def main():
    """Point d'entrée principal"""
    checker = RenderDeploymentChecker()
    is_ready = checker.check_all()
    
    if is_ready:
        print(f"\n🚀 READY TO DEPLOY ON RENDER!")
        sys.exit(0)
    else:
        print(f"\n🔧 FIXES REQUIRED BEFORE DEPLOYMENT")
        sys.exit(1)


if __name__ == "__main__":
    main()