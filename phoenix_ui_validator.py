#!/usr/bin/env python3
"""
🏛️ Phoenix UI Validator - Audit Interface Front-End
Valide l'expérience utilisateur pour Phoenix CV & Letters
"""

import os
import sys
import time
import subprocess
import requests
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
import json

@dataclass
class TestResult:
    """Résultat d'un test individuel"""
    element: str
    expected: str
    observed: str
    status: str
    notes: str = ""

@dataclass
class UIAuditReport:
    """Rapport d'audit complet de l'interface"""
    app_name: str
    test_mode: str
    results: List[TestResult] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""
    
    def add_result(self, element: str, expected: str, observed: str, status: str, notes: str = ""):
        """Ajoute un résultat de test"""
        self.results.append(TestResult(element, expected, observed, status, notes))
    
    def get_summary(self) -> Dict[str, int]:
        """Retourne un résumé des résultats"""
        summary = {"OK": 0, "FAIL": 0, "WARNING": 0, "SKIP": 0}
        for result in self.results:
            summary[result.status] = summary.get(result.status, 0) + 1
        return summary
    
    def print_report(self):
        """Affiche le rapport formaté"""
        print(f"\n🏛️ Phoenix UI Audit Report - {self.app_name}")
        print("=" * 80)
        print(f"Mode de test: {self.test_mode}")
        print(f"Période: {self.start_time} → {self.end_time}")
        print()
        
        # Tableau des résultats
        print("| Élément testé | Résultat attendu | Résultat observé | Statut |")
        print("|--------------|------------------|------------------|--------|")
        
        for result in self.results:
            status_emoji = {
                "OK": "✅",
                "FAIL": "❌", 
                "WARNING": "⚠️",
                "SKIP": "⏭️"
            }.get(result.status, "❓")
            
            print(f"| {result.element} | {result.expected} | {result.observed} | {status_emoji} {result.status} |")
            if result.notes:
                print(f"| | | Notes: {result.notes} | |")
        
        print()
        
        # Résumé
        summary = self.get_summary()
        print(f"📊 Résumé: {summary['OK']} OK, {summary['FAIL']} FAIL, {summary['WARNING']} WARNING, {summary['SKIP']} SKIP")
        print()

