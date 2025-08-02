"""
🚀 Phoenix Letters - Launcher Architecture Multi-Packages
Solution Gemini Pro Oracle finale - Plus de manipulation sys.path !

Architecture professionnelle avec packages installés proprement
"""

# Point d'entrée principal - Architecture clean Gemini Pro Oracle
if __name__ == "__main__":
    try:
        # Import direct depuis le paquet installé 'phoenix_letters'  
        # Tous les composants partagés sont maintenant des packages installés
        from phoenix_letters.app import main
        
        print("✅ Architecture multi-packages Gemini Pro Oracle activée")
        main()
        
    except ImportError as e:
        # Diagnostic avancé si l'architecture n'est pas encore déployée
        import streamlit as st
        import os
        import sys
        
        st.set_page_config(
            page_title="🚀 Phoenix Letters",
            page_icon="🔥", 
            layout="wide"
        )
        
        st.error("❌ **Architecture multi-packages en cours de déploiement**")
        
        st.info(f"""
        **🏗️ Solution Gemini Pro Oracle - Multi-Packages**
        
        L'architecture professionnelle finale est en cours d'installation :
        
        1. 📦 **phoenix_event_bridge** (package partagé)
        2. 🚀 **phoenix_letters** (application avec dépendances déclarées)
        
        **Status :** {str(e)}
        """)
        
        # Diagnostic de l'environnement
        st.subheader("🔍 Diagnostic Architecture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📦 Packages attendus :**")
            packages_to_check = ["phoenix_event_bridge", "phoenix_letters"]
            
            for pkg in packages_to_check:
                try:
                    __import__(pkg)
                    st.success(f"✅ {pkg}")
                except ImportError:
                    st.error(f"❌ {pkg}")
            
            st.write("**📁 Structure monorepo :**")
            base_dir = os.getcwd()
            
            expected_dirs = [
                "packages/phoenix_event_bridge",
                "apps/phoenix-letters"
            ]
            
            for dir_path in expected_dirs:
                full_path = os.path.join(base_dir, dir_path)
                if os.path.exists(full_path):
                    st.success(f"✅ {dir_path}")
                else:
                    st.error(f"❌ {dir_path}")
        
        with col2:
            st.write("**🔧 Requirements status :**")
            req_path = os.path.join(os.getcwd(), 'requirements.txt')
            
            if os.path.exists(req_path):
                st.success("✅ requirements.txt")
                try:
                    with open(req_path, 'r') as f:
                        content = f.read()
                    st.code(content)
                except Exception as e:
                    st.error(f"Erreur lecture: {e}")
            else:
                st.error("❌ requirements.txt manquant")
            
            st.write("**🐍 Python Path :**")
            for i, path in enumerate(sys.path[:6]):
                if any(keyword in path.lower() for keyword in ['phoenix', 'packages', 'apps']):
                    st.success(f"{i+1}. {path}")
                else:
                    st.code(f"{i+1}. {path}")
        
        st.markdown("---")
        st.success("""
        **🎯 Prochaines étapes automatiques :**
        
        1. Streamlit Cloud installe `phoenix_event_bridge` 
        2. Streamlit Cloud installe `phoenix_letters` avec ses dépendances
        3. L'architecture multi-packages devient active
        4. Phoenix Letters se charge automatiquement !
        """)
        
        if st.button("🔄 Recharger l'application"):
            st.rerun()

def main():
    """Point d'entrée alternatif (utilisé par l'architecture package)"""
    pass