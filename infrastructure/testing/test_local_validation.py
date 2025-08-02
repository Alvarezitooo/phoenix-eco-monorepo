"""
🔥 Phoenix Ecosystem - Tests de Validation Locale
Validation de la configuration et des fichiers avant déploiement

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Local Validation Suite
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def test_project_structure() -> Dict[str, Any]:
    """Valide la structure du projet."""
    test_result = {
        "test_name": "Project Structure Validation",
        "success": False,
        "duration": 0,
        "details": {}
    }
    
    start_time = time.time()
    
    try:
        base_path = Path("/Users/mattvaness/Desktop/IA/phoenix/phoenix-eco")
        
        required_structure = {
            "Phoenix-cv": ["app.py", "requirements.txt", "services/stripe_service.py"],
            "Phoenix-letters": ["app.py", "requirements.txt", "infrastructure/payment/stripe_service.py"]
        }
        
        structure_checks = {}
        
        for project, files in required_structure.items():
            project_path = base_path / project
            structure_checks[project] = {
                "exists": project_path.exists(),
                "files_present": []
            }
            
            if project_path.exists():
                for file_path in files:
                    full_path = project_path / file_path
                    structure_checks[project]["files_present"].append({
                        "file": file_path,
                        "exists": full_path.exists()
                    })
        
        test_result["details"]["structure_checks"] = structure_checks
        
        # Succès si les projets principaux existent
        test_result["success"] = all(
            check["exists"] for check in structure_checks.values()
        )
        
    except Exception as e:
        test_result["details"]["error"] = str(e)
    
    test_result["duration"] = time.time() - start_time
    return test_result


def test_stripe_configuration() -> Dict[str, Any]:
    """Valide la configuration Stripe."""
    test_result = {
        "test_name": "Stripe Configuration Validation",
        "success": False,
        "duration": 0,
        "details": {}
    }
    
    start_time = time.time()
    
    try:
        base_path = Path("/Users/mattvaness/Desktop/IA/phoenix/phoenix-eco")
        
        # Vérification Phoenix CV
        cv_stripe_file = base_path / "Phoenix-cv" / "services" / "stripe_service.py"
        cv_config = {"file_exists": cv_stripe_file.exists()}
        
        if cv_stripe_file.exists():
            content = cv_stripe_file.read_text()
            cv_config.update({
                "has_premium_plan": "premium" in content.lower(),
                "correct_price": "799" in content,  # 7.99€ = 799 centimes
                "has_stripe_import": "import stripe" in content
            })
        
        # Vérification Phoenix Letters
        letters_stripe_file = base_path / "Phoenix-letters" / "infrastructure" / "payment" / "stripe_service.py"
        letters_config = {"file_exists": letters_stripe_file.exists()}
        
        if letters_stripe_file.exists():
            content = letters_stripe_file.read_text()
            letters_config.update({
                "has_premium_plan": "premium" in content.lower(),
                "correct_price": "999" in content,  # 9.99€ = 999 centimes
                "has_stripe_import": "import stripe" in content
            })
        
        test_result["details"] = {
            "phoenix_cv": cv_config,
            "phoenix_letters": letters_config
        }
        
        # Succès si les configurations sont cohérentes
        test_result["success"] = (
            cv_config.get("file_exists", False) and
            letters_config.get("file_exists", False) and
            cv_config.get("correct_price", False) and
            letters_config.get("correct_price", False)
        )
        
    except Exception as e:
        test_result["details"]["error"] = str(e)
    
    test_result["duration"] = time.time() - start_time
    return test_result


def test_price_consistency_in_files() -> Dict[str, Any]:
    """Valide la cohérence des prix dans les fichiers."""
    test_result = {
        "test_name": "Price Consistency in Files",
        "success": False,
        "duration": 0,
        "details": {}
    }
    
    start_time = time.time()
    
    try:
        base_path = Path("/Users/mattvaness/Desktop/IA/phoenix/phoenix-eco")
        
        # Prix attendus
        expected_prices = {
            "phoenix_cv": ["7.99", "799"],  # Prix affiché et centimes
            "phoenix_letters": ["9.99", "999"]
        }
        
        price_checks = {}
        
        # Vérification Phoenix CV
        cv_path = base_path / "Phoenix-cv"
        if cv_path.exists():
            cv_files = list(cv_path.rglob("*.py"))
            cv_content = ""
            for file in cv_files:
                try:
                    cv_content += file.read_text() + "\n"
                except:
                    pass
            
            price_checks["phoenix_cv"] = {
                "files_checked": len(cv_files),
                "has_display_price": "7.99" in cv_content,
                "has_cents_price": "799" in cv_content,
                "no_old_prices": "14.90" not in cv_content and "1490" not in cv_content
            }
        
        # Vérification Phoenix Letters
        letters_path = base_path / "Phoenix-letters"
        if letters_path.exists():
            letters_files = list(letters_path.rglob("*.py"))
            letters_content = ""
            for file in letters_files:
                try:
                    letters_content += file.read_text() + "\n"
                except:
                    pass
            
            price_checks["phoenix_letters"] = {
                "files_checked": len(letters_files),
                "has_display_price": "9.99" in letters_content,
                "has_cents_price": "999" in letters_content,
                "no_old_prices": "9.90" not in letters_content and "990" not in letters_content
            }
        
        test_result["details"]["price_checks"] = price_checks
        
        # Succès si tous les prix sont cohérents
        all_checks_passed = True
        for app, checks in price_checks.items():
            if not all([
                checks.get("has_display_price", False),
                checks.get("has_cents_price", False),
                checks.get("no_old_prices", True)
            ]):
                all_checks_passed = False
        
        test_result["success"] = all_checks_passed
        
    except Exception as e:
        test_result["details"]["error"] = str(e)
    
    test_result["duration"] = time.time() - start_time
    return test_result


def test_deployment_readiness() -> Dict[str, Any]:
    """Teste la préparation au déploiement."""
    test_result = {
        "test_name": "Deployment Readiness",
        "success": False,
        "duration": 0,
        "details": {}
    }
    
    start_time = time.time()
    
    try:
        base_path = Path("/Users/mattvaness/Desktop/IA/phoenix/phoenix-eco")
        
        deployment_checks = {}
        
        for project in ["Phoenix-cv", "Phoenix-letters"]:
            project_path = base_path / project
            
            if project_path.exists():
                checks = {
                    "has_requirements": (project_path / "requirements.txt").exists(),
                    "has_main_app": (project_path / "app.py").exists(),
                    "has_env_example": (project_path / ".env.example").exists(),
                    "has_streamlit_config": (project_path / ".streamlit").exists(),
                }
                
                # Vérification requirements.txt
                req_file = project_path / "requirements.txt"
                if req_file.exists():
                    req_content = req_file.read_text()
                    checks.update({
                        "has_streamlit": "streamlit" in req_content,
                        "has_stripe": "stripe" in req_content
                    })
                
                deployment_checks[project] = checks
        
        test_result["details"]["deployment_checks"] = deployment_checks
        
        # Succès si les éléments essentiels sont présents
        essential_checks = 0
        total_checks = 0
        
        for project, checks in deployment_checks.items():
            for check, result in checks.items():
                total_checks += 1
                if result:
                    essential_checks += 1
        
        success_rate = (essential_checks / total_checks) if total_checks > 0 else 0
        test_result["success"] = success_rate >= 0.8  # 80% des vérifications
        test_result["details"]["success_rate"] = success_rate
        
    except Exception as e:
        test_result["details"]["error"] = str(e)
    
    test_result["duration"] = time.time() - start_time
    return test_result


def test_configuration_files() -> Dict[str, Any]:
    """Teste les fichiers de configuration."""
    test_result = {
        "test_name": "Configuration Files Validation",
        "success": False,
        "duration": 0,
        "details": {}
    }
    
    start_time = time.time()
    
    try:
        base_path = Path("/Users/mattvaness/Desktop/IA/phoenix/phoenix-eco")
        
        config_checks = {}
        
        for project in ["Phoenix-cv", "Phoenix-letters"]:
            project_path = base_path / project
            
            if project_path.exists():
                # Vérification .env.example
                env_example = project_path / ".env.example"
                checks = {"env_example_exists": env_example.exists()}
                
                if env_example.exists():
                    env_content = env_example.read_text()
                    checks.update({
                        "has_stripe_config": "STRIPE" in env_content,
                        "has_gemini_config": "GEMINI" in env_content or "GOOGLE" in env_content,
                        "has_proper_format": "=" in env_content
                    })
                
                # Vérification .streamlit/secrets.toml
                secrets_file = project_path / ".streamlit" / "secrets.toml"
                checks["secrets_template_exists"] = secrets_file.exists()
                
                config_checks[project] = checks
        
        test_result["details"]["config_checks"] = config_checks
        
        # Succès si les configurations de base sont présentes
        config_score = 0
        total_configs = 0
        
        for project, checks in config_checks.items():
            for check, result in checks.items():
                total_configs += 1
                if result:
                    config_score += 1
        
        test_result["success"] = (config_score / total_configs) >= 0.7 if total_configs > 0 else False
        test_result["details"]["config_score"] = config_score / total_configs if total_configs > 0 else 0
        
    except Exception as e:
        test_result["details"]["error"] = str(e)
    
    test_result["duration"] = time.time() - start_time
    return test_result


def run_local_validation() -> Dict[str, Any]:
    """Lance tous les tests de validation locale."""
    print("🔥 PHOENIX ECOSYSTEM - VALIDATION LOCALE")
    print("=" * 60)
    
    start_time = datetime.now()
    results = []
    
    # Test 1: Structure du projet
    print("🏗️ Validation structure projet...")
    structure_result = test_project_structure()
    results.append(structure_result)
    status = "✅" if structure_result["success"] else "❌"
    print(f"   {status} {structure_result['test_name']}: {structure_result['duration']:.3f}s")
    
    # Test 2: Configuration Stripe
    print("💳 Validation configuration Stripe...")
    stripe_result = test_stripe_configuration()
    results.append(stripe_result)
    status = "✅" if stripe_result["success"] else "❌"
    print(f"   {status} {stripe_result['test_name']}: {stripe_result['duration']:.3f}s")
    
    # Test 3: Cohérence des prix
    print("💰 Validation cohérence des prix...")
    price_result = test_price_consistency_in_files()
    results.append(price_result)
    status = "✅" if price_result["success"] else "❌"
    print(f"   {status} {price_result['test_name']}: {price_result['duration']:.3f}s")
    
    # Test 4: Préparation déploiement
    print("🚀 Validation préparation déploiement...")
    deployment_result = test_deployment_readiness()
    results.append(deployment_result)
    status = "✅" if deployment_result["success"] else "❌"
    print(f"   {status} {deployment_result['test_name']}: {deployment_result['duration']:.3f}s")
    
    # Test 5: Fichiers de configuration
    print("⚙️ Validation fichiers de configuration...")
    config_result = test_configuration_files()
    results.append(config_result)
    status = "✅" if config_result["success"] else "❌"
    print(f"   {status} {config_result['test_name']}: {config_result['duration']:.3f}s")
    
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    # Calcul des statistiques
    successful_tests = sum(1 for result in results if result["success"])
    success_rate = (successful_tests / len(results)) * 100
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA VALIDATION LOCALE")
    print("=" * 60)
    print(f"⏱️  Durée totale: {total_duration:.3f}s")
    print(f"📊 Tests exécutés: {len(results)}")
    print(f"✅ Tests réussis: {successful_tests}")
    print(f"❌ Tests échoués: {len(results) - successful_tests}")
    print(f"📈 Taux de réussite: {success_rate:.1f}%")
    
    # Évaluation globale
    overall_success = success_rate >= 80.0
    print(f"\n🎯 STATUT GLOBAL: {'PASS' if overall_success else 'FAIL'}")
    print(f"🚀 Prêt pour déploiement: {'OUI' if overall_success else 'NON'}")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    if overall_success:
        print("   ✅ Configuration locale validée")
        print("   🔧 Configurer les clés API en production")
        print("   🌐 Tester l'accès aux URLs de production")
        print("   📊 Lancer les tests complets après déploiement")
    else:
        print("   🔧 Corriger les problèmes de configuration identifiés")
        print("   📁 Vérifier la structure des fichiers projet")
        print("   💰 Valider la cohérence des prix dans tous les fichiers")
        print("   ⚙️ Compléter les fichiers de configuration manquants")
    
    return {
        "summary": {
            "total_tests": len(results),
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "duration_seconds": total_duration,
            "overall_success": overall_success
        },
        "detailed_results": results,
        "timestamp": datetime.now().isoformat(),
        "recommendations": [
            "Configuration locale validée" if overall_success else "Corriger problèmes identifiés",
            "Configurer clés API production",
            "Tester URLs production après déploiement"
        ]
    }


if __name__ == "__main__":
    # Lancement de la validation locale
    validation_results = run_local_validation()
    
    # Sauvegarde des résultats
    with open("phoenix_local_validation_results.json", "w", encoding="utf-8") as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📁 Résultats sauvegardés: phoenix_local_validation_results.json")
    
    # Code de sortie
    exit_code = 0 if validation_results["summary"]["overall_success"] else 1
    exit(exit_code)