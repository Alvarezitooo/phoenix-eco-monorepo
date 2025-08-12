"""
Page de test pour diagnostiquer le problème de rendu HTML
"""
import streamlit as st

st.set_page_config(layout="wide", page_title="Test Rendu HTML - Phoenix CV")
st.title("🧪 Page de Test de Rendu HTML")

# Test direct avec st.markdown
st.subheader("Test 1: st.markdown direct")
html_string = "<div style='padding: 10px; border: 2px solid red; background: #ffe6e6;'><strong>✅ Ceci est un test HTML direct.</strong></div>"
st.markdown(html_string, unsafe_allow_html=True)

# Test avec listes HTML
st.subheader("Test 2: Listes HTML avec st.markdown")
html_list = """
<div style='padding: 15px; border: 2px solid blue; background: #e6f3ff;'>
    <h4>📋 Test Liste HTML</h4>
    <ul style='color: #333;'>
        <li>✅ Item 1 - Test</li>
        <li>✅ Item 2 - Test</li>
        <li>✅ Item 3 - Test</li>
    </ul>
</div>
"""
st.markdown(html_list, unsafe_allow_html=True)

# Test avec la fonction importée
st.subheader("Test 3: Fonction safe_markdown importée")
try:
    from phoenix_cv.utils.safe_markdown import safe_markdown
    test_html = "<div style='padding: 10px; border: 2px solid green; background: #e6ffe6;'><strong>✅ Test safe_markdown importé réussi!</strong></div>"
    safe_markdown(test_html)
    st.success("✅ Import et exécution de safe_markdown réussis.")
except Exception as e:
    st.error(f"❌ Erreur lors de l'import ou l'exécution de safe_markdown : {e}")

# Test des widgets problématiques
st.subheader("Test 4: Widget Écosystème Reproductible")
phoenix_html = """
<div style="background: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #007bff; text-align: center;">
    <h3 style="color: #333;">📄 Phoenix CV Test</h3>
    <p style="color: #666; font-size: 0.9rem;">Test du widget écosystème</p>
    
    <ul style="text-align: left; color: #333; font-size: 0.85rem;">
        <li>✅ Prompts magistraux Gemini Pro</li>
        <li>✅ Optimisation ATS avancée</li>
        <li>✅ Spécialisé reconversions</li>
        <li>✅ Green AI intégré</li>
    </ul>
</div>
"""

try:
    from phoenix_cv.utils.safe_markdown import safe_markdown
    safe_markdown(phoenix_html)
    st.success("✅ Widget écosystème rendu avec safe_markdown")
except:
    st.markdown(phoenix_html, unsafe_allow_html=True)
    st.warning("⚠️ Widget rendu avec st.markdown direct (fallback)")

# Informations de debug
st.subheader("🔍 Informations de Debug")
st.write(f"**Streamlit version:** {st.__version__}")
st.write(f"**Session state keys:** {list(st.session_state.keys())}")

if st.button("🔄 Rerun Test"):
    st.rerun()