class PhoenixUIValidator:
    """Validateur d'interface Phoenix"""
    
    def __init__(self):
        self.monorepo_root = Path(__file__).resolve().parent
        self.expected_price_ids = {
            "cv_premium": "price_1RraUoDcM3VIYgvy0NXiKmKV",
            "letters_premium": "price_1RraAcDcM3VIYgvyEBNFXfbR", 
            "bundle": "price_1RraWhDcM3VIYgvyGykPghCc"
        }
    
    def validate_app_structure(self, app_name: str) -> UIAuditReport:
        """Valide la structure et les composants d'une application"""
        report = UIAuditReport(
            app_name=app_name,
            test_mode="Structure Validation",
            start_time=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        app_path = self.monorepo_root / "apps" / f"phoenix-{app_name}"
        
        # 1. Vérification existence de l'app
        if app_path.exists():
            report.add_result(
                f"App {app_name}", 
                "Dossier existant",
                f"✅ Trouvé à {app_path}",
                "OK"
            )
        else:
            report.add_result(
                f"App {app_name}",
                "Dossier existant", 
                f"❌ Pas trouvé à {app_path}",
                "FAIL"
            )
            return report
        
        # 2. Vérification du point d'entrée
        entry_point = app_path / "app.py"
        if entry_point.exists():
            report.add_result(
                "Point d'entrée",
                "app.py présent",
                "✅ Fichier trouvé",
                "OK"
            )
        else:
            report.add_result(
                "Point d'entrée",
                "app.py présent",
                "❌ app.py manquant",
                "FAIL"
            )
        
        # 3. Vérification des imports phoenix_shared_ui
        self._check_shared_ui_imports(app_path, report)
        
        # 4. Vérification des price IDs dans le code
        self._check_price_ids_in_code(app_path, app_name, report)
        
        report.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        return report
    
    def _check_shared_ui_imports(self, app_path: Path, report: UIAuditReport):
        """Vérifie que l'app peut importer phoenix_shared_ui"""
        try:
            # Test d'import depuis le contexte de l'app
            test_script = f"""
import sys
sys.path.insert(0, '{self.monorepo_root}/packages')
try:
    from phoenix_shared_ui.components.common import PhoenixProgressBar
    print('IMPORT_SUCCESS')
except Exception as e:
    print(f'IMPORT_FAIL: {{e}}')
"""
            
            result = subprocess.run([
                sys.executable, "-c", test_script
            ], capture_output=True, text=True, timeout=10)
            
            if "IMPORT_SUCCESS" in result.stdout:
                report.add_result(
                    "Import phoenix_shared_ui",
                    "Import réussi",
                    "✅ Composants partagés accessibles",
                    "OK"
                )
            else:
                report.add_result(
                    "Import phoenix_shared_ui", 
                    "Import réussi",
                    f"❌ Erreur: {result.stdout or result.stderr}",
                    "FAIL"
                )
        except Exception as e:
            report.add_result(
                "Import phoenix_shared_ui",
                "Import réussi",
                f"❌ Exception: {e}",
                "FAIL"
            )
    
    def _check_price_ids_in_code(self, app_path: Path, app_name: str, report: UIAuditReport):
        """Vérifie la présence des bons price IDs dans le code"""
        # Recherche récursive des price IDs
        found_prices = {}
        
        for py_file in app_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for price_type, price_id in self.expected_price_ids.items():
                        if price_id in content:
                            found_prices[price_type] = py_file.name
            except Exception:
                continue
        
        # Vérification selon l'app
        expected_for_app = []
        if app_name == "cv":
            expected_for_app = ["cv_premium", "bundle"]
        elif app_name == "letters":  
            expected_for_app = ["letters_premium", "bundle"]
        
        for price_type in expected_for_app:
            if price_type in found_prices:
                report.add_result(
                    f"Price ID {price_type}",
                    f"Présent: {self.expected_price_ids[price_type]}",
                    f"✅ Trouvé dans {found_prices[price_type]}",
                    "OK"
                )
            else:
                report.add_result(
                    f"Price ID {price_type}",
                    f"Présent: {self.expected_price_ids[price_type]}",
                    "❌ Non trouvé dans le code",
                    "FAIL"
                )
    
    def validate_stripe_integration(self, app_name: str) -> UIAuditReport:
        """Valide l'intégration Stripe (sans lancer l'app)"""
        report = UIAuditReport(
            app_name=app_name,
            test_mode="Stripe Integration Check",
            start_time=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Vérification des variables d'environnement Stripe
        stripe_vars = ["STRIPE_PUBLISHABLE_KEY", "STRIPE_SECRET_KEY", "STRIPE_CV_PRICE_ID", 
                      "STRIPE_LETTERS_PRICE_ID", "STRIPE_BUNDLE_PRICE_ID"]
        
        for var in stripe_vars:
            value = os.getenv(var)
            if value:
                # Masquer la clé secrète
                displayed_value = value[:12] + "..." if "sk_" in value else value
                report.add_result(
                    f"Variable {var}",
                    "Définie",
                    f"✅ {displayed_value}",
                    "OK"
                )
            else:
                report.add_result(
                    f"Variable {var}",
                    "Définie", 
                    "❌ Non définie",
                    "WARNING",
                    "Variable manquante pour tests Stripe complets"
                )
        
        # Vérification des imports Stripe dans le code
        app_path = self.monorepo_root / "apps" / f"phoenix-{app_name}"
        stripe_imports_found = False
        
        for py_file in app_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "stripe" in content.lower() and ("checkout" in content.lower() or "Session" in content):
                        stripe_imports_found = True
                        break
            except Exception:
                continue
        
        if stripe_imports_found:
            report.add_result(
                "Intégration Stripe code",
                "Imports/usage Stripe présents",
                "✅ Code Stripe trouvé",
                "OK"
            )
        else:
            report.add_result(
                "Intégration Stripe code",
                "Imports/usage Stripe présents", 
                "❌ Aucun code Stripe détecté",
                "FAIL"
            )
        
        report.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        return report
    
    def check_safe_mode_handling(self, app_name: str) -> UIAuditReport:
        """Vérifie la gestion du SAFE_MODE"""
        report = UIAuditReport(
            app_name=app_name,
            test_mode="SAFE_MODE Check",
            start_time=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        app_path = self.monorepo_root / "apps" / f"phoenix-{app_name}"
        safe_mode_handling = False
        
        # Recherche de gestion SAFE_MODE dans le code
        for py_file in app_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "SAFE_MODE" in content or "safe_mode" in content:
                        safe_mode_handling = True
                        break
            except Exception:
                continue
        
        if safe_mode_handling:
            report.add_result(
                "Gestion SAFE_MODE",
                "Code de gestion présent",
                "✅ Logique SAFE_MODE détectée",
                "OK"
            )
        else:
            report.add_result(
                "Gestion SAFE_MODE",
                "Code de gestion présent",
                "⚠️ Aucune gestion SAFE_MODE trouvée",
                "WARNING",
                "L'app pourrait ne pas gérer le mode dégradé"
            )
        
        report.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        return report
    
    def run_full_audit(self) -> List[UIAuditReport]:
        """Lance un audit complet des deux applications"""
        print("🚀 Lancement de l'audit Phoenix UI...")
        print()
        
        reports = []
        
        for app in ["cv", "letters"]:
            print(f"📋 Audit de Phoenix {app.upper()}...")
            
            # Tests de structure
            structure_report = self.validate_app_structure(app)
            reports.append(structure_report)
            
            # Tests Stripe
            stripe_report = self.validate_stripe_integration(app)
            reports.append(stripe_report)
            
            # Tests SAFE_MODE
            safe_mode_report = self.check_safe_mode_handling(app)
            reports.append(safe_mode_report)
            
            print(f"✅ Audit {app} terminé\n")
        
        return reports

def main():
    """Point d'entrée principal"""
    print("🏛️ Phoenix UI Validator")
    print("=" * 50)
    
    # Vérification de l'environnement
    env_mode = os.getenv("ENV", "dev")
    safe_mode = os.getenv("PHOENIX_SAFE_MODE", "0") == "1"
    
    print(f"Environment: {env_mode}")
    print(f"Safe Mode: {safe_mode}")
    print()
    
    # Lancement de l'audit
    validator = PhoenixUIValidator()
    reports = validator.run_full_audit()
    
    # Affichage des rapports
    for report in reports:
        report.print_report()
    
    # Résumé global
    total_ok = sum(r.get_summary()["OK"] for r in reports)
    total_fail = sum(r.get_summary()["FAIL"] for r in reports) 
    total_warning = sum(r.get_summary()["WARNING"] for r in reports)
    
    print("🏆 RÉSUMÉ GLOBAL PHOENIX UI")
    print("=" * 50)
    print(f"✅ Tests réussis: {total_ok}")
    print(f"❌ Tests échoués: {total_fail}")
    print(f"⚠️ Avertissements: {total_warning}")
    print()
    
    if total_fail == 0:
        print("🎉 Interface Phoenix prête pour production!")
        return 0
    else:
        print("🚨 Des corrections sont nécessaires avant déploiement")
        return 1

if __name__ == "__main__":
    sys.exit(main())