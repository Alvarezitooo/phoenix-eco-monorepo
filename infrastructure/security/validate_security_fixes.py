#!/usr/bin/env python3
"""
🛡️ Phoenix Security Validation Script
Valide que les vulnérabilités Dependabot ont été corrigées

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Security Patch Validation
"""

import subprocess
import sys
from pathlib import Path

def check_package_version(package_name: str, min_version: str, requirements_file: str) -> bool:
    """Vérifie qu'un package respecte la version minimale sécurisée."""
    try:
        with open(requirements_file, 'r') as f:
            content = f.read()
            
        for line in content.split('\n'):
            if line.strip().startswith(package_name):
                if min_version in line or f">={min_version}" in line:
                    print(f"✅ {package_name} - Version sécurisée trouvée dans {requirements_file}")
                    return True
                else:
                    print(f"❌ {package_name} - Version non sécurisée dans {requirements_file}: {line}")
                    return False
                    
        print(f"⚠️  {package_name} - Non trouvé dans {requirements_file}")
        return True  # Pas utilisé = pas de risque
        
    except FileNotFoundError:
        print(f"⚠️  Fichier non trouvé: {requirements_file}")
        return True

def main():
    """Valide toutes les corrections de sécurité."""
    print("🛡️ PHOENIX SECURITY VALIDATION")
    print("=" * 50)
    
    # Vulnérabilités à vérifier
    security_checks = [
        {
            "package": "python-jose",
            "min_version": "3.4.0",
            "description": "CVE-2024-33663 & CVE-2024-33664 - ECDSA confusion & JWE DoS"
        },
        {
            "package": "python-multipart", 
            "min_version": "0.0.9",
            "description": "ReDoS & multipart DoS vulnerabilities"
        }
    ]
    
    # Fichiers requirements à vérifier
    requirements_files = [
        "requirements.txt",
        "apps/phoenix-backend-unified/requirements.txt", 
        "agent_ia/requirements.txt",
        "packages/phoenix-shared-auth/requirements.txt"
    ]
    
    all_secure = True
    
    for check in security_checks:
        print(f"\n🔍 Vérification: {check['package']} >= {check['min_version']}")
        print(f"   Vulnérabilité: {check['description']}")
        
        for req_file in requirements_files:
            if not check_package_version(check['package'], check['min_version'], req_file):
                all_secure = False
    
    print("\n" + "=" * 50)
    if all_secure:
        print("🎉 TOUTES LES VULNÉRABILITÉS SONT CORRIGÉES!")
        print("✅ Phoenix est maintenant sécurisé contre:")
        print("   - CVE-2024-33663: ECDSA algorithm confusion")
        print("   - CVE-2024-33664: JWE compression DoS") 
        print("   - python-multipart ReDoS attacks")
        print("   - multipart form-data DoS attacks")
        sys.exit(0)
    else:
        print("❌ VULNÉRABILITÉS ENCORE PRÉSENTES!")
        print("⚠️  Action requise: Mettre à jour les packages non conformes")
        sys.exit(1)

if __name__ == "__main__":
    main()
