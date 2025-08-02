"""
🚀 Phoenix Letters - Launcher Script with Smart Fallback
Solution Gemini Pro Oracle avec fallback intelligent

Stratégie : Package installable + fallback sys.path si échec installation
"""

import os
import sys

def main():
    """Point d'entrée principal avec stratégie de fallback robuste"""
    
    # Configuration Streamlit globale
    import streamlit as st
    
    st.set_page_config(
        page_title="🚀 Phoenix Letters", 
        page_icon="🔥",
        layout="wide"
    )
    
    # Stratégie 1: Essayer le package installé (solution Gemini Pro)
    try:
        from phoenix_letters.app import main as phoenix_main
        print("✅ Package phoenix_letters trouvé - utilisation de l'architecture propre")
        phoenix_main()
        return
    except ImportError as package_error:
        print(f"⚠️ Package installé non trouvé: {package_error}")
        pass  # Continue vers fallback
    
    # Stratégie 2: Fallback sys.path avec gestion imports (solution de secours)
    
    try:
        print("🔄 Fallback vers manipulation sys.path...")
        
        # Ajouter le chemin Phoenix Letters au sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        phoenix_letters_path = os.path.join(current_dir, 'apps', 'phoenix-letters')
        
        if phoenix_letters_path not in sys.path:
            sys.path.insert(0, phoenix_letters_path)
            
        print(f"📁 Chemin ajouté: {phoenix_letters_path}")
        
        # Import et exécution plus robuste
        import importlib.util
        
        app_file_path = os.path.join(phoenix_letters_path, 'app.py')
        
        if os.path.exists(app_file_path):
            st.success("✅ Fallback sys.path activé - Chargement de l'app Phoenix Letters...")
            
            # Essayer d'importer le module app directement
            spec = importlib.util.spec_from_file_location("phoenix_app", app_file_path)
            phoenix_app = importlib.util.module_from_spec(spec)
            
            # Ajouter au sys.modules pour les imports relatifs
            sys.modules["phoenix_app"] = phoenix_app
            
            # Exécuter le module
            spec.loader.exec_module(phoenix_app)
            
            # Appeler la fonction main si elle existe
            if hasattr(phoenix_app, 'main'):
                print("✅ Fallback réussi - chargement de l'app originale")
                phoenix_app.main()
                return
            else:
                st.error("❌ Fonction main() non trouvée dans app.py")
        else:
            st.error(f"❌ Fichier app.py non trouvé: {app_file_path}")
            
    except Exception as fallback_error:
        print(f"❌ Fallback échoué: {fallback_error}")
        st.error(f"**❌ Erreur Fallback:** {str(fallback_error)}")
        
        # Afficher l'erreur détaillée pour debug
        import traceback
        st.code(traceback.format_exc())
        
        pass  # Continue vers diagnostic
    
    # Stratégie 3: Diagnostic et interface minimale
    
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