#!/usr/bin/env python3
"""
Script pour corriger automatiquement les imports dans Phoenix CV
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Corrige les imports dans un fichier donné"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Corrections phoenix_shared_models
        content = re.sub(
            r'from phoenix_shared_models\.user_profile import',
            'from ..models.user_profile import',
            content
        )
        
        # Corrections phoenix_shared_auth
        content = re.sub(
            r'from phoenix_shared_auth\.entities\.phoenix_user import',
            'from ..models.phoenix_user import',
            content
        )
        
        # Corrections imports services absolus dans les fichiers UI
        if '/ui/' in str(file_path):
            content = re.sub(
                r'from services\.',
                'from ..services.',
                content
            )
        
        # Corrections imports services absolus dans les fichiers services
        elif '/services/' in str(file_path):
            content = re.sub(
                r'from services\.',
                'from .',
                content
            )
        
        # Corrections imports services absolus dans app_core
        elif 'app_core.py' in str(file_path):
            content = re.sub(
                r'from services\.',
                'from ..services.',
                content
            )
        
        # Corrections config absolus
        content = re.sub(
            r'from config\.',
            'from ..config.',
            content
        )
        
        # Sauvegarder seulement si il y a eu des modifications
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigé: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Erreur dans {file_path}: {e}")
        return False

def main():
    """Fonction principale"""
    phoenix_cv_path = Path("/Users/mattvaness/Desktop/IA/phoenix/phoenix-eco-monorepo/apps/phoenix-cv/phoenix_cv")
    
    if not phoenix_cv_path.exists():
        print("❌ Chemin Phoenix CV introuvable")
        return
    
    files_fixed = 0
    files_processed = 0
    
    # Parcourir tous les fichiers Python
    for py_file in phoenix_cv_path.rglob("*.py"):
        files_processed += 1
        if fix_imports_in_file(py_file):
            files_fixed += 1
    
    print(f"\n📊 Résumé:")
    print(f"   Fichiers traités: {files_processed}")
    print(f"   Fichiers modifiés: {files_fixed}")
    print(f"   Succès: {files_fixed}/{files_processed}")

if __name__ == "__main__":
    main()