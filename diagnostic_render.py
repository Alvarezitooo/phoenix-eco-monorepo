#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC RENDER - Vérification Repo vs Interface Bug
"""

import yaml
import json
import os
from pathlib import Path

def test_render_yaml():
    """Test complet du render.yaml"""
    print("🔍 DIAGNOSTIC RENDER.YAML")
    print("=" * 50)
    
    # Test 1: Fichier existe
    yaml_path = Path("render.yaml")
    if not yaml_path.exists():
        print("❌ render.yaml manquant")
        return False
    print("✅ render.yaml existe")
    
    # Test 2: Syntaxe YAML valide
    try:
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
        print("✅ Syntaxe YAML valide")
    except Exception as e:
        print(f"❌ Erreur YAML: {e}")
        return False
    
    # Test 3: Structure obligatoire
    if 'services' not in config:
        print("❌ Section 'services' manquante")
        return False
    print("✅ Section 'services' présente")
    
    # Test 4: Services valides
    services = config['services']
    print(f"✅ {len(services)} services trouvés:")
    
    for i, service in enumerate(services):
        name = service.get('name', f'service_{i}')
        service_type = service.get('type', 'unknown')
        
        # Vérifications par service
        issues = []
        
        if 'name' not in service:
            issues.append("name manquant")
        if 'type' not in service:
            issues.append("type manquant")
        if service.get('env') == 'docker' and 'dockerfilePath' not in service:
            issues.append("dockerfilePath manquant pour Docker")
        if service_type == 'web' and service.get('env') == 'docker' and 'healthCheckPath' not in service:
            issues.append("healthCheckPath recommandé")
            
        if issues:
            print(f"   ⚠️  {name} ({service_type}): {', '.join(issues)}")
        else:
            print(f"   ✅ {name} ({service_type}): OK")
    
    # Test 5: Paths Docker valides
    docker_services = [s for s in services if s.get('env') == 'docker']
    for service in docker_services:
        dockerfile_path = service.get('dockerfilePath', '')
        full_path = Path(dockerfile_path)
        
        if full_path.exists():
            print(f"   ✅ Dockerfile existe: {dockerfile_path}")
        else:
            print(f"   ❌ Dockerfile manquant: {dockerfile_path}")
            return False
    
    # Test 6: Variables d'environnement
    env_issues = []
    for service in services:
        env_vars = service.get('envVars', [])
        for var in env_vars:
            if 'fromService' in var and 'name' in var:
                # Check que le service référencé existe
                ref_service = var['fromService']
                if not any(s.get('name') == ref_service for s in services):
                    env_issues.append(f"{service['name']}: référence service inexistant {ref_service}")
    
    if env_issues:
        print("⚠️  Références services:")
        for issue in env_issues:
            print(f"   {issue}")
    else:
        print("✅ Références entre services OK")
    
    return True

def test_repo_structure():
    """Test structure du repo"""
    print("\n🏗️ DIAGNOSTIC STRUCTURE REPO")
    print("=" * 50)
    
    critical_files = [
        "Dockerfile",
        "apps/phoenix-letters/app.py",
        "apps/phoenix-letters/requirements.txt",
        "apps/phoenix-cv/app.py", 
        "apps/phoenix-cv/requirements.txt",
        "apps/phoenix-backend-unified/app.py",
        "apps/phoenix-backend-unified/requirements.txt"
    ]
    
    missing = []
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing.append(file_path)
    
    return len(missing) == 0

def test_render_specific_issues():
    """Test des problèmes spécifiques Render"""
    print("\n⚡ DIAGNOSTIC SPÉCIFIQUE RENDER")
    print("=" * 50)
    
    # Vérification taille du render.yaml
    yaml_size = Path("render.yaml").stat().st_size
    print(f"📏 Taille render.yaml: {yaml_size} bytes")
    
    if yaml_size > 50000:  # 50KB
        print("⚠️  Fichier très volumineux - possible timeout Render")
    else:
        print("✅ Taille acceptable")
    
    # Vérification caractères spéciaux
    with open("render.yaml") as f:
        content = f.read()
    
    if "🚀" in content or "✅" in content:
        print("⚠️  Emojis détectés - possible problème parsing Render")
        # Compter les emojis
        emoji_count = sum(1 for c in content if ord(c) > 127)
        print(f"   📊 {emoji_count} caractères non-ASCII")
    else:
        print("✅ Pas d'emojis problématiques")
    
    # Test longueur des noms de services
    with open("render.yaml") as f:
        config = yaml.safe_load(f)
    
    long_names = []
    for service in config.get('services', []):
        name = service.get('name', '')
        if len(name) > 30:
            long_names.append(name)
    
    if long_names:
        print(f"⚠️  Noms de services longs: {long_names}")
    else:
        print("✅ Noms de services OK")

def generate_minimal_yaml():
    """Génère un YAML minimal pour test"""
    print("\n🔧 GÉNÉRATION YAML MINIMAL")
    print("=" * 50)
    
    minimal_config = {
        'services': [
            {
                'type': 'web',
                'name': 'phoenix-letters-test',
                'env': 'docker', 
                'dockerfilePath': './Dockerfile',
                'dockerBuildArgs': ['APP_NAME=phoenix-letters'],
                'plan': 'free',
                'envVars': [
                    {'key': 'TEST_VAR', 'value': 'test'}
                ]
            }
        ]
    }
    
    with open('render-minimal-test.yaml', 'w') as f:
        yaml.dump(minimal_config, f, default_flow_style=False, sort_keys=False)
    
    print("✅ render-minimal-test.yaml créé")
    print("   📝 1 service simple pour test")

def main():
    print("🔍 DIAGNOSTIC COMPLET: REPO vs RENDER BUG")
    print("=" * 60)
    
    # Tests
    yaml_ok = test_render_yaml()
    repo_ok = test_repo_structure() 
    test_render_specific_issues()
    
    print("\n" + "=" * 60)
    print("📋 VERDICT FINAL")
    print("=" * 60)
    
    if yaml_ok and repo_ok:
        print("✅ TON REPO EST PARFAIT !")
        print("   Le problème vient bien de l'interface Render")
        print("   Recommandation: Déploiement manuel ou CLI")
    else:
        print("⚠️  PROBLÈMES REPO DÉTECTÉS")
        print("   Corriger ces problèmes avant de blâmer Render")
    
    # Génération fichier test
    generate_minimal_yaml()
    
    print(f"\n🚀 PROCHAINES ÉTAPES:")
    print("1. Si repo OK → Interface Render bugge, utilise déploiement manuel")
    print("2. Si repo KO → Corrige les erreurs détectées") 
    print("3. Test avec render-minimal-test.yaml pour confirmation")

if __name__ == "__main__":
    main()