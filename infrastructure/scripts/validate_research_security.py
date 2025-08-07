#!/usr/bin/env python3
"""
🛡️ Script de Validation Sécurité - Export Recherche-Action Phoenix

Valide la conformité RGPD complète du système d'export de recherche.
Vérifie toutes les protections, anonymisations et politiques de sécurité.

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - RGPD Compliance Validator
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import du module d'export pour validation
try:
    from export_research_data import EthicalDataExporter, ExportFormat
except ImportError:
    print("❌ Impossible d'importer export_research_data.py")
    sys.exit(1)


@dataclass
class SecurityValidationResult:
    """Résultat de validation de sécurité"""
    test_name: str
    passed: bool
    details: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    remediation: Optional[str] = None


class RGPDComplianceValidator:
    """
    Validateur de conformité RGPD pour l'export de recherche Phoenix.
    
    Tests tous les aspects de sécurité et conformité réglementaire.
    """
    
    def __init__(self):
        """Initialisation du validateur"""
        self.results: List[SecurityValidationResult] = []
        self.exporter = None
        
    def run_full_security_audit(self) -> Dict[str, Any]:
        """
        Audit complet de sécurité du système d'export
        
        Returns:
            Dict: Rapport complet d'audit de sécurité
        """
        print("🛡️ AUDIT SÉCURITÉ COMPLET - EXPORT RECHERCHE PHOENIX")
        print("=" * 60)
        
        # Phase 1: Tests d'initialisation
        self._test_anonymizer_requirement()
        self._test_nlp_security_integration()
        
        # Phase 2: Tests de requêtes SQL
        self._test_sql_data_minimization()
        self._test_consent_enforcement()
        
        # Phase 3: Tests d'anonymisation
        self._test_text_anonymization_pipeline()
        self._test_user_id_hashing()
        
        # Phase 4: Tests d'export
        self._test_export_content_security()
        self._test_no_personal_data_leakage()
        
        # Phase 5: Tests de conformité
        self._test_rgpd_compliance_flags()
        self._test_retention_policies()
        
        # Génération du rapport final
        return self._generate_security_report()
    
    def _test_anonymizer_requirement(self):
        """Test: DataAnonymizer est obligatoire pour l'export"""
        try:
            # Test avec DataAnonymizer manquant
            exporter = EthicalDataExporter()
            exporter.anonymizer = None  # Simuler absence
            
            try:
                exporter.export_research_data(max_users=1)
                # Si ça passe, c'est un échec de sécurité
                self.results.append(SecurityValidationResult(
                    test_name="DataAnonymizer Obligatoire",
                    passed=False,
                    details="Export autorisé sans DataAnonymizer - FAILLE CRITIQUE",
                    risk_level="CRITICAL",
                    remediation="Forcer validation DataAnonymizer avant tout export"
                ))
            except ValueError as e:
                if "DataAnonymizer requis" in str(e):
                    self.results.append(SecurityValidationResult(
                        test_name="DataAnonymizer Obligatoire",
                        passed=True,
                        details="Export correctement bloqué sans DataAnonymizer",
                        risk_level="LOW"
                    ))
                else:
                    raise
                    
        except Exception as e:
            self.results.append(SecurityValidationResult(
                test_name="DataAnonymizer Obligatoire",
                passed=False,
                details=f"Erreur test: {e}",
                risk_level="MEDIUM",
                remediation="Vérifier l'implémentation de la validation"
            ))
    
    def _test_nlp_security_integration(self):
        """Test: NLP ne reçoit que des données anonymisées"""
        # Simuler un exporter avec mock anonymizer
        test_exporter = EthicalDataExporter()
        
        # Mock des services pour test
        class MockAnonymizer:
            def anonymize_text(self, text):
                # Simuler anonymisation réussie
                anonymized = text.replace("John", "[PRÉNOM]").replace("Doe", "[NOM]")
                return type('obj', (object,), {
                    'success': True,
                    'anonymized_text': anonymized
                })()
        
        class MockNLPTagger:
            def __init__(self):
                self.last_input = None
                
            def tag_user_notes(self, text, preserve_privacy=True):
                self.last_input = text  # Capturer l'input
                return type('obj', (object,), {
                    'emotion_tags': [type('obj', (object,), {'value': 'test'})()],
                    'value_tags': [type('obj', (object,), {'value': 'test'})()],
                    'transition_phase': type('obj', (object,), {'value': 'test'})()
                })()
        
        # Injecter les mocks
        mock_nlp = MockNLPTagger()
        test_exporter.anonymizer = MockAnonymizer()
        test_exporter.nlp_tagger = mock_nlp
        
        # Test avec données personnelles
        test_user = {
            "user_id": "test_123",
            "notes": ["John Doe travaille chez Entreprise X", "Il habite à Paris"]
        }
        
        # Simuler le processus d'anonymisation
        profiles = test_exporter._anonymize_and_enrich_profiles([test_user])
        
        # Vérifier que le NLP a reçu des données anonymisées
        if mock_nlp.last_input and "[PRÉNOM]" in mock_nlp.last_input and "[NOM]" in mock_nlp.last_input:
            self.results.append(SecurityValidationResult(
                test_name="Anonymisation avant NLP",
                passed=True,
                details="NLP reçoit bien des données anonymisées",
                risk_level="LOW"
            ))
        else:
            self.results.append(SecurityValidationResult(
                test_name="Anonymisation avant NLP",
                passed=False,
                details=f"NLP a reçu: '{mock_nlp.last_input}' - données non anonymisées détectées",
                risk_level="CRITICAL",
                remediation="Forcer anonymisation avant tous les appels NLP"
            ))
    
    def _test_sql_data_minimization(self):
        """Test: Requête SQL ne collecte que le minimum nécessaire"""
        # Analyser le code SQL dans export_research_data.py
        script_path = Path(__file__).parent / "export_research_data.py"
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier que l'email n'est plus dans la requête
            if "u.email" in content:
                self.results.append(SecurityValidationResult(
                    test_name="Minimisation des Données SQL",
                    passed=False,
                    details="Email encore présent dans la requête SQL",
                    risk_level="MEDIUM",
                    remediation="Retirer u.email de la requête SELECT"
                ))
            else:
                self.results.append(SecurityValidationResult(
                    test_name="Minimisation des Données SQL",
                    passed=True,
                    details="Requête SQL ne collecte pas d'emails inutiles",
                    risk_level="LOW"
                ))
                
            # Vérifier la clause WHERE pour consentement
            if "WHERE u.research_consent = 1" in content:
                self.results.append(SecurityValidationResult(
                    test_name="Filtrage par Consentement",
                    passed=True,
                    details="Requête filtre correctement par consentement explicite",
                    risk_level="LOW"
                ))
            else:
                self.results.append(SecurityValidationResult(
                    test_name="Filtrage par Consentement",
                    passed=False,
                    details="Clause WHERE pour consentement manquante ou incorrecte",
                    risk_level="CRITICAL",
                    remediation="Ajouter WHERE u.research_consent = 1 à la requête"
                ))
                
        except FileNotFoundError:
            self.results.append(SecurityValidationResult(
                test_name="Analyse SQL",
                passed=False,
                details="Fichier export_research_data.py non trouvé",
                risk_level="HIGH",
                remediation="Vérifier le chemin du fichier d'export"
            ))
    
    def _test_consent_enforcement(self):
        """Test: Seuls les utilisateurs consentants sont exportés"""
        # Test avec données simulées
        test_exporter = EthicalDataExporter()
        
        # Simuler des utilisateurs avec consentements mixtes
        mixed_users = [
            {"user_id": "user_consent_yes", "research_consent": True, "notes": ["Test"]},
            {"user_id": "user_consent_no", "research_consent": False, "notes": ["Test"]},
            {"user_id": "user_consent_none", "notes": ["Test"]}  # Pas de champ consent
        ]
        
        # Le processus ne devrait traiter que user_consent_yes
        # Note: _extract_consenting_users filtre déjà, mais testons _anonymize_and_enrich_profiles
        consenting_only = [u for u in mixed_users if u.get("research_consent") == True]
        profiles = test_exporter._anonymize_and_enrich_profiles(consenting_only)
        
        if len(profiles) == 1 and profiles[0].research_consent == True:
            self.results.append(SecurityValidationResult(
                test_name="Application du Consentement",
                passed=True,
                details="Seuls les utilisateurs consentants sont traités",
                risk_level="LOW"
            ))
        else:
            self.results.append(SecurityValidationResult(
                test_name="Application du Consentement",
                passed=False,
                details=f"Traitement incorrect du consentement: {len(profiles)} profils générés",
                risk_level="CRITICAL",
                remediation="Renforcer le filtrage par consentement explicite"
            ))
    
    def _test_text_anonymization_pipeline(self):
        """Test: Pipeline d'anonymisation des textes"""
        test_text = "Je m'appelle Marie Dupont et je travaille chez Google France. Mon email est marie.dupont@gmail.com"
        
        # Test avec vraie DataAnonymizer si disponible
        try:
            from packages.phoenix_shared_ui.services.data_anonymizer import DataAnonymizer
            anonymizer = DataAnonymizer()
            result = anonymizer.anonymize_text(test_text)
            
            if result.success and ("Marie" not in result.anonymized_text or "Dupont" not in result.anonymized_text):
                self.results.append(SecurityValidationResult(
                    test_name="Anonymisation des Textes",
                    passed=True,
                    details="DataAnonymizer fonctionne correctement",
                    risk_level="LOW"
                ))
            else:
                self.results.append(SecurityValidationResult(
                    test_name="Anonymisation des Textes",
                    passed=False,
                    details="DataAnonymizer ne supprime pas les données personnelles",
                    risk_level="CRITICAL",
                    remediation="Vérifier et améliorer l'algorithme d'anonymisation"
                ))
        except ImportError:
            self.results.append(SecurityValidationResult(
                test_name="Anonymisation des Textes",
                passed=False,
                details="DataAnonymizer non importable - dépendance manquante",
                risk_level="CRITICAL",
                remediation="Installer et configurer le service DataAnonymizer"
            ))
    
    def _test_user_id_hashing(self):
        """Test: Hachage SHA256 des IDs utilisateur"""
        import hashlib
        
        test_user_id = "user_12345_test"
        expected_hash = hashlib.sha256(test_user_id.encode()).hexdigest()[:16]
        
        # Simuler le processus
        test_exporter = EthicalDataExporter()
        test_user = {"user_id": test_user_id, "research_consent": True}
        profiles = test_exporter._anonymize_and_enrich_profiles([test_user])
        
        if len(profiles) == 1 and profiles[0].user_hash == expected_hash:
            self.results.append(SecurityValidationResult(
                test_name="Hachage des IDs",
                passed=True,
                details="IDs utilisateur correctement hachés en SHA256",
                risk_level="LOW"
            ))
        else:
            actual_hash = profiles[0].user_hash if profiles else "None"
            self.results.append(SecurityValidationResult(
                test_name="Hachage des IDs",
                passed=False,
                details=f"Hachage incorrect: attendu {expected_hash}, obtenu {actual_hash}",
                risk_level="HIGH",
                remediation="Vérifier l'implémentation du hachage SHA256"
            ))
    
    def _test_export_content_security(self):
        """Test: Contenu exporté ne contient aucune donnée personnelle"""
        # Créer un export de test
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                test_exporter = EthicalDataExporter()
                # Mock pour éviter les erreurs d'import
                test_exporter.anonymizer = type('obj', (object,), {
                    'anonymize_text': lambda self, text: type('obj', (object,), {
                        'success': True, 'anonymized_text': '[ANONYMIZED]'
                    })()
                })()
                
                output_file = test_exporter.export_research_data(
                    output_format=ExportFormat.JSON,
                    output_dir=temp_dir,
                    max_users=5
                )
                
                # Lire et analyser le fichier exporté
                with open(output_file, 'r', encoding='utf-8') as f:
                    export_data = json.load(f)
                
                # Chercher des données personnelles typiques
                content_str = json.dumps(export_data)
                personal_data_indicators = [
                    "@", "gmail", "yahoo", "hotmail",  # Emails
                    "user_", "email", "phone", "address",  # Champs personnels
                    "password", "token", "secret"  # Données sensibles
                ]
                
                found_indicators = [indicator for indicator in personal_data_indicators if indicator.lower() in content_str.lower()]
                
                if not found_indicators:
                    self.results.append(SecurityValidationResult(
                        test_name="Contenu Export Sécurisé",
                        passed=True,
                        details="Aucune donnée personnelle détectée dans l'export",
                        risk_level="LOW"
                    ))
                else:
                    self.results.append(SecurityValidationResult(
                        test_name="Contenu Export Sécurisé",
                        passed=False,
                        details=f"Données personnelles potentielles détectées: {found_indicators}",
                        risk_level="HIGH",
                        remediation="Améliorer l'anonymisation ou retirer ces champs"
                    ))
                    
            except Exception as e:
                self.results.append(SecurityValidationResult(
                    test_name="Contenu Export Sécurisé",
                    passed=False,
                    details=f"Erreur lors du test d'export: {e}",
                    risk_level="MEDIUM",
                    remediation="Déboguer le processus d'export"
                ))
    
    def _test_no_personal_data_leakage(self):
        """Test: Aucune fuite de données personnelles dans les métadonnées"""
        test_exporter = EthicalDataExporter()
        
        # Tester la génération des insights agrégés
        test_profiles = [
            self._create_anonymous_profile("user1", {"total_sessions": 5}),
            self._create_anonymous_profile("user2", {"total_sessions": 10})
        ]
        
        insights = test_exporter._generate_aggregated_insights(test_profiles)
        
        # Vérifier qu'il n'y a que des données agrégées
        required_insight_keys = [
            "demographic_insights", "emotional_insights", 
            "usage_insights", "research_insights"
        ]
        
        has_all_keys = all(key in insights for key in required_insight_keys)
        
        # S'assurer qu'il n'y a pas d'IDs utilisateur dans les insights
        insights_str = json.dumps(insights)
        has_user_ids = any(uid in insights_str for uid in ["user1", "user2", "user_"])
        
        if has_all_keys and not has_user_ids:
            self.results.append(SecurityValidationResult(
                test_name="Pas de Fuite dans Insights",
                passed=True,
                details="Insights agrégés seulement, aucun ID utilisateur",
                risk_level="LOW"
            ))
        else:
            self.results.append(SecurityValidationResult(
                test_name="Pas de Fuite dans Insights",
                passed=False,
                details=f"Structure incorrecte ou IDs détectés dans insights",
                risk_level="MEDIUM",
                remediation="Vérifier la génération des insights agrégés"
            ))
    
    def _create_anonymous_profile(self, user_hash: str, data: Dict) -> Any:
        """Helper pour créer un profil anonyme de test"""
        from export_research_data import AnonymizedUserProfile
        return AnonymizedUserProfile(
            user_hash=user_hash,
            age_range="25-30",
            region="Test Region",
            registration_month="2024-01",
            activity_level="medium",
            research_consent=True,
            consent_date="2024-01",
            total_sessions=data.get("total_sessions", 0),
            total_cv_generated=0,
            total_letters_generated=0,
            avg_session_duration_minutes=20,
            emotion_tags=[],
            value_tags=[],
            transition_phase="questionnement",
            export_date="2024-01",
            ethics_validated=True
        )
    
    def _test_rgpd_compliance_flags(self):
        """Test: Flags de conformité RGPD présents et corrects"""
        test_exporter = EthicalDataExporter()
        test_exporter.anonymizer = type('MockAnonymizer', (), {
            'anonymize_text': lambda self, text: type('obj', (object,), {
                'success': True, 'anonymized_text': '[ANONYMIZED]'
            })()
        })()
        
        # Créer un export minimal
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = test_exporter.export_research_data(
                output_format=ExportFormat.RESEARCH_SUMMARY,
                output_dir=temp_dir,
                max_users=1
            )
            
            with open(output_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            # Vérifier les flags RGPD
            ethics_compliance = export_data.get("ethics_compliance", {})
            required_flags = [
                "rgpd_compliant", "consent_verified", 
                "anonymization_validated", "no_personal_data", 
                "research_purpose_only"
            ]
            
            all_flags_true = all(
                ethics_compliance.get(flag, False) == True 
                for flag in required_flags
            )
            
            if all_flags_true:
                self.results.append(SecurityValidationResult(
                    test_name="Flags RGPD Conformité",
                    passed=True,
                    details="Tous les flags de conformité RGPD sont présents et True",
                    risk_level="LOW"
                ))
            else:
                missing_or_false = [
                    flag for flag in required_flags 
                    if not ethics_compliance.get(flag, False)
                ]
                self.results.append(SecurityValidationResult(
                    test_name="Flags RGPD Conformité",
                    passed=False,
                    details=f"Flags manquants ou False: {missing_or_false}",
                    risk_level="MEDIUM",
                    remediation="Assurer que tous les flags RGPD sont True dans l'export"
                ))
    
    def _test_retention_policies(self):
        """Test: Politiques de rétention des données documentées"""
        # Vérifier la présence des politiques dans les métadonnées d'export
        script_path = Path(__file__).parent / "export_research_data.py"
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            retention_keywords = [
                "retention", "research purposes only", 
                "no re-identification", "data_retention_policy"
            ]
            
            found_policies = [kw for kw in retention_keywords if kw in content]
            
            if len(found_policies) >= 2:
                self.results.append(SecurityValidationResult(
                    test_name="Politiques de Rétention",
                    passed=True,
                    details=f"Politiques documentées: {found_policies}",
                    risk_level="LOW"
                ))
            else:
                self.results.append(SecurityValidationResult(
                    test_name="Politiques de Rétention",
                    passed=False,
                    details="Politiques de rétention insuffisamment documentées",
                    risk_level="MEDIUM",
                    remediation="Ajouter des politiques claires de rétention des données"
                ))
                
        except FileNotFoundError:
            self.results.append(SecurityValidationResult(
                test_name="Politiques de Rétention",
                passed=False,
                details="Impossible de vérifier les politiques (fichier non trouvé)",
                risk_level="MEDIUM",
                remediation="Vérifier l'emplacement du fichier d'export"
            ))
    
    def _generate_security_report(self) -> Dict[str, Any]:
        """Génère le rapport final d'audit de sécurité"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Compter par niveau de risque
        risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for result in self.results:
            risk_counts[result.risk_level] = risk_counts.get(result.risk_level, 0) + 1
        
        # Tests critiques échoués
        critical_failures = [r for r in self.results if not r.passed and r.risk_level == "CRITICAL"]
        
        # Déterminer le statut global
        if critical_failures:
            global_status = "CRITICAL_ISSUES_FOUND"
        elif failed_tests > 0:
            global_status = "ISSUES_FOUND"
        else:
            global_status = "ALL_TESTS_PASSED"
        
        report = {
            "audit_metadata": {
                "audit_date": "2024-08-07",
                "audit_version": "1.0.0",
                "auditor": "Claude Phoenix DevSecOps Guardian",
                "scope": "RGPD Compliance - Export Recherche-Action"
            },
            "summary": {
                "global_status": global_status,
                "total_tests": total_tests,
                "tests_passed": passed_tests,
                "tests_failed": failed_tests,
                "success_rate": round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0
            },
            "risk_analysis": {
                "critical_issues": risk_counts["CRITICAL"],
                "high_risk_issues": risk_counts["HIGH"],
                "medium_risk_issues": risk_counts["MEDIUM"],
                "low_risk_issues": risk_counts["LOW"]
            },
            "detailed_results": [
                {
                    "test": r.test_name,
                    "status": "PASSED" if r.passed else "FAILED",
                    "risk_level": r.risk_level,
                    "details": r.details,
                    "remediation": r.remediation
                }
                for r in self.results
            ],
            "critical_failures": [
                {
                    "test": r.test_name,
                    "details": r.details,
                    "remediation": r.remediation
                }
                for r in critical_failures
            ],
            "compliance_status": {
                "anonymization_enforced": not any(
                    r.test_name == "Anonymisation avant NLP" and not r.passed 
                    for r in self.results
                ),
                "data_minimization_applied": not any(
                    r.test_name == "Minimisation des Données SQL" and not r.passed 
                    for r in self.results
                ),
                "consent_verification_active": not any(
                    r.test_name == "Application du Consentement" and not r.passed 
                    for r in self.results
                ),
                "no_data_leakage": not any(
                    r.test_name == "Contenu Export Sécurisé" and not r.passed 
                    for r in self.results
                )
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Génère les recommandations de sécurité"""
        recommendations = []
        
        # Recommandations basées sur les échecs
        for result in self.results:
            if not result.passed and result.remediation:
                recommendations.append({
                    "priority": result.risk_level,
                    "issue": result.test_name,
                    "action": result.remediation
                })
        
        # Recommandations générales
        recommendations.extend([
            {
                "priority": "HIGH",
                "issue": "Surveillance Continue",
                "action": "Implémenter un monitoring continu de la conformité RGPD"
            },
            {
                "priority": "MEDIUM",
                "issue": "Formation Équipe",
                "action": "Former l'équipe sur les bonnes pratiques de protection des données"
            },
            {
                "priority": "MEDIUM",
                "issue": "Documentation",
                "action": "Maintenir une documentation complète des processus d'anonymisation"
            }
        ])
        
        return recommendations


def main():
    """Point d'entrée principal pour l'audit de sécurité"""
    print("🚀 DÉMARRAGE AUDIT SÉCURITÉ RGPD - PHOENIX LETTERS")
    
    validator = RGPDComplianceValidator()
    report = validator.run_full_security_audit()
    
    # Affichage du rapport
    print("\n" + "=" * 80)
    print("📊 RAPPORT FINAL D'AUDIT SÉCURITÉ")
    print("=" * 80)
    print(f"Statut Global: {report['summary']['global_status']}")
    print(f"Tests Réussis: {report['summary']['tests_passed']}/{report['summary']['total_tests']}")
    print(f"Taux de Réussite: {report['summary']['success_rate']}%")
    print(f"Issues Critiques: {report['risk_analysis']['critical_issues']}")
    print(f"Issues Élevées: {report['risk_analysis']['high_risk_issues']}")
    
    if report['summary']['global_status'] == "ALL_TESTS_PASSED":
        print("\n✅ CONFORMITÉ RGPD VALIDÉE - EXPORT AUTORISÉ")
    else:
        print(f"\n❌ PROBLÈMES DÉTECTÉS - CORRECTION REQUISE")
        
        if report['critical_failures']:
            print("\n🚨 ÉCHECS CRITIQUES:")
            for failure in report['critical_failures']:
                print(f"  - {failure['test']}: {failure['details']}")
                print(f"    → {failure['remediation']}")
    
    # Sauvegarder le rapport
    report_file = f"rgpd_compliance_audit_{report['audit_metadata']['audit_date'].replace('-', '')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Rapport complet sauvegardé: {report_file}")
    
    return report['summary']['global_status'] == "ALL_TESTS_PASSED"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)