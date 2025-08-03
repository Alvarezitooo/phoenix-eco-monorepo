"""
🚀 Phoenix Letters - Launcher Architecture Poetry Simple
Solution finale : Poetry a installé les packages, utilisons-les directement !
"""

# Point d'entrée principal - Architecture clean Poetry
if __name__ == "__main__":
    try:
        # Import direct depuis le paquet installé par Poetry
        # Poetry a installé phoenix_letters dans l'environnement
        from phoenix_letters.app import main
        
        print("✅ Architecture Poetry package activée")
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
        
        st.error("❌ **Architecture Poetry en cours de déploiement**")
        
        st.info(f"""
        **🏗️ Solution Poetry Package**
        
        L'architecture finale est en cours d'installation :
        
        1. 📦 **phoenix_event_bridge** (package partagé)
        2. 🚀 **phoenix_letters** (application principale)
        
        **Status :** {str(e)}
        """)
        
        # Diagnostic de l'environnement
        st.subheader("🔍 Diagnostic Architecture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📦 Packages Poetry attendus :**")
            packages_to_check = ["phoenix_event_bridge", "phoenix_letters"]
            
            for pkg in packages_to_check:
                try:
                    __import__(pkg)
                    st.success(f"✅ {pkg}")
                except ImportError:
                    st.error(f"❌ {pkg}")
        
        with col2:
            st.write("**🐍 Python Path :**")
            for i, path in enumerate(sys.path[:6]):
                if any(keyword in path.lower() for keyword in ['phoenix', 'packages', 'apps']):
                    st.success(f"{i+1}. {path}")
                else:
                    st.code(f"{i+1}. {path}")
        
        st.markdown("---")
        st.success("""
        **🎯 Poetry va installer automatiquement :**
        
        1. Package `phoenix_letters` depuis `apps/phoenix-letters/`
        2. Package `phoenix_event_bridge` depuis `packages/`
        3. Toutes les dépendances (84 packages)
        4. Phoenix Letters se lance automatiquement !
        """)
        
        if st.button("🔄 Recharger l'application"):
            st.rerun()