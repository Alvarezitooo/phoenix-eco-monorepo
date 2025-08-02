"""
🔗 Phoenix Ecosystem - Tests Intégrations API
Validation complète des APIs externes (France Travail, Gemini)

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Production Testing Suite
"""

import pytest
import requests
import time
import json
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class APITestConfig:
    """Configuration des tests API."""
    france_travail_base_url: str = "https://api.francetravail.io"
    gemini_model: str = "gemini-1.5-flash"
    timeout: int = 30
    retry_attempts: int = 3
    test_queries: List[str] = None
    
    def __post_init__(self):
        self.test_queries = [
            "Développeur Python reconversion",
            "Data Analyst transition professionnelle",
            "Chef de projet IT changement carrière"
        ]


class FranceTravailAPITester:
    """
    Testeur pour l'API France Travail.
    Valide la récupération d'offres d'emploi et les formats de données.
    """
    
    def __init__(self, config: APITestConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout
        self.access_token = None
        
        # Headers par défaut
        self.session.headers.update({
            'User-Agent': 'Phoenix-Letters/1.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def authenticate(self, client_id: str, client_secret: str) -> Dict[str, Any]:
        """
        Authentification OAuth2 avec France Travail API.
        
        Args:
            client_id: ID client France Travail
            client_secret: Secret client France Travail
            
        Returns:
            Résultat de l'authentification
        """
        auth_result = {
            "step_name": "France Travail Authentication",
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            # Endpoint d'authentification
            auth_url = f"{self.config.france_travail_base_url}/connexion/oauth2/access_token"
            
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "api_offresdemploiv2 o2dsoffre"
            }
            
            response = self.session.post(
                auth_url,
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            end_time = time.time()
            auth_result["duration"] = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                
                # Mise à jour des headers avec le token
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                auth_result["success"] = bool(self.access_token)
                auth_result["details"] = {
                    "token_type": token_data.get("token_type"),
                    "expires_in": token_data.get("expires_in"),
                    "scope": token_data.get("scope")
                }
            else:
                auth_result["details"] = {
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            auth_result["details"]["error"] = str(e)
            logger.error(f"Erreur authentification France Travail: {e}")
            
        return auth_result

    def test_job_search(self, search_query: str, location: str = "France") -> Dict[str, Any]:
        """
        Test de recherche d'offres d'emploi.
        
        Args:
            search_query: Terme de recherche
            location: Localisation
            
        Returns:
            Résultat du test de recherche
        """
        search_result = {
            "step_name": f"Job Search - {search_query}",
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            # Endpoint de recherche d'offres
            search_url = f"{self.config.france_travail_base_url}/partenaire/offresdemploi/v2/offres/search"
            
            params = {
                "motsCles": search_query,
                "commune": location,
                "distance": 50,
                "sort": 1,  # Tri par pertinence
                "range": "0-19"  # 20 premiers résultats
            }
            
            response = self.session.get(search_url, params=params)
            
            end_time = time.time()
            search_result["duration"] = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                data = response.json()
                
                search_result["details"] = {
                    "total_results": data.get("resultats", {}).get("total", 0),
                    "returned_results": len(data.get("resultats", {}).get("offre", [])),
                    "response_time": search_result["duration"],
                    "sample_jobs": []
                }
                
                # Extraction d'échantillons d'offres
                offers = data.get("resultats", {}).get("offre", [])
                for offer in offers[:3]:  # 3 premiers échantillons
                    search_result["details"]["sample_jobs"].append({
                        "id": offer.get("id"),
                        "title": offer.get("intitule"),
                        "company": offer.get("entreprise", {}).get("nom"),
                        "location": offer.get("lieuTravail", {}).get("libelle"),
                        "contract_type": offer.get("typeContrat")
                    })
                
                search_result["success"] = len(offers) > 0
                
            else:
                search_result["details"] = {
                    "status_code": response.status_code,
                    "error": response.text[:500]  # Premiers 500 caractères de l'erreur
                }
                
        except Exception as e:
            search_result["details"]["error"] = str(e)
            logger.error(f"Erreur recherche France Travail: {e}")
            
        return search_result

    def test_job_details(self, job_id: str) -> Dict[str, Any]:
        """
        Test de récupération des détails d'une offre.
        
        Args:
            job_id: ID de l'offre d'emploi
            
        Returns:
            Résultat du test de détails
        """
        details_result = {
            "step_name": f"Job Details - {job_id}",
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            details_url = f"{self.config.france_travail_base_url}/partenaire/offresdemploi/v2/offres/{job_id}"
            
            response = self.session.get(details_url)
            
            end_time = time.time()
            details_result["duration"] = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                job_data = response.json()
                
                details_result["details"] = {
                    "job_id": job_id,
                    "title": job_data.get("intitule"),
                    "description_length": len(job_data.get("description", "")),
                    "has_requirements": bool(job_data.get("competences")),
                    "has_salary_info": bool(job_data.get("salaire")),
                    "response_time": details_result["duration"]
                }
                
                details_result["success"] = bool(job_data.get("intitule"))
                
            else:
                details_result["details"] = {
                    "status_code": response.status_code,
                    "error": response.text[:500]
                }
                
        except Exception as e:
            details_result["details"]["error"] = str(e)
            
        return details_result

    def test_api_limits(self) -> Dict[str, Any]:
        """
        Test des limites de l'API (rate limiting).
        
        Returns:
            Résultat du test de limites
        """
        limits_result = {
            "step_name": "API Rate Limits Test",
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            # Test de requêtes multiples rapides
            request_count = 10
            successful_requests = 0
            rate_limited_requests = 0
            
            for i in range(request_count):
                try:
                    response = self.session.get(
                        f"{self.config.france_travail_base_url}/partenaire/offresdemploi/v2/offres/search",
                        params={"motsCles": "test", "range": "0-4"}
                    )
                    
                    if response.status_code == 200:
                        successful_requests += 1
                    elif response.status_code == 429:  # Too Many Requests
                        rate_limited_requests += 1
                        
                    time.sleep(0.1)  # Pause courte entre requêtes
                    
                except Exception:
                    pass
            
            end_time = time.time()
            limits_result["duration"] = round(end_time - start_time, 2)
            
            limits_result["details"] = {
                "total_requests": request_count,
                "successful_requests": successful_requests,
                "rate_limited_requests": rate_limited_requests,
                "success_rate": (successful_requests / request_count) * 100
            }
            
            limits_result["success"] = successful_requests > 0
            
        except Exception as e:
            limits_result["details"]["error"] = str(e)
            
        return limits_result


class GeminiAPITester:
    """
    Testeur pour l'API Google Gemini.
    Valide la génération de contenu et les performances.
    """
    
    def __init__(self, config: APITestConfig):
        self.config = config
        self.model = None
        
    def initialize(self, api_key: str) -> Dict[str, Any]:
        """
        Initialisation de l'API Gemini.
        
        Args:
            api_key: Clé API Google Gemini
            
        Returns:
            Résultat de l'initialisation
        """
        init_result = {
            "step_name": "Gemini API Initialization",
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.config.gemini_model)
            
            # Test de base
            test_response = self.model.generate_content("Test de connexion API")
            
            end_time = time.time()
            init_result["duration"] = round(end_time - start_time, 2)
            
            if test_response and test_response.text:
                init_result["success"] = True
                init_result["details"] = {
                    "model_name": self.config.gemini_model,
                    "response_length": len(test_response.text),
                    "response_time": init_result["duration"]
                }
            else:
                init_result["details"]["error"] = "Pas de réponse du modèle"
                
        except Exception as e:
            init_result["details"]["error"] = str(e)
            logger.error(f"Erreur initialisation Gemini: {e}")
            
        return init_result

    def test_letter_generation(self, user_profile: Dict, job_offer: Dict) -> Dict[str, Any]:
        """
        Test de génération de lettre de motivation.
        
        Args:
            user_profile: Profil utilisateur simulé
            job_offer: Offre d'emploi simulée
            
        Returns:
            Résultat du test de génération
        """
        generation_result = {
            "step_name": "Letter Generation Test",
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            # Prompt de test pour génération de lettre
            prompt = f"""
            Génère une lettre de motivation professionnelle pour une reconversion.
            
            Profil candidat:
            - Nom: {user_profile.get('name', 'Test User')}
            - Expérience actuelle: {user_profile.get('current_role', 'Rôle actuel')}
            - Objectif: {user_profile.get('target_role', 'Rôle cible')}
            
            Offre d'emploi:
            - Poste: {job_offer.get('title', 'Titre du poste')}
            - Entreprise: {job_offer.get('company', 'Entreprise test')}
            - Compétences requises: {job_offer.get('skills', 'Compétences')}
            
            Génère une lettre personnalisée et convaincante.
            """
            
            response = self.model.generate_content(prompt)
            
            end_time = time.time()
            generation_result["duration"] = round(end_time - start_time, 2)
            
            if response and response.text:
                letter_text = response.text
                
                generation_result["details"] = {
                    "letter_length": len(letter_text),
                    "word_count": len(letter_text.split()),
                    "has_personalization": any(term in letter_text.lower() for term in [
                        user_profile.get('name', '').lower(),
                        job_offer.get('company', '').lower(),
                        job_offer.get('title', '').lower()
                    ]),
                    "response_time": generation_result["duration"],
                    "letter_preview": letter_text[:200] + "..." if len(letter_text) > 200 else letter_text
                }
                
                # Critères de qualité
                quality_checks = {
                    "minimum_length": len(letter_text) > 500,
                    "has_greeting": any(greeting in letter_text.lower() for greeting in ["madame", "monsieur", "bonjour"]),
                    "has_closing": any(closing in letter_text.lower() for closing in ["cordialement", "salutations", "respectueusement"]),
                    "mentions_company": job_offer.get('company', '').lower() in letter_text.lower(),
                    "mentions_position": job_offer.get('title', '').lower() in letter_text.lower()
                }
                
                generation_result["details"]["quality_checks"] = quality_checks
                generation_result["success"] = all(quality_checks.values())
                
            else:
                generation_result["details"]["error"] = "Pas de contenu généré"
                
        except Exception as e:
            generation_result["details"]["error"] = str(e)
            logger.error(f"Erreur génération Gemini: {e}")
            
        return generation_result

    def test_cv_analysis(self, cv_content: str) -> Dict[str, Any]:
        """
        Test d'analyse de CV.
        
        Args:
            cv_content: Contenu du CV à analyser
            
        Returns:
            Résultat du test d'analyse
        """
        analysis_result = {
            "step_name": "CV Analysis Test",
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            analysis_prompt = f"""
            Analyse ce CV et fournis un feedback structuré pour une reconversion professionnelle:
            
            {cv_content}
            
            Fournis:
            1. Points forts identifiés
            2. Compétences transférables
            3. Domaines à améliorer
            4. Suggestions pour la reconversion
            
            Format ta réponse en JSON avec les clés: strengths, transferable_skills, improvements, recommendations
            """
            
            response = self.model.generate_content(analysis_prompt)
            
            end_time = time.time()
            analysis_result["duration"] = round(end_time - start_time, 2)
            
            if response and response.text:
                analysis_text = response.text
                
                # Tentative de parsing JSON
                try:
                    # Extraction du JSON si présent
                    json_start = analysis_text.find('{')
                    json_end = analysis_text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_content = analysis_text[json_start:json_end]
                        parsed_analysis = json.loads(json_content)
                        
                        analysis_result["details"] = {
                            "analysis_length": len(analysis_text),
                            "structured_output": True,
                            "parsed_sections": list(parsed_analysis.keys()),
                            "response_time": analysis_result["duration"]
                        }
                        
                        analysis_result["success"] = len(parsed_analysis) >= 3
                    else:
                        # Pas de JSON mais contenu présent
                        analysis_result["details"] = {
                            "analysis_length": len(analysis_text),
                            "structured_output": False,
                            "has_content": True,
                            "response_time": analysis_result["duration"]
                        }
                        
                        analysis_result["success"] = len(analysis_text) > 200
                        
                except json.JSONDecodeError:
                    analysis_result["details"] = {
                        "analysis_length": len(analysis_text),
                        "json_parsing_error": True,
                        "has_content": True,
                        "response_time": analysis_result["duration"]
                    }
                    
                    analysis_result["success"] = len(analysis_text) > 200
            else:
                analysis_result["details"]["error"] = "Pas d'analyse générée"
                
        except Exception as e:
            analysis_result["details"]["error"] = str(e)
            
        return analysis_result

    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """
        Test de benchmarks de performance.
        
        Returns:
            Résultat des tests de performance
        """
        perf_result = {
            "step_name": "Performance Benchmarks",
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            # Tests de différentes tailles de contenu
            test_prompts = {
                "short": "Écris une phrase sur la reconversion professionnelle.",
                "medium": "Génère un paragraphe de 100 mots sur les avantages d'une reconversion en tech.",
                "long": "Rédige un article de 300 mots sur les étapes clés d'une reconversion professionnelle réussie."
            }
            
            performance_metrics = {}
            
            for test_type, prompt in test_prompts.items():
                test_start = time.time()
                
                try:
                    response = self.model.generate_content(prompt)
                    test_end = time.time()
                    
                    if response and response.text:
                        performance_metrics[test_type] = {
                            "response_time": round(test_end - test_start, 2),
                            "content_length": len(response.text),
                            "words_per_second": len(response.text.split()) / (test_end - test_start),
                            "success": True
                        }
                    else:
                        performance_metrics[test_type] = {
                            "response_time": round(test_end - test_start, 2),
                            "success": False,
                            "error": "No content generated"
                        }
                        
                except Exception as e:
                    performance_metrics[test_type] = {
                        "success": False,
                        "error": str(e)
                    }
            
            end_time = time.time()
            perf_result["duration"] = round(end_time - start_time, 2)
            
            perf_result["details"] = {
                "total_test_time": perf_result["duration"],
                "individual_tests": performance_metrics,
                "average_response_time": sum(
                    metric.get("response_time", 0) 
                    for metric in performance_metrics.values()
                ) / len(performance_metrics)
            }
            
            perf_result["success"] = all(
                metric.get("success", False) 
                for metric in performance_metrics.values()
            )
            
        except Exception as e:
            perf_result["details"]["error"] = str(e)
            
        return perf_result


def run_comprehensive_api_tests(
    france_travail_client_id: str = None,
    france_travail_client_secret: str = None,
    gemini_api_key: str = None
) -> Dict[str, Any]:
    """
    Lance la suite complète de tests API.
    
    Args:
        france_travail_client_id: ID client France Travail
        france_travail_client_secret: Secret client France Travail
        gemini_api_key: Clé API Gemini
        
    Returns:
        Résultats détaillés des tests
    """
    config = APITestConfig()
    results = []
    
    print("🔗 Lancement des tests d'intégrations API...")
    
    # Tests France Travail API
    if france_travail_client_id and france_travail_client_secret:
        print("🏢 Test France Travail API...")
        
        ft_tester = FranceTravailAPITester(config)
        
        # Authentification
        auth_result = ft_tester.authenticate(france_travail_client_id, france_travail_client_secret)
        results.append({
            "api": "France Travail",
            "test_type": "Authentication",
            "result": auth_result
        })
        
        if auth_result["success"]:
            # Test de recherche
            for query in config.test_queries:
                search_result = ft_tester.test_job_search(query)
                results.append({
                    "api": "France Travail",
                    "test_type": "Job Search",
                    "query": query,
                    "result": search_result
                })
            
            # Test des limites API
            limits_result = ft_tester.test_api_limits()
            results.append({
                "api": "France Travail",
                "test_type": "Rate Limits",
                "result": limits_result
            })
    else:
        print("⚠️ Identifiants France Travail non fournis - Tests ignorés")
    
    # Tests Gemini API
    if gemini_api_key:
        print("🤖 Test Gemini API...")
        
        gemini_tester = GeminiAPITester(config)
        
        # Initialisation
        init_result = gemini_tester.initialize(gemini_api_key)
        results.append({
            "api": "Gemini",
            "test_type": "Initialization",
            "result": init_result
        })
        
        if init_result["success"]:
            # Test de génération de lettre
            test_profile = {
                "name": "Marie Dupont",
                "current_role": "Comptable",
                "target_role": "Data Analyst"
            }
            
            test_job = {
                "title": "Data Analyst Junior",
                "company": "TechCorp",
                "skills": "Python, SQL, Excel"
            }
            
            letter_result = gemini_tester.test_letter_generation(test_profile, test_job)
            results.append({
                "api": "Gemini",
                "test_type": "Letter Generation",
                "result": letter_result
            })
            
            # Test d'analyse CV
            sample_cv = """
            Marie Dupont
            Comptable Senior - 5 ans d'expérience
            
            Expérience:
            - Gestion comptabilité générale
            - Analyse financière
            - Reporting mensuel
            - Maîtrise Excel avancé
            
            Formation:
            - Master Comptabilité-Finance
            - Formation Python (autodidacte)
            """
            
            cv_analysis_result = gemini_tester.test_cv_analysis(sample_cv)
            results.append({
                "api": "Gemini",
                "test_type": "CV Analysis",
                "result": cv_analysis_result
            })
            
            # Test de performance
            perf_result = gemini_tester.test_performance_benchmarks()
            results.append({
                "api": "Gemini",
                "test_type": "Performance Benchmarks",
                "result": perf_result
            })
    else:
        print("⚠️ Clé API Gemini non fournie - Tests ignorés")
    
    # Génération du résumé
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["result"]["success"])
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
        "apis_tested": list(set(r["api"] for r in results))
    }
    
    return {
        "results": results,
        "summary": summary
    }


if __name__ == "__main__":
    # Configuration des clés (remplacer par vraies valeurs)
    FT_CLIENT_ID = "your_france_travail_client_id"
    FT_CLIENT_SECRET = "your_france_travail_client_secret"
    GEMINI_API_KEY = "your_gemini_api_key"
    
    # Exécution des tests
    test_results = run_comprehensive_api_tests(
        france_travail_client_id=FT_CLIENT_ID if FT_CLIENT_ID != "your_france_travail_client_id" else None,
        france_travail_client_secret=FT_CLIENT_SECRET if FT_CLIENT_SECRET != "your_france_travail_client_secret" else None,
        gemini_api_key=GEMINI_API_KEY if GEMINI_API_KEY != "your_gemini_api_key" else None
    )
    
    # Affichage des résultats
    print(f"\n✅ Tests API terminés:")
    print(f"📊 {test_results['summary']['passed_tests']}/{test_results['summary']['total_tests']} tests réussis")
    print(f"📈 Taux de réussite: {test_results['summary']['success_rate']:.1f}%")
    print(f"🔗 APIs testées: {', '.join(test_results['summary']['apis_tested'])}")
    
    # Sauvegarde des résultats
    with open("phoenix_api_tests_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print("📁 Résultats sauvegardés: phoenix_api_tests_results.json")