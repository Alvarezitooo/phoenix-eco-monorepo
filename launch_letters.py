"""
🚀 Phoenix Letters - Launcher Script Architectural Clean
Solution Gemini Pro Oracle - Package installable approach

Ce launcher est maintenant beaucoup plus simple grâce à l'approche
par paquet installable. Plus besoin de manipuler sys.path !
"""

# Point d'entrée principal avec package installé
if __name__ == "__main__":
    try:
        # Import direct depuis le paquet installé 'phoenix_letters'
        from phoenix_letters.app import main
        
        # Exécution de l'application Phoenix Letters complète
        main()
        
    except ImportError as e:
        # Fallback avec diagnostic détaillé
        import streamlit as st
        
        st.set_page_config(
            page_title="🚀 Phoenix Letters",
            page_icon="🔥",
            layout="wide"
        )
        
        st.error(f"""
        **❌ Erreur d'importation du module Phoenix Letters**
        
        Cela signifie probablement que l'installation via `pip install -e .` 
        a échoué dans l'environnement Streamlit Cloud.
        
        **🔧 Solution Gemini Pro Oracle en cours...**
        """)
        
        st.code(f"Détails de l'erreur: {str(e)}")
        
        st.info("""
        **🏗️ Architecture Gemini Pro Oracle**
        
        - ✅ Launcher pattern activé
        - 🔄 Package installable en cours de déploiement
        - 🎯 Solution définitive pour monorepo Python
        """)
        
        # Diagnostics additionnels
        st.subheader("🔍 Diagnostic Environnement")
        
        import sys
        import os
        
        st.write("**Python Path:**")
        for path in sys.path[:5]:  # Affiche les 5 premiers paths
            st.code(path)
            
        st.write("**Working Directory:**")
        st.code(os.getcwd())
        
        st.write("**Environment Type:**")
        st.code("Streamlit Cloud" if "streamlit" in os.getcwd().lower() else "Local")

def main():
    """Point d'entrée alternatif (ne sera pas utilisé avec le package)"""
    pass