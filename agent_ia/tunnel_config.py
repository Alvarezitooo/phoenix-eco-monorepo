#!/usr/bin/env python3
"""
🌐 Phoenix Agents IA - Configuration Tunnel Cloud
Exposition sécurisée des agents locaux pour apps déployées
"""

import os
import subprocess
import time
import requests
import json
from typing import Optional, Dict, Any
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhoenixAgentsTunnel:
    """
    🌉 Gestionnaire tunnel pour agents IA Phoenix
    Expose les agents locaux aux apps déployées (Railway/Streamlit Cloud)
    """
    
    def __init__(self):
        self.local_port = 8001
        self.tunnel_url: Optional[str] = None
        self.tunnel_process: Optional[subprocess.Popen] = None
        self.tunnel_type = "cloudflared"  # ou "ngrok"
        
    def install_cloudflared(self) -> bool:
        """Installation automatique cloudflared si nécessaire"""
        try:
            # Vérifier si cloudflared existe
            subprocess.run(["cloudflared", "--version"], 
                         capture_output=True, check=True)
            logger.info("✅ cloudflared already installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("📥 Installing cloudflared...")
            
            # Installation via Homebrew sur macOS
            try:
                subprocess.run(["brew", "install", "cloudflared"], check=True)
                logger.info("✅ cloudflared installed successfully")
                return True
            except subprocess.CalledProcessError:
                logger.error("❌ Failed to install cloudflared via brew")
                logger.info("💡 Install manually: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
                return False
    
    def start_tunnel(self) -> Optional[str]:
        """Démarrage tunnel cloudflared"""
        if not self.install_cloudflared():
            return None
            
        logger.info(f"🚀 Starting tunnel for agents on port {self.local_port}...")
        
        try:
            # Commande cloudflared tunnel
            cmd = [
                "cloudflared", "tunnel", 
                "--url", f"http://localhost:{self.local_port}",
                "--no-autoupdate"
            ]
            
            self.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre l'URL du tunnel
            timeout = 30
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.tunnel_process.poll() is not None:
                    logger.error("❌ Tunnel process exited unexpectedly")
                    return None
                
                # Lire la sortie pour trouver l'URL
                try:
                    line = self.tunnel_process.stdout.readline()
                    if "https://" in line and "trycloudflare.com" in line:
                        # Extraire l'URL
                        self.tunnel_url = line.strip().split()[-1]
                        if self.tunnel_url.startswith("https://"):
                            logger.info(f"✅ Tunnel active: {self.tunnel_url}")
                            return self.tunnel_url
                except:
                    pass
                    
                time.sleep(1)
            
            logger.error("❌ Timeout waiting for tunnel URL")
            self.stop_tunnel()
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to start tunnel: {e}")
            return None
    
    def stop_tunnel(self):
        """Arrêt du tunnel"""
        if self.tunnel_process:
            logger.info("🛑 Stopping tunnel...")
            self.tunnel_process.terminate()
            try:
                self.tunnel_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.tunnel_process.kill()
            self.tunnel_process = None
            self.tunnel_url = None
            logger.info("✅ Tunnel stopped")
    
    def test_tunnel(self) -> bool:
        """Test de connectivité du tunnel"""
        if not self.tunnel_url:
            return False
            
        try:
            response = requests.get(f"{self.tunnel_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Tunnel connectivity test passed")
                return True
            else:
                logger.warning(f"⚠️ Tunnel responds but with status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Tunnel connectivity test failed: {e}")
            return False
    
    def get_config_for_apps(self) -> Dict[str, Any]:
        """Génération config pour apps déployées"""
        if not self.tunnel_url:
            return {"error": "No tunnel active"}
            
        return {
            "agents_api_url": self.tunnel_url,
            "endpoints": {
                "health": f"{self.tunnel_url}/health",
                "security_analyze": f"{self.tunnel_url}/security/analyze",
                "data_insights": f"{self.tunnel_url}/data/insights",
                "data_analyze": f"{self.tunnel_url}/data/analyze",
                "system_status": f"{self.tunnel_url}/system/status"
            },
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "Phoenix-App/1.0"
            },
            "timeout": 30,
            "fallback_enabled": True
        }
    
    def generate_env_vars(self) -> str:
        """Génération variables d'environnement pour apps"""
        if not self.tunnel_url:
            return "# No tunnel active"
            
        return f"""# 🌐 Phoenix Agents IA - Tunnel Configuration
# Variables pour apps déployées (Railway/Streamlit Cloud)

AGENTS_API_URL={self.tunnel_url}
AGENTS_API_ENABLED=true
AGENTS_API_TIMEOUT=30
AGENTS_FALLBACK_ENABLED=true

# Endpoints spécifiques
AGENTS_SECURITY_ENDPOINT={self.tunnel_url}/security/analyze
AGENTS_DATA_ENDPOINT={self.tunnel_url}/data/insights
AGENTS_HEALTH_ENDPOINT={self.tunnel_url}/health
"""

def main():
    """Fonction principale pour test"""
    tunnel = PhoenixAgentsTunnel()
    
    print("🌐 Phoenix Agents IA - Configuration Tunnel")
    print("=" * 50)
    
    # Démarrage tunnel
    tunnel_url = tunnel.start_tunnel()
    
    if tunnel_url:
        print(f"✅ Tunnel actif: {tunnel_url}")
        
        # Test connectivité
        print("🧪 Test de connectivité...")
        if tunnel.test_tunnel():
            print("✅ Test réussi!")
        else:
            print("❌ Test échoué")
        
        # Configuration pour apps
        print("\n📋 Configuration pour vos apps déployées:")
        print(tunnel.generate_env_vars())
        
        print("\n🔗 URLs à utiliser dans vos apps:")
        config = tunnel.get_config_for_apps()
        for name, url in config.get("endpoints", {}).items():
            print(f"  • {name}: {url}")
        
        print("\n⚠️ Le tunnel restera actif. Appuyez sur Ctrl+C pour arrêter.")
        
        try:
            while True:
                time.sleep(60)
                # Test périodique
                if not tunnel.test_tunnel():
                    print("⚠️ Tunnel connectivity lost, restarting...")
                    tunnel.stop_tunnel()
                    tunnel_url = tunnel.start_tunnel()
                    if tunnel_url:
                        print(f"✅ Tunnel restarted: {tunnel_url}")
                    else:
                        print("❌ Failed to restart tunnel")
                        break
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé...")
        finally:
            tunnel.stop_tunnel()
    else:
        print("❌ Impossible de démarrer le tunnel")

if __name__ == "__main__":
    main()