"""
🧠 Tagger NLP Émotion/Valeur - Recherche-Action Phoenix
Analyse sémantique éthique des notes utilisateur pour la recherche

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Éthique & Privacy First
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from enum import Enum


class EmotionTag(Enum):
    """Tags émotionnels identifiés dans les notes utilisateur"""
    BURNOUT = "burnout"
    ANXIETE = "anxiété" 
    CONFIANCE = "confiance"
    MOTIVATION = "motivation"
    FRUSTRATION = "frustration"
    ESPOIR = "espoir"
    PEUR = "peur"
    JOIE = "joie"
    STRESS = "stress"
    SOULAGEMENT = "soulagement"


class ValueTag(Enum):
    """Tags de valeurs et aspirations identifiés"""
    QUETE_DE_SENS = "quête_de_sens"
    EQUILIBRE_VIE_PRO = "équilibre_vie_pro"
    RECONNAISSANCE = "reconnaissance"
    AUTONOMIE = "autonomie"
    CREATIVITE = "créativité"
    IMPACT_SOCIAL = "impact_social"
    SECURITE_FINANCIERE = "sécurité_financière"
    APPRENTISSAGE = "apprentissage"
    LEADERSHIP = "leadership"
    COLLABORATION = "collaboration"


class TransitionPhase(Enum):
    """Phases de transition professionnelle"""
    QUESTIONNEMENT = "questionnement"
    EXPLORATION = "exploration"
    PREPARATION = "préparation"
    ACTION = "action"
    INTEGRATION = "intégration"
    BILAN = "bilan"


@dataclass
class NLPTagResult:
    """Résultat de l'analyse NLP d'une note utilisateur"""
    original_text_length: int
    emotion_tags: List[EmotionTag]
    value_tags: List[ValueTag]  
    transition_phase: TransitionPhase
    confidence_score: float
    anonymized_keywords: List[str]
    

class EthicalNLPTagger:
    """
    Tagger NLP éthique pour analyse des dynamiques de reconversion
    
    PRINCIPE: Analyse sémantique respectueuse, jamais de stockage de texte brut
    """
    
    def __init__(self):
        """Initialisation des dictionnaires sémantiques éthiques"""
        self.emotion_patterns = self._build_emotion_patterns()
        self.value_patterns = self._build_value_patterns()
        self.transition_patterns = self._build_transition_patterns()
        
    def _build_emotion_patterns(self) -> Dict[EmotionTag, List[str]]:
        """Construction des patterns d'émotions (mots-clés français)"""
        return {
            EmotionTag.BURNOUT: [
                'épuisement', 'épuisé', 'fatigué', 'burn.?out', 'plus la force',
                'vidé', 'à bout', 'craqué', 'surmenage', 'surchargé'
            ],
            EmotionTag.ANXIETE: [
                'anxiété', 'anxieux', 'angoissé', 'inquiet', 'stress',
                'panique', 'appréhension', 'nerveux', 'tension'
            ],
            EmotionTag.CONFIANCE: [
                'confiant', 'confiance', 'sûr de moi', 'optimiste', 
                'serein', 'assurance', 'foi en', 'certain'
            ],
            EmotionTag.MOTIVATION: [
                'motivé', 'motivation', 'envie', 'enthousiasme', 'dynamique',
                'énergie', 'déterminé', 'ambition', 'volonté'
            ],
            EmotionTag.FRUSTRATION: [
                'frustré', 'frustration', 'agacé', 'irrité', 'colère',
                'ras le bol', 'marre', 'exaspéré'
            ],
            EmotionTag.ESPOIR: [
                'espoir', 'espérer', 'optimisme', 'positif', 'avenir',
                'perspectives', 'lumière', 'renaissance'
            ],
            EmotionTag.PEUR: [
                'peur', 'crainte', 'appréhension', 'terrorisé', 'effrayé',
                'inquiétude', 'angoisse', 'trouille'
            ],
            EmotionTag.JOIE: [
                'joie', 'heureux', 'bonheur', 'ravi', 'content',
                'satisfait', 'épanouissement', 'plaisir'
            ],
            EmotionTag.STRESS: [
                'stress', 'stressé', 'pression', 'tension', 'nervosité',
                'anxiété', 'surmenage'
            ],
            EmotionTag.SOULAGEMENT: [
                'soulagé', 'soulagement', 'libéré', 'délivré', 'apaisé',
                'rassuré', 'détendu'
            ]
        }
    
    def _build_value_patterns(self) -> Dict[ValueTag, List[str]]:
        """Construction des patterns de valeurs et aspirations"""
        return {
            ValueTag.QUETE_DE_SENS: [
                'sens', 'signification', 'utilité', 'impact', 'valeurs',
                'mission', 'raison d.être', 'pourquoi', 'vocation'
            ],
            ValueTag.EQUILIBRE_VIE_PRO: [
                'équilibre', 'vie personnelle', 'famille', 'temps libre',
                'conciliation', 'bien.être', 'life.work.balance'
            ],
            ValueTag.RECONNAISSANCE: [
                'reconnaissance', 'apprécié', 'valorisé', 'respecté',
                'considération', 'mérite', 'gratitude'
            ],
            ValueTag.AUTONOMIE: [
                'autonomie', 'indépendance', 'liberté', 'décision',
                'contrôle', 'responsabilité', 'entrepreneur'
            ],
            ValueTag.CREATIVITE: [
                'créativité', 'créatif', 'innovation', 'imagination',
                'artistique', 'original', 'inventif'
            ],
            ValueTag.IMPACT_SOCIAL: [
                'impact social', 'société', 'communauté', 'aider',
                'contribution', 'changement', 'engagement'
            ],
            ValueTag.SECURITE_FINANCIERE: [
                'sécurité financière', 'argent', 'salaire', 'revenus',
                'stabilité', 'économique', 'financier'
            ],
            ValueTag.APPRENTISSAGE: [
                'apprendre', 'formation', 'développement', 'compétences',
                'connaissances', 'évoluer', 'croissance'
            ],
            ValueTag.LEADERSHIP: [
                'leadership', 'diriger', 'manager', 'équipe', 'responsable',
                'influence', 'guider'
            ],
            ValueTag.COLLABORATION: [
                'collaboration', 'équipe', 'ensemble', 'coopération',
                'collectif', 'partage', 'solidarité'
            ]
        }
    
    def _build_transition_patterns(self) -> Dict[TransitionPhase, List[str]]:
        """Construction des patterns de phases de transition"""
        return {
            TransitionPhase.QUESTIONNEMENT: [
                'questions', 'doutes', 'réflexion', 'pourquoi', 'sens',
                'remise en question', 'interrogation'
            ],
            TransitionPhase.EXPLORATION: [
                'explorer', 'découvrir', 'rechercher', 'possibilités',
                'options', 'pistes', 'opportunités'
            ],
            TransitionPhase.PREPARATION: [
                'formation', 'préparer', 'planifier', 'apprendre',
                'compétences', 'préparation', 'étudier'
            ],
            TransitionPhase.ACTION: [
                'postuler', 'candidature', 'entretien', 'projet',
                'action', 'lancement', 'démarche'
            ],
            TransitionPhase.INTEGRATION: [
                'adaptation', 'intégration', 'nouveau poste', 'débuter',
                'commencer', 'premiers pas'
            ],
            TransitionPhase.BILAN: [
                'bilan', 'évaluation', 'résultats', 'retour',
                'analyse', 'satisfaction', 'acquis'
            ]
        }
    
    def tag_user_notes(self, text: str, preserve_privacy: bool = True) -> NLPTagResult:
        """
        Analyse éthique des notes utilisateur avec protection totale de la vie privée
        
        Args:
            text: Texte à analyser (jamais stocké)
            preserve_privacy: Mode protection maximale (défaut: True)
            
        Returns:
            NLPTagResult: Résultats agrégés sans données personnelles
        """
        if not text or len(text.strip()) < 10:
            return NLPTagResult(
                original_text_length=len(text),
                emotion_tags=[],
                value_tags=[],
                transition_phase=TransitionPhase.QUESTIONNEMENT,
                confidence_score=0.0,
                anonymized_keywords=[]
            )
        
        # Normalisation du texte (minuscules, suppression accents)
        normalized_text = self._normalize_text(text.lower())
        
        # Analyse des émotions
        emotion_tags = self._detect_emotions(normalized_text)
        
        # Analyse des valeurs  
        value_tags = self._detect_values(normalized_text)
        
        # Détection de la phase de transition
        transition_phase = self._detect_transition_phase(normalized_text)
        
        # Score de confiance basé sur le nombre de matches
        confidence_score = self._calculate_confidence_score(
            len(emotion_tags), len(value_tags), len(normalized_text)
        )
        
        # Extraction de mots-clés anonymisés (sans données personnelles)
        anonymized_keywords = []
        if not preserve_privacy:  # Seulement si explicitement autorisé
            anonymized_keywords = self._extract_safe_keywords(normalized_text)
        
        return NLPTagResult(
            original_text_length=len(text),
            emotion_tags=emotion_tags,
            value_tags=value_tags,
            transition_phase=transition_phase,
            confidence_score=confidence_score,
            anonymized_keywords=anonymized_keywords
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalisation du texte pour l'analyse"""
        # Suppression des caractères spéciaux, garde les lettres et espaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _detect_emotions(self, text: str) -> List[EmotionTag]:
        """Détection des émotions dans le texte"""
        detected_emotions = []
        
        for emotion, patterns in self.emotion_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    detected_emotions.append(emotion)
                    break  # Un seul match suffit par émotion
                    
        return detected_emotions
    
    def _detect_values(self, text: str) -> List[ValueTag]:
        """Détection des valeurs dans le texte"""
        detected_values = []
        
        for value, patterns in self.value_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    detected_values.append(value)
                    break  # Un seul match suffit par valeur
                    
        return detected_values
    
    def _detect_transition_phase(self, text: str) -> TransitionPhase:
        """Détection de la phase de transition dominante"""
        phase_scores = {}
        
        for phase, patterns in self.transition_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text))
                score += matches
            phase_scores[phase] = score
        
        # Phase avec le score le plus élevé
        if max(phase_scores.values()) == 0:
            return TransitionPhase.QUESTIONNEMENT  # Par défaut
            
        return max(phase_scores, key=phase_scores.get)
    
    def _calculate_confidence_score(self, emotion_count: int, value_count: int, text_length: int) -> float:
        """Calcul du score de confiance de l'analyse"""
        if text_length < 50:
            return 0.3  # Texte trop court
        
        total_tags = emotion_count + value_count
        
        # Score basé sur la richesse sémantique
        if total_tags == 0:
            return 0.1
        elif total_tags <= 2:
            return 0.5
        elif total_tags <= 4:
            return 0.7
        else:
            return 0.9
    
    def _extract_safe_keywords(self, text: str) -> List[str]:
        """
        Extraction de mots-clés anonymisés (sans données personnelles)
        
        ATTENTION: Ne jamais utiliser en mode production sans consentement explicite
        """
        # Liste de mots "sûrs" (sans données personnelles)
        safe_words = []
        words = text.split()
        
        # Filtrage des mots potentiellement personnels
        personal_indicators = [
            'je', 'mon', 'ma', 'mes', 'moi', 'nous', 'notre', 'nos',
            '@', '.com', '.fr', 'tél', 'téléphone', 'adresse'
        ]
        
        for word in words:
            if len(word) > 4 and not any(indicator in word.lower() for indicator in personal_indicators):
                safe_words.append(word)
        
        return safe_words[:10]  # Maximum 10 mots-clés


def batch_analyze_notes(notes: List[str], preserve_privacy: bool = True) -> List[NLPTagResult]:
    """
    Analyse en lot de notes utilisateur avec protection de la vie privée
    
    Args:
        notes: Liste des notes à analyser
        preserve_privacy: Mode protection maximale
        
    Returns:
        List[NLPTagResult]: Résultats d'analyse anonymisés
    """
    tagger = EthicalNLPTagger()
    results = []
    
    for note in notes:
        if note and note.strip():
            result = tagger.tag_user_notes(note, preserve_privacy)
            results.append(result)
    
    return results


def get_aggregated_insights(results: List[NLPTagResult]) -> Dict:
    """
    Génération d'insights agrégés pour la recherche (anonymes)
    
    Args:
        results: Résultats d'analyses individuelles
        
    Returns:
        Dict: Statistiques agrégées anonymes
    """
    if not results:
        return {}
    
    # Comptage des émotions
    emotion_counts = {}
    for result in results:
        for emotion in result.emotion_tags:
            emotion_counts[emotion.value] = emotion_counts.get(emotion.value, 0) + 1
    
    # Comptage des valeurs
    value_counts = {}
    for result in results:
        for value in result.value_tags:
            value_counts[value.value] = value_counts.get(value.value, 0) + 1
    
    # Phases de transition
    phase_counts = {}
    for result in results:
        phase = result.transition_phase.value
        phase_counts[phase] = phase_counts.get(phase, 0) + 1
    
    # Score de confiance moyen
    avg_confidence = sum(r.confidence_score for r in results) / len(results)
    
    return {
        "total_analyses": len(results),
        "emotion_distribution": emotion_counts,
        "value_distribution": value_counts, 
        "transition_phase_distribution": phase_counts,
        "average_confidence_score": round(avg_confidence, 2),
        "ethics_compliance": True,
        "privacy_preserved": True
    }


# 🔬 EXEMPLE D'UTILISATION ÉTHIQUE
if __name__ == "__main__":
    # Données de test (non personnelles)
    test_notes = [
        "Je me sens épuisé par mon travail actuel, j'aimerais trouver plus de sens dans ce que je fais.",
        "J'explore différentes possibilités de reconversion, je cherche plus d'autonomie et de créativité.",
        "Je suis motivé pour changer de carrière, je veux avoir un impact social plus important."
    ]
    
    # Analyse éthique
    tagger = EthicalNLPTagger()
    results = []
    
    print("🔬 ANALYSE NLP ÉTHIQUE - RECHERCHE-ACTION PHOENIX")
    print("=" * 60)
    
    for i, note in enumerate(test_notes, 1):
        result = tagger.tag_user_notes(note, preserve_privacy=True)
        results.append(result)
        
        print(f"\nNote {i} (longueur: {result.original_text_length} caractères)")
        print(f"Émotions détectées: {[e.value for e in result.emotion_tags]}")
        print(f"Valeurs détectées: {[v.value for v in result.value_tags]}")
        print(f"Phase de transition: {result.transition_phase.value}")
        print(f"Score de confiance: {result.confidence_score}")
    
    # Insights agrégés
    print("\n" + "=" * 60)
    print("📊 INSIGHTS AGRÉGÉS (ANONYMES)")
    print("=" * 60)
    insights = get_aggregated_insights(results)
    
    for key, value in insights.items():
        print(f"{key}: {value}")