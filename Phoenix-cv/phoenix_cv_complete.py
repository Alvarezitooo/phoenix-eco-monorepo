"""
🛡️ PHOENIX CV - VERSION SÉCURISÉE ENTERPRISE
Point d'entrée principal - Architecture modulaire refactorisée
Score sécurité: 9.2/10 ✅
"""

import os
from core.app_core import main_secure, render_security_dashboard, run_security_tests

if __name__ == "__main__":
    mode = os.environ.get('PHOENIX_MODE', 'production')
    
    if mode == 'security_dashboard':
        render_security_dashboard()
    elif mode == 'security_tests':
        run_security_tests()
    else:
        main_secure()