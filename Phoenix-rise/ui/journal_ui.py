"""
Interface de saisie du journal d'humeur quotidien.
"""

import streamlit as st
import pandas as pd
from services.db_service import DBService
from services.ai_coach_service import AICoachService
from typing import List, Dict

def render_journal_ui(user_id: str, db_service: DBService, ai_service: AICoachService):
    """
    Interface complète du journal : saisie + historique.
    
    Args:
        user_id: ID de l'utilisateur connecté
        db_service: Service de base de données
        ai_service: Service de coaching IA
    """
    st.header("🖋️ Mon Suivi Quotidien")

    # Section de saisie
    _render_mood_input_section(user_id, db_service, ai_service)
    
    st.markdown("---")
    
    # Section historique
    _render_mood_history_section(user_id, db_service)

def _render_mood_input_section(user_id: str, db_service: DBService, ai_service: AICoachService):
    """Section de saisie de l'humeur du jour."""
    st.subheader("📊 Comment vous sentez-vous aujourd'hui ?")
    
    with st.container(border=True):
        # Sliders d'évaluation
        col1, col2 = st.columns(2)
        
        with col1:
            mood = st.slider(
                "😊 Humeur générale", 
                min_value=1, max_value=10, value=7,
                help="1 = Très difficile, 10 = Excellent moral"
            )
            
        with col2:
            confidence = st.slider(
                "💪 Confiance en ma reconversion", 
                min_value=1, max_value=10, value=7,
                help="1 = Plein de doutes, 10 = Très confiant"
            )
        
        # Zone de notes
        notes = st.text_area(
            "💭 Notes du jour (optionnel)",
            placeholder="Ex: J'ai postulé à 3 offres, entretien prévu demain, cours terminé...",
            height=100
        )
        
        # Bouton d'enregistrement
        if st.button("✨ Enregistrer et recevoir mon encouragement IA", type="primary"):
            with st.spinner("Phoenix analyse votre journée..."):
                # Sauvegarde en base
                result = db_service.add_mood_entry(user_id, mood, 0, confidence, notes)
                
                if result.get("success"):
                    # Génération de l'encouragement IA
                    encouragement = ai_service.generate_encouragement(mood, confidence, notes)
                    
                    st.success("✅ Journée enregistrée avec succès !")
                    st.info(f"**🦋 Phoenix vous dit :** {encouragement}")
                else:
                    st.error(f"❌ Erreur lors de la sauvegarde : {result.get('error')}")

def _render_mood_history_section(user_id: str, db_service: DBService):
    """Section d'affichage de l'historique."""
    st.subheader("📖 Votre Historique")
    
    mood_entries = db_service.get_mood_entries(user_id)
    
    if not mood_entries:
        st.info("📝 Votre historique apparaîtra ici après votre première saisie.")
        return
    
    # Affichage des entrées récentes
    for entry in mood_entries[:10]:  # Limite à 10 entrées récentes
        entry_date = pd.to_datetime(entry['created_at']).strftime('%d %B %Y à %H:%M')
        
        with st.expander(
            f"**{entry_date}** - Humeur: {entry['mood_score']}/10, Confiance: {entry['confidence_level']}/10"
        ):
            if entry.get('notes'):
                st.write(f"**Notes :** {entry['notes']}")
            else:
                st.write("*Aucune note pour cette journée*")
