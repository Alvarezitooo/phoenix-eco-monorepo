"""
🚀 Phoenix Letters - Launcher Script with Smart Fallback
Solution Gemini Pro Oracle avec fallback intelligent

Stratégie : Package installable + fallback sys.path si échec installation
"""

import os
import sys

def main():
    """Point d'entrée principal avec stratégie de fallback robuste"""
    
    # Stratégie 1: Essayer le package installé (solution Gemini Pro)
    try:
        from phoenix_letters.app import main as phoenix_main
        print("✅ Package phoenix_letters trouvé - utilisation de l'architecture propre")
        phoenix_main()
        return
    except ImportError as package_error:
        print(f"⚠️ Package installé non trouvé: {package_error}")
        pass  # Continue vers fallback
    
    # Stratégie 2: Fallback sys.path (solution de secours)
    try:
        print("🔄 Fallback vers manipulation sys.path...")
        
        # Ajouter le chemin Phoenix Letters au sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        phoenix_letters_path = os.path.join(current_dir, 'apps', 'phoenix-letters')
        
        if phoenix_letters_path not in sys.path:
            sys.path.insert(0, phoenix_letters_path)
            
        print(f"📁 Chemin ajouté: {phoenix_letters_path}")
        
        # Import direct depuis le chemin
        from app import main as fallback_main
        print("✅ Fallback réussi - chargement de l'app originale")
        fallback_main()
        return
        
    except ImportError as fallback_error:
        print(f"❌ Fallback échoué: {fallback_error}")
        pass  # Continue vers diagnostic
    
    # Stratégie 3: Diagnostic et interface minimale
    import streamlit as st
    
    st.set_page_config(
        page_title="🚀 Phoenix Letters", 
        page_icon="🔥",
        layout="wide"
    )
    
    st.error("❌ **Impossible de charger Phoenix Letters**")
    
    # Diagnostic détaillé
    st.subheader("🔍 Diagnostic Complet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📦 Package installé:**")
        try:
            import phoenix_letters
            st.success("✅ phoenix_letters trouvé")
        except ImportError:
            st.error("❌ phoenix_letters non installé")
            
        st.write("**📁 Répertoire apps/phoenix-letters:**")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        phoenix_path = os.path.join(current_dir, 'apps', 'phoenix-letters')
        
        if os.path.exists(phoenix_path):
            st.success(f"✅ Trouvé: {phoenix_path}")
            
            # Liste le contenu
            try:
                contents = os.listdir(phoenix_path)
                st.write("**Contenu:**")
                for item in contents[:10]:  # Affiche les 10 premiers
                    st.code(item)
            except Exception as e:
                st.error(f"Erreur listage: {e}")
        else:
            st.error(f"❌ Non trouvé: {phoenix_path}")
    
    with col2:
        st.write("**🐍 Python Path:**")
        for i, path in enumerate(sys.path[:8]):
            if 'phoenix' in path.lower():
                st.success(f"{i+1}. {path}")
            else:
                st.code(f"{i+1}. {path}")
                
        st.write("**📍 Working Directory:**")
        st.code(os.getcwd())
        
        st.write("**🔧 Requirements Status:**")
        req_path = os.path.join(os.getcwd(), 'requirements.txt')
        if os.path.exists(req_path):
            st.success("✅ requirements.txt trouvé")
            try:
                with open(req_path, 'r') as f:
                    content = f.read()
                st.code(content)
            except Exception as e:
                st.error(f"Erreur lecture: {e}")
        else:
            st.error("❌ requirements.txt non trouvé")
    
    # Solution alternative temporaire
    st.subheader("🛠️ Solution Temporaire")
    st.info("""
    **Le package n'a pas pu être installé, mais le launcher fonctionne !**
    
    🔧 **Prochaines étapes :**
    1. Vérifier l'installation du package sur Streamlit Cloud
    2. Alternative : Modifier requirements.txt pour installation directe
    3. Ou utiliser structure sans package (legacy approach)
    """)
    
    # Bouton pour forcer le reload
    if st.button("🔄 Relancer l'application"):
        st.rerun()

if __name__ == "__main__":
    main()