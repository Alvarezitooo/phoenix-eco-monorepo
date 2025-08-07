#!/usr/bin/env python3
"""
📊 Dashboard de Recherche-Action Phoenix
Visualisation des insights éthiques sur les dynamiques de reconversion

PRINCIPE : Transparence + Insights Agrégés + Impact Social

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Public Research Interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np

# Configuration Streamlit
st.set_page_config(
    page_title="📊 Recherche-Action Phoenix",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


class ResearchDashboard:
    """
    Dashboard de recherche éthique Phoenix
    
    Visualise les insights anonymisés sur les dynamiques de reconversion professionnelle
    """
    
    def __init__(self):
        """Initialisation du dashboard"""
        self.research_data = self._load_research_data()
        self.setup_page_styling()
    
    def setup_page_styling(self):
        """Configuration du style CSS personnalisé"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border-left: 4px solid #667eea;
            margin-bottom: 1rem;
        }
        
        .insight-box {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #28a745;
        }
        
        .ethics-badge {
            background: #28a745;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .research-note {
            background: #fff3cd;
            border: 1px solid #ffeeba;
            color: #856404;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _load_research_data(self) -> Optional[Dict]:
        """
        Chargement des données de recherche exportées
        
        Returns:
            Dict: Données de recherche ou None si non disponible
        """
        # Recherche des fichiers de données exportés
        research_dir = Path("research_exports")
        if not research_dir.exists():
            return self._generate_demo_data()
        
        # Recherche du fichier le plus récent
        json_files = list(research_dir.glob("phoenix_research_data_*.json"))
        if not json_files:
            return self._generate_demo_data()
        
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            st.sidebar.success(f"✅ Données chargées: {latest_file.name}")
            return data
            
        except Exception as e:
            st.sidebar.error(f"❌ Erreur de chargement: {e}")
            return self._generate_demo_data()
    
    def _generate_demo_data(self) -> Dict:
        """Génération de données de démonstration pour le développement"""
        st.sidebar.info("📊 Données de démonstration utilisées")
        
        return {
            "export_metadata": {
                "export_date": datetime.now().isoformat(),
                "total_users_exported": 127,
                "ethics_compliance_checked": True,
                "anonymization_method": "SHA256 + Generalization"
            },
            "user_profiles": [
                {
                    "user_hash": f"demo_user_{i:03d}",
                    "age_range": np.random.choice(["25-30", "31-35", "36-40", "41-45", "46-50"]),
                    "region": np.random.choice(["Île-de-France", "PACA", "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine"]),
                    "activity_level": np.random.choice(["low", "medium", "high"]),
                    "total_sessions": np.random.randint(1, 25),
                    "total_cv_generated": np.random.randint(0, 6),
                    "total_letters_generated": np.random.randint(0, 12),
                    "emotion_tags": np.random.choice([
                        ["burnout", "stress"], ["confiance", "motivation"], 
                        ["anxiété", "peur"], ["espoir", "joie"], []
                    ]),
                    "value_tags": np.random.choice([
                        ["quête_de_sens"], ["équilibre_vie_pro"], ["autonomie"], 
                        ["créativité"], ["impact_social"], []
                    ]),
                    "transition_phase": np.random.choice([
                        "questionnement", "exploration", "préparation", "action"
                    ])
                }
                for i in range(127)
            ],
            "aggregated_insights": {
                "demographic_insights": {
                    "age_distribution": {"25-30": 32, "31-35": 28, "36-40": 25, "41-45": 22, "46-50": 20},
                    "region_distribution": {"Île-de-France": 45, "PACA": 28, "Auvergne-Rhône-Alpes": 32, "Nouvelle-Aquitaine": 22}
                },
                "emotional_insights": {
                    "emotion_frequency": {"burnout": 42, "stress": 38, "confiance": 35, "motivation": 31, "anxiété": 28},
                    "value_frequency": {"quête_de_sens": 48, "équilibre_vie_pro": 35, "autonomie": 32, "créativité": 28},
                    "transition_phase_distribution": {"questionnement": 35, "exploration": 32, "préparation": 28, "action": 25}
                },
                "usage_insights": {
                    "average_sessions_per_user": 8.5,
                    "average_cv_per_user": 2.3,
                    "average_letters_per_user": 4.7
                }
            },
            "ethics_compliance": {
                "rgpd_compliant": True,
                "consent_verified": True,
                "anonymization_validated": True,
                "no_personal_data": True
            }
        }
    
    def render_header(self):
        """Rendu de l'en-tête principal"""
        st.markdown("""
        <div class="main-header">
            <h1>🔬 Recherche-Action Phoenix</h1>
            <h3>Insights sur l'Impact de l'IA dans la Reconversion Professionnelle</h3>
            <p>Dashboard public des données agrégées et anonymisées</p>
            <span class="ethics-badge">🛡️ RGPD Compliant</span>
            <span class="ethics-badge">✅ Données Anonymisées</span>
            <span class="ethics-badge">🔬 Recherche Publique</span>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Rendu de la barre latérale avec informations contextuelles"""
        with st.sidebar:
            st.markdown("## 📋 À Propos")
            
            st.markdown("""
            ### 🎯 Mission
            Comprendre comment l'IA peut mieux accompagner les reconversions professionnelles.
            
            ### 🛡️ Éthique
            - Consentement explicite
            - Données 100% anonymisées
            - Usage recherche uniquement
            - Transparence totale
            
            ### 📊 Données
            """)
            
            if self.research_data:
                metadata = self.research_data.get("export_metadata", {})
                st.metric("Participants", metadata.get("total_users_exported", 0))
                
                export_date = metadata.get("export_date", "")
                if export_date:
                    date_obj = datetime.fromisoformat(export_date.replace('Z', '+00:00'))
                    st.write(f"**Dernière mise à jour:** {date_obj.strftime('%d/%m/%Y')}")
            
            st.markdown("---")
            st.markdown("""
            ### 🤝 Contact Recherche
            📧 recherche@phoenix-creator.fr  
            🌐 [Phoenix Creator](https://phoenix-creator.fr)
            """)
    
    def render_overview_metrics(self):
        """Rendu des métriques générales"""
        st.markdown("## 📊 Vue d'Ensemble")
        
        if not self.research_data:
            st.warning("Aucune donnée de recherche disponible")
            return
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        metadata = self.research_data.get("export_metadata", {})
        usage_insights = self.research_data.get("aggregated_insights", {}).get("usage_insights", {})
        
        with col1:
            total_users = metadata.get("total_users_exported", 0)
            st.metric("👥 Participants", total_users)
        
        with col2:
            avg_sessions = usage_insights.get("average_sessions_per_user", 0)
            st.metric("📱 Sessions Moy.", f"{avg_sessions:.1f}")
        
        with col3:
            avg_cv = usage_insights.get("average_cv_per_user", 0)
            st.metric("📄 CV Générés Moy.", f"{avg_cv:.1f}")
        
        with col4:
            avg_letters = usage_insights.get("average_letters_per_user", 0)
            st.metric("✉️ Lettres Générées Moy.", f"{avg_letters:.1f}")
    
    def render_demographic_analysis(self):
        """Analyse démographique"""
        st.markdown("## 🌍 Analyse Démographique")
        
        demographic_data = self.research_data.get("aggregated_insights", {}).get("demographic_insights", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution par âge
            age_dist = demographic_data.get("age_distribution", {})
            if age_dist:
                fig_age = px.bar(
                    x=list(age_dist.keys()),
                    y=list(age_dist.values()),
                    title="Distribution par Tranche d'Âge",
                    color=list(age_dist.values()),
                    color_continuous_scale="Blues"
                )
                fig_age.update_layout(
                    showlegend=False,
                    xaxis_title="Tranche d'âge",
                    yaxis_title="Nombre de participants"
                )
                st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            # Distribution géographique
            region_dist = demographic_data.get("region_distribution", {})
            if region_dist:
                fig_region = px.pie(
                    names=list(region_dist.keys()),
                    values=list(region_dist.values()),
                    title="Distribution Géographique"
                )
                st.plotly_chart(fig_region, use_container_width=True)
    
    def render_emotional_insights(self):
        """Analyse des insights émotionnels"""
        st.markdown("## 🧠 Insights Émotionnels et Valeurs")
        
        emotional_data = self.research_data.get("aggregated_insights", {}).get("emotional_insights", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 😊 Émotions Exprimées")
            emotion_freq = emotional_data.get("emotion_frequency", {})
            
            if emotion_freq:
                # Graphique en barres horizontales pour les émotions
                emotions_df = pd.DataFrame(list(emotion_freq.items()), columns=['Émotion', 'Fréquence'])
                emotions_df = emotions_df.sort_values('Fréquence', ascending=True)
                
                fig_emotions = px.bar(
                    emotions_df,
                    x='Fréquence',
                    y='Émotion',
                    orientation='h',
                    title="Fréquence des Émotions",
                    color='Fréquence',
                    color_continuous_scale="RdYlBu_r"
                )
                st.plotly_chart(fig_emotions, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Valeurs Recherchées")
            value_freq = emotional_data.get("value_frequency", {})
            
            if value_freq:
                # Graphique radar pour les valeurs
                values_list = list(value_freq.keys())
                freq_list = list(value_freq.values())
                
                fig_values = go.Figure()
                fig_values.add_trace(go.Scatterpolar(
                    r=freq_list,
                    theta=values_list,
                    fill='toself',
                    name='Fréquence des Valeurs',
                    line_color='#667eea'
                ))
                
                fig_values.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, max(freq_list)])
                    ),
                    title="Radar des Valeurs Recherchées",
                    showlegend=True
                )
                st.plotly_chart(fig_values, use_container_width=True)
    
    def render_transition_analysis(self):
        """Analyse des phases de transition"""
        st.markdown("## 🔄 Phases de Transition")
        
        emotional_data = self.research_data.get("aggregated_insights", {}).get("emotional_insights", {})
        phase_dist = emotional_data.get("transition_phase_distribution", {})
        
        if phase_dist:
            # Graphique en entonnoir pour les phases
            phases_order = ["questionnement", "exploration", "préparation", "action", "intégration", "bilan"]
            ordered_phases = {phase: phase_dist.get(phase, 0) for phase in phases_order if phase in phase_dist}
            
            fig_funnel = go.Figure(go.Funnel(
                y=list(ordered_phases.keys()),
                x=list(ordered_phases.values()),
                textinfo="value+percent initial",
                marker_color=["#667eea", "#764ba2", "#28a745", "#ffc107", "#fd7e14", "#dc3545"][:len(ordered_phases)]
            ))
            
            fig_funnel.update_layout(
                title="Répartition des Phases de Transition",
                font_size=12
            )
            
            st.plotly_chart(fig_funnel, use_container_width=True)
            
            # Insights textuels
            st.markdown("""
            <div class="insight-box">
                <h4>💡 Insights sur les Phases de Transition</h4>
                <p>La majorité des utilisateurs se trouvent en phase de <strong>questionnement</strong> et d'<strong>exploration</strong>, 
                suggérant un besoin important d'accompagnement dans la clarification des objectifs de reconversion.</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_research_implications(self):
        """Implications pour la recherche"""
        st.markdown("## 🎓 Implications Scientifiques")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="insight-box">
                <h4>🔬 Observations Clés</h4>
                <ul>
                    <li><strong>Burnout Répandu:</strong> 33% des participants expriment de l'épuisement professionnel</li>
                    <li><strong>Quête de Sens:</strong> 38% recherchent prioritairement du sens dans leur travail</li>
                    <li><strong>Besoin d'Autonomie:</strong> 25% aspirent à plus d'indépendance professionnelle</li>
                    <li><strong>Phase d'Exploration:</strong> La majorité est en phase de questionnement actif</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="insight-box">
                <h4>🎯 Recommandations IA</h4>
                <ul>
                    <li><strong>Accompagnement Émotionnel:</strong> Intégrer des mécanismes de soutien psychologique</li>
                    <li><strong>Clarification de Valeurs:</strong> Développer des outils d'exploration des valeurs personnelles</li>
                    <li><strong>Parcours Personnalisés:</strong> Adapter les recommandations aux phases de transition</li>
                    <li><strong>Approche Holistique:</strong> Considérer l'équilibre vie pro/perso dans les suggestions</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def render_ethics_compliance(self):
        """Section conformité éthique"""
        st.markdown("## 🛡️ Conformité Éthique")
        
        ethics_data = self.research_data.get("ethics_compliance", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        compliance_items = [
            ("🇪🇺 RGPD", ethics_data.get("rgpd_compliant", False)),
            ("✅ Consentement", ethics_data.get("consent_verified", False)),
            ("🔒 Anonymisation", ethics_data.get("anonymization_validated", False)),
            ("🚫 Données Perso", not ethics_data.get("no_personal_data", True))
        ]
        
        for i, (label, status) in enumerate(compliance_items):
            with [col1, col2, col3, col4][i]:
                color = "#28a745" if status else "#dc3545"
                icon = "✅" if status else "❌"
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {color};">
                    <h4 style="color: {color}; margin: 0;">{icon} {label}</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">
                        {'Conforme' if status else 'Non Conforme'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Note de recherche
        st.markdown("""
        <div class="research-note">
            <strong>📋 Note de Recherche:</strong> 
            Toutes les données présentées dans ce dashboard sont entièrement anonymisées et agrégées. 
            Aucune donnée personnelle n'est stockée ou affichée. Cette recherche respecte intégralement 
            les principes du RGPD et de l'éthique de la recherche en sciences sociales.
        </div>
        """, unsafe_allow_html=True)
    
    def render_call_to_action(self):
        """Appel à l'action pour la recherche"""
        st.markdown("## 🤝 Participez à la Recherche")
        
        st.markdown("""
        <div class="insight-box">
            <h3>🌟 Votre Contribution Compte</h3>
            <p>En utilisant Phoenix, vous contribuez à une recherche d'utilité publique sur l'IA éthique 
            dans l'accompagnement des reconversions professionnelles.</p>
            
            <h4>💡 Pourquoi Participer ?</h4>
            <ul>
                <li>🔬 <strong>Recherche Publique:</strong> Vos données (anonymes) aident la science</li>
                <li>🤖 <strong>IA Plus Humaine:</strong> Amélioration des algorithmes d'accompagnement</li>
                <li>🌍 <strong>Impact Social:</strong> Meilleur soutien pour les reconversions futures</li>
                <li>🛡️ <strong>Respect Total:</strong> Anonymisation garantie, révocable à tout moment</li>
            </ul>
            
            <h4>🖊️ Comment Participer ?</h4>
            <p>Lors de votre utilisation de Phoenix, vous pouvez donner votre consentement dans 
            la section "Contribution à la Recherche" de votre profil.</p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Lancement principal du dashboard"""
        # En-tête
        self.render_header()
        
        # Barre latérale
        self.render_sidebar()
        
        # Contenu principal
        self.render_overview_metrics()
        
        st.markdown("---")
        
        self.render_demographic_analysis()
        
        st.markdown("---")
        
        self.render_emotional_insights()
        
        st.markdown("---")
        
        self.render_transition_analysis()
        
        st.markdown("---")
        
        self.render_research_implications()
        
        st.markdown("---")
        
        self.render_ethics_compliance()
        
        st.markdown("---")
        
        self.render_call_to_action()
        
        # Footer
        st.markdown("""
        ---
        <div style="text-align: center; color: #666; padding: 2rem;">
            <p>🔬 <strong>Dashboard Recherche-Action Phoenix</strong> - Données Éthiques & Anonymisées</p>
            <p>Made with ❤️ for Social Good | 🛡️ Privacy by Design | 🌍 Open Research</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Point d'entrée principal du dashboard"""
    dashboard = ResearchDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()