"""
DATA FLYWHEEL MVP - Version Basique pour Phoenix Letters
Architecture modulaire compatible avec l'écosystème existant
"""

import hashlib
import json
import logging
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ReconversionPattern:
    """Modèle de données pour un pattern de reconversion"""

    id: str
    source_sector: str  # Secteur d'origine (ex: "santé")
    target_sector: str  # Secteur cible (ex: "tech")
    profile_hash: str  # Hash anonymisé du profil
    prompt_version: str  # Version du prompt utilisée
    success_indicators: Dict  # Métriques de succès
    timestamp: str
    user_tier: str  # FREE, PREMIUM, PREMIUM_PLUS


@dataclass
class PromptPerformance:
    """Performance d'un prompt spécifique"""

    prompt_version: str
    sector_combination: str
    usage_count: int
    success_rate: float
    avg_satisfaction: float
    last_updated: str


class DataFlywheelMVP:
    """
    Data Flywheel MVP - Collecte et analyse des patterns de reconversion
    Compatible avec l'architecture Phoenix Letters existante
    """

    def __init__(self, db_path: str = "data/flywheel.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialise la base de données SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Table des patterns de reconversion
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reconversion_patterns (
                    id TEXT PRIMARY KEY,
                    source_sector TEXT NOT NULL,
                    target_sector TEXT NOT NULL,
                    profile_hash TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    success_indicators TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_tier TEXT NOT NULL
                )
            """
            )

            # Table des performances de prompts
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_performance (
                    prompt_version TEXT NOT NULL,
                    sector_combination TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    success_rate REAL DEFAULT 0.0,
                    avg_satisfaction REAL DEFAULT 0.0,
                    last_updated TEXT NOT NULL,
                    PRIMARY KEY (prompt_version, sector_combination)
                )
            """
            )

            conn.commit()
            conn.close()
            logger.info("Base de données Data Flywheel initialisée")

        except Exception as e:
            logger.error(f"Erreur initialisation DB: {e}")
            raise

    def _extract_sectors(self, cv_text: str, job_offer: str) -> Tuple[str, str]:
        """
        Extrait les secteurs source et cible à partir du CV et de l'offre
        Version simplifiée - à améliorer avec de l'IA plus tard
        """
        # Dictionnaire de mots-clés par secteur (version basique)
        sector_keywords = {
            "santé": ["infirmier", "aide-soignant", "médical", "hôpital", "soins"],
            "tech": ["développeur", "informatique", "cyber", "digital", "tech"],
            "éducation": ["professeur", "enseignant", "école", "formation"],
            "commerce": ["vente", "commercial", "marketing", "client"],
            "finance": ["comptable", "banque", "finance", "audit"],
        }

        source_sector = "autre"
        target_sector = "autre"

        # Analyse simple par mots-clés
        cv_lower = cv_text.lower()
        job_lower = job_offer.lower()

        for sector, keywords in sector_keywords.items():
            if any(keyword in cv_lower for keyword in keywords):
                source_sector = sector
            if any(keyword in job_lower for keyword in keywords):
                target_sector = sector

        return source_sector, target_sector

    def _anonymize_profile(self, cv_text: str) -> str:
        """Crée un hash anonymisé du profil pour tracking"""
        # Extraire les éléments clés sans données personnelles
        key_elements = [
            len(cv_text),
            cv_text.lower().count("expérience"),
            cv_text.lower().count("formation"),
            cv_text.lower().count("compétence"),
        ]

        profile_signature = "_".join(map(str, key_elements))
        # SÉCURITÉ: Utilisation de SHA-256 au lieu de MD5 (vulnérable)
        return hashlib.sha256(profile_signature.encode()).hexdigest()[:16]

    def collect_interaction(
        self,
        cv_text: str,
        job_offer: str,
        generated_letter: str,
        prompt_version: str = "v1.0",
        user_tier: str = "FREE",
        success_indicators: Optional[Dict] = None,
    ) -> str:
        """
        Collecte une interaction utilisateur pour alimenter le flywheel

        Args:
            cv_text: Texte du CV utilisateur
            job_offer: Texte de l'offre d'emploi
            generated_letter: Lettre générée par l'IA
            prompt_version: Version du prompt utilisée
            user_tier: Niveau utilisateur (FREE/PREMIUM/PREMIUM_PLUS)
            success_indicators: Métriques de succès (optionnel)

        Returns:
            ID unique du pattern créé
        """
        try:
            # Extraction des secteurs
            source_sector, target_sector = self._extract_sectors(cv_text, job_offer)

            # Anonymisation du profil
            profile_hash = self._anonymize_profile(cv_text)

            # Indicateurs de succès par défaut
            if success_indicators is None:
                success_indicators = {
                    "letter_length": len(generated_letter),
                    "generation_time": datetime.now().isoformat(),
                    "sectors_detected": f"{source_sector}→{target_sector}",
                }

            # Création du pattern
            pattern = ReconversionPattern(
                id=f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{profile_hash[:8]}",
                source_sector=source_sector,
                target_sector=target_sector,
                profile_hash=profile_hash,
                prompt_version=prompt_version,
                success_indicators=success_indicators,
                timestamp=datetime.now().isoformat(),
                user_tier=user_tier,
            )

            # Sauvegarde en base
            self._save_pattern(pattern)

            # Mise à jour des performances de prompt
            self._update_prompt_performance(pattern)

            logger.info(f"Pattern collecté: {pattern.id}")
            return pattern.id

        except Exception as e:
            logger.error(f"Erreur collecte interaction: {e}")
            return ""

    def _save_pattern(self, pattern: ReconversionPattern):
        """Sauvegarde un pattern en base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO reconversion_patterns
                (id, source_sector, target_sector, profile_hash, prompt_version, 
                 success_indicators, timestamp, user_tier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    pattern.id,
                    pattern.source_sector,
                    pattern.target_sector,
                    pattern.profile_hash,
                    pattern.prompt_version,
                    json.dumps(pattern.success_indicators),
                    pattern.timestamp,
                    pattern.user_tier,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Erreur sauvegarde pattern: {e}")
            raise

    def _update_prompt_performance(self, pattern: ReconversionPattern):
        """Met à jour les performances d'un prompt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            sector_combination = f"{pattern.source_sector}→{pattern.target_sector}"

            # Vérifier si l'entrée existe
            cursor.execute(
                """
                SELECT usage_count, success_rate, avg_satisfaction 
                FROM prompt_performance 
                WHERE prompt_version = ? AND sector_combination = ?
            """,
                (pattern.prompt_version, sector_combination),
            )

            result = cursor.fetchone()

            if result:
                # Mise à jour
                usage_count = result[0] + 1
                # Pour l'instant, on assume un succès basique
                # TODO: Intégrer de vraies métriques de succès
                new_success_rate = (result[1] * result[0] + 1.0) / usage_count

                cursor.execute(
                    """
                    UPDATE prompt_performance 
                    SET usage_count = ?, success_rate = ?, last_updated = ?
                    WHERE prompt_version = ? AND sector_combination = ?
                """,
                    (
                        usage_count,
                        new_success_rate,
                        datetime.now().isoformat(),
                        pattern.prompt_version,
                        sector_combination,
                    ),
                )
            else:
                # Création
                cursor.execute(
                    """
                    INSERT INTO prompt_performance
                    (prompt_version, sector_combination, usage_count, 
                     success_rate, avg_satisfaction, last_updated)
                    VALUES (?, ?, 1, 1.0, 0.0, ?)
                """,
                    (
                        pattern.prompt_version,
                        sector_combination,
                        datetime.now().isoformat(),
                    ),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Erreur update performance: {e}")

    def get_best_prompt_for_profile(
        self, source_sector: str, target_sector: str
    ) -> Optional[str]:
        """
        Retourne le meilleur prompt pour une combinaison de secteurs

        Args:
            source_sector: Secteur d'origine
            target_sector: Secteur cible

        Returns:
            Version du prompt recommandée ou None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            sector_combination = f"{source_sector}→{target_sector}"

            cursor.execute(
                """
                SELECT prompt_version, success_rate, usage_count
                FROM prompt_performance 
                WHERE sector_combination = ?
                ORDER BY success_rate DESC, usage_count DESC
                LIMIT 1
            """,
                (sector_combination,),
            )

            result = cursor.fetchone()
            conn.close()

            if result and result[2] >= 5:  # Au moins 5 utilisations
                logger.info(
                    f"Prompt recommandé pour {sector_combination}: {result[0]} (success: {result[1]:.2f})"
                )
                return result[0]
            else:
                logger.info(
                    f"Pas assez de données pour {sector_combination}, utilisation prompt par défaut"
                )
                return "v1.0"  # Prompt par défaut

        except Exception as e:
            logger.error(f"Erreur récupération meilleur prompt: {e}")
            return "v1.0"

    def get_analytics_dashboard(self) -> Dict:
        """
        Génère un dashboard analytics pour Phoenix

        Returns:
            Dictionnaire avec les métriques clés
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total des patterns
            cursor.execute("SELECT COUNT(*) FROM reconversion_patterns")
            total_patterns = cursor.fetchone()[0]

            # Top 5 des combinaisons de secteurs
            cursor.execute(
                """
                SELECT source_sector, target_sector, COUNT(*) as count
                FROM reconversion_patterns 
                GROUP BY source_sector, target_sector
                ORDER BY count DESC
                LIMIT 5
            """
            )
            top_combinations = cursor.fetchall()

            # Performance moyenne des prompts
            cursor.execute(
                """
                SELECT prompt_version, AVG(success_rate) as avg_success, COUNT(*) as combinations
                FROM prompt_performance
                GROUP BY prompt_version
                ORDER BY avg_success DESC
            """
            )
            prompt_performance = cursor.fetchall()

            # Répartition par tier utilisateur
            cursor.execute(
                """
                SELECT user_tier, COUNT(*) as count
                FROM reconversion_patterns
                GROUP BY user_tier
            """
            )
            user_tiers = cursor.fetchall()

            conn.close()

            return {
                "total_patterns": total_patterns,
                "top_sector_combinations": [
                    {"from": combo[0], "to": combo[1], "count": combo[2]}
                    for combo in top_combinations
                ],
                "prompt_performance": [
                    {
                        "version": perf[0],
                        "avg_success": perf[1],
                        "combinations": perf[2],
                    }
                    for perf in prompt_performance
                ],
                "user_distribution": [
                    {"tier": tier[0], "count": tier[1]} for tier in user_tiers
                ],
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erreur génération analytics: {e}")
            return {"error": str(e)}

    def export_learning_data(self) -> Dict:
        """
        Exporte les données d'apprentissage pour améliorer les prompts
        Données anonymisées et agrégées
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Patterns de réussite par secteur
            cursor.execute(
                """
                SELECT 
                    source_sector,
                    target_sector,
                    prompt_version,
                    COUNT(*) as occurrences,
                    AVG(CASE WHEN json_extract(success_indicators, '$.letter_length') > 500 
                        THEN 1.0 ELSE 0.5 END) as quality_score
                FROM reconversion_patterns
                GROUP BY source_sector, target_sector, prompt_version
                HAVING occurrences >= 3
                ORDER BY quality_score DESC
            """
            )

            learning_patterns = []
            for row in cursor.fetchall():
                learning_patterns.append(
                    {
                        "source_sector": row[0],
                        "target_sector": row[1],
                        "prompt_version": row[2],
                        "sample_size": row[3],
                        "quality_score": row[4],
                    }
                )

            conn.close()

            return {
                "learning_patterns": learning_patterns,
                "recommendations": self._generate_prompt_recommendations(
                    learning_patterns
                ),
                "export_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erreur export learning data: {e}")
            return {"error": str(e)}

    def _generate_prompt_recommendations(self, patterns: List[Dict]) -> List[str]:
        """Génère des recommandations d'amélioration des prompts"""
        recommendations = []

        # Analyse des patterns pour recommandations
        sector_performance = {}
        for pattern in patterns:
            key = f"{pattern['source_sector']}→{pattern['target_sector']}"
            if key not in sector_performance:
                sector_performance[key] = []
            sector_performance[key].append(pattern["quality_score"])

        for combo, scores in sector_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 0.7:
                recommendations.append(
                    f"Améliorer prompt pour {combo} (score: {avg_score:.2f})"
                )
            elif avg_score > 0.9:
                recommendations.append(
                    f"Excellent prompt pour {combo} - utiliser comme modèle"
                )

        return recommendations


# Exemple d'intégration avec Phoenix Letters existant
class PhoenixDataFlywheelIntegration:
    """
    Classe d'intégration avec l'architecture Phoenix Letters existante
    """

    def __init__(self):
        self.flywheel = DataFlywheelMVP()

    def enhance_letter_generation(
        self, cv_text: str, job_offer: str, user_tier: str = "FREE"
    ) -> Tuple[str, str]:
        """
        Améliore la génération de lettre avec le Data Flywheel

        Returns:
            Tuple (prompt_version_recommandée, lettre_générée)
        """
        # Extraire les secteurs
        source_sector, target_sector = self.flywheel._extract_sectors(
            cv_text, job_offer
        )

        # Obtenir le meilleur prompt
        best_prompt = self.flywheel.get_best_prompt_for_profile(
            source_sector, target_sector
        )

        # TODO: Intégrer avec le système de génération existant
        # generated_letter = generate_letter_with_prompt(cv_text, job_offer, best_prompt)
        generated_letter = f"[Lettre générée avec prompt {best_prompt}]"

        # Collecter l'interaction
        self.flywheel.collect_interaction(
            cv_text=cv_text,
            job_offer=job_offer,
            generated_letter=generated_letter,
            prompt_version=best_prompt,
            user_tier=user_tier,
        )

        return best_prompt, generated_letter


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation
    flywheel = DataFlywheelMVP()

    # Simulation d'une interaction
    cv_exemple = (
        "Aide-soignant avec 5 ans d'expérience, passionné par la technologie..."
    )
    job_exemple = "Développeur Junior en cybersécurité, entreprise innovante..."

    pattern_id = flywheel.collect_interaction(
        cv_text=cv_exemple,
        job_offer=job_exemple,
        generated_letter="Lettre de motivation générée...",
        prompt_version="v1.0",
        user_tier="FREE",
    )

    print(f"Pattern créé: {pattern_id}")

    # Analytics
    dashboard = flywheel.get_analytics_dashboard()
    print(f"Analytics: {json.dumps(dashboard, indent=2)}")

    # Recommandation de prompt
    best_prompt = flywheel.get_best_prompt_for_profile("santé", "tech")
    print(f"Meilleur prompt santé→tech: {best_prompt}")
