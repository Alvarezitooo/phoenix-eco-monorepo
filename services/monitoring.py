import time
import psutil
import tracemalloc
import logging
import functools
from datetime import datetime
from collections import defaultdict, deque
import streamlit as st
import json
import os
import traceback
import re

class PerformanceMonitor:
    """Monitore les performances en temps réel"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'min_time': float('inf'),
            'max_time': 0,
            'errors': 0,
            'last_error': None,
            'memory_usage': deque(maxlen=100)
        })
        
        # Démarrage du tracking mémoire
        tracemalloc.start()
        
        # Métriques globales
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
    def track_performance(self, component_name: str):
        """Décorateur pour tracker les performances d'une fonction"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Mesures avant exécution
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                
                # ID unique pour la requête
                request_id = f"{component_name}_{int(time.time() * 1000)}"
                
                try:
                    # Log début
                    logging.info(f"[MONITOR] Starting {component_name} - Request: {request_id}")
                    
                    # Exécution
                    result = func(*args, **kwargs)
                    
                    # Mesures après exécution
                    end_time = time.time()
                    duration = end_time - start_time
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_delta = end_memory - start_memory
                    
                    # Mise à jour métriques
                    metrics = self.metrics[component_name]
                    metrics['count'] += 1
                    metrics['total_time'] += duration
                    metrics['min_time'] = min(metrics['min_time'], duration)
                    metrics['max_time'] = max(metrics['max_time'], duration)
                    metrics['memory_usage'].append({
                        'timestamp': datetime.now().isoformat(),
                        'memory_mb': end_memory,
                        'delta_mb': memory_delta
                    })
                    
                    # Log succès
                    logging.info(f"[MONITOR] Success {component_name} - Duration: {duration:.2f}s - Memory: {memory_delta:+.1f}MB")
                    
                    # Alertes performances
                    if duration > 5:
                        logging.warning(f"[PERF ALERT] {component_name} took {duration:.2f}s (>5s threshold)")
                    
                    if memory_delta > 50:
                        logging.warning(f"[MEMORY ALERT] {component_name} used {memory_delta:.1f}MB (>50MB threshold)")
                    
                    return result
                    
                except Exception as e:
                    # Tracking erreurs
                    metrics = self.metrics[component_name]
                    metrics['errors'] += 1
                    metrics['last_error'] = {
                        'timestamp': datetime.now().isoformat(),
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
                    
                    self.error_count += 1
                    
                    # Log erreur
                    logging.error(f"[MONITOR] Error in {component_name}: {str(e)}")
                    logging.error(traceback.format_exc())
                    
                    # Re-raise l'erreur
                    raise
                    
                finally:
                    self.request_count += 1
                    
            return wrapper
        return decorator
    
    def get_metrics_summary(self):
        """Retourne un résumé des métriques"""
        uptime = time.time() - self.start_time
        
        summary = {
            'uptime_seconds': uptime,
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': self.error_count / max(self.request_count, 1),
            'components': {}
        }
        
        for component, metrics in self.metrics.items():
            avg_time = metrics['total_time'] / max(metrics['count'], 1)
            
            summary['components'][component] = {
                'requests': metrics['count'],
                'avg_time': avg_time,
                'min_time': metrics['min_time'] if metrics['min_time'] != float('inf') else 0,
                'max_time': metrics['max_time'],
                'errors': metrics['errors'],
                'error_rate': metrics['errors'] / max(metrics['count'], 1),
                'last_error': metrics['last_error']
            }
            
            # Mémoire
            if metrics['memory_usage']:
                recent_memory = [m['memory_mb'] for m in list(metrics['memory_usage'])[-10:]]
                summary['components'][component]['avg_memory_mb'] = sum(recent_memory) / len(recent_memory)
        
        return summary
    
    def display_dashboard(self):
        """Affiche un dashboard de monitoring dans Streamlit"""
        st.markdown("##  Monitoring Temps Réel")
        
        summary = self.get_metrics_summary()
        
        # Métriques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Uptime", f"{summary['uptime_seconds']:.0f}s")
        
        with col2:
            st.metric("Requêtes", summary['total_requests'])
        
        with col3:
            st.metric("Erreurs", summary['total_errors'])
        
        with col4:
            error_rate_pct = summary['error_rate'] * 100
            st.metric("Taux d'erreur", f"{error_rate_pct:.1f}%")
        
        # Détails par composant
        st.markdown("### Performances par Composant")
        
        for component, metrics in summary['components'].items():
            with st.expander(f" {component}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Requêtes", metrics['requests'])
                    st.metric("Temps moyen", f"{metrics['avg_time']:.2f}s")
                
                with col2:
                    st.metric("Temps min", f"{metrics['min_time']:.2f}s")
                    st.metric("Temps max", f"{metrics['max_time']:.2f}s")
                
                with col3:
                    st.metric("Erreurs", metrics['errors'])
                    if 'avg_memory_mb' in metrics:
                        st.metric("Mémoire moy.", f"{metrics['avg_memory_mb']:.1f}MB")
                
                if metrics['last_error']:
                    st.error(f"Dernière erreur: {metrics['last_error']['error']}")
                    with st.expander("Traceback"):
                        st.code(metrics['last_error']['traceback'])


class SecurityAuditor:
    """Audit de sécurité en temps réel"""
    
    def __init__(self):
        self.security_events = deque(maxlen=1000)
        self.suspicious_patterns = [
            r'(?i)(ignore|oublie|nouvelle instruction)',  # Prompt injection
            r'(?i)(script|javascript|onerror)',  # XSS attempts
            r'(?i)(union|select|drop|insert|update)',  # SQL injection
            r'(?i)(\.\.\/|\.\.\\)',  # Path traversal
            r'<[^>]+>',  # HTML tags
        ]
    
    def audit_input(self, input_type: str, content: str, user_id: str = None):
        """Audite une entrée utilisateur"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': input_type,
            'user_id': user_id,
            'content_length': len(content),
            'suspicious': False,
            'threats': []
        }
        
        # Vérification patterns suspects
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content):
                event['suspicious'] = True
                event['threats'].append(f"Pattern suspect détecté: {pattern}")
        
        # Vérification taille
        if len(content) > 10000:
                event['suspicious'] = True
                event['threats'].append(f"Contenu trop long: {len(content)} caractères")
        
        # Détection PII basique
        if re.search(r'\b\d{10,}\b', content):  # Numéros longs
            event['threats'].append("Possible PII: numéro long détecté")
        
        if re.search(r'\b[A-Za-z0-9._%+-]+ @[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
            event['threats'].append("PII détecté: email")
        
        self.security_events.append(event);
        
        if event['suspicious']:
            logging.warning(f"[SECURITY] Suspicious input detected: {event['threats']}")
        
        return event
    
    def get_security_summary(self):
        """Résumé des événements de sécurité"""
        total_events = len(self.security_events)
        suspicious_events = sum(1 for e in self.security_events if e['suspicious'])
        
        threat_counts = defaultdict(int)
        for event in self.security_events:
            for threat in event['threats']:
                threat_counts[threat.split(':')[0]] += 1
        
        return {
            'total_events': total_events,
            'suspicious_events': suspicious_events,
            'threat_distribution': dict(threat_counts),
            'recent_threats': list(self.security_events)[-10:]
        }


class UserBehaviorTracker:
    """Tracking du comportement utilisateur"""
    
    def __init__(self):
        self.user_sessions = defaultdict(lambda: {
            'start_time': time.time(),
            'actions': [],
            'generation_count': 0,
            'error_count': 0,
            'tier': 'free'
        })
    
    def track_action(self, user_id: str, action: str, details: dict = None):
        """Enregistre une action utilisateur"""
        session = self.user_sessions[user_id]
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details or {}
        }
        
        session['actions'].append(event)
        
        # Compteurs spécifiques
        if action == 'generate_letter':
            session['generation_count'] += 1
        elif action == 'error':
            session['error_count'] += 1
        
        logging.info(f"[USER] {user_id} - {action}")
    
    def get_user_analytics(self):
        """Analytics utilisateurs"""
        total_users = len(self.user_sessions)
        total_generations = sum(s['generation_count'] for s in self.user_sessions.values())
        
        # Calcul du funnel
        funnel = {
            'visited': total_users,
            'uploaded_cv': 0,
            'configured': 0,
            'generated': 0
        }
        
        for session in self.user_sessions.values():
            actions = [a['action'] for a in session['actions']]
            if 'upload_cv' in actions:
                funnel['uploaded_cv'] += 1
            if 'configured' in actions:
                funnel['configured'] += 1
            if 'generate_letter' in actions:
                funnel['generated'] += 1
        
        return {
            'total_users': total_users,
            'total_generations': total_generations,
            'avg_generations_per_user': total_generations / max(total_users, 1),
            'conversion_funnel': funnel,
            'tier_distribution': defaultdict(int)  # À implémenter
        }


# Instance globale du monitor
monitor = PerformanceMonitor()
security_auditor = SecurityAuditor()
user_tracker = UserBehaviorTracker()


# Intégration dans app.py
def integrate_monitoring(app_main_function):
    """Wrapper pour intégrer le monitoring dans l'app principale"""
    
    @functools.wraps(app_main_function)
    def monitored_app():
        # Sidebar monitoring
        with st.sidebar:
            if st.checkbox(" Monitoring Avancé", value=False):
                monitor.display_dashboard()
                
                # Security summary
                st.markdown("###  Sécurité")
                security_summary = security_auditor.get_security_summary()
                st.metric("Événements suspects", security_summary['suspicious_events'])
                
                # User analytics
                st.markdown("###  Analytics")
                analytics = user_tracker.get_user_analytics()
                st.metric("Utilisateurs actifs", analytics['total_users'])
                st.metric("Lettres générées", analytics['total_generations'])
        
        # Run main app
        app_main_function()
    
    return monitored_app


# Exemple d'utilisation dans vos services
"""
from services.monitoring import monitor, security_auditor, user_tracker

# Dans letter_service.py
 @monitor.track_performance('letter_generation')
def generer_lettre(request: LetterRequest) -> LetterResponse:
    # Audit sécurité
    security_auditor.audit_input('cv', request.cv_contenu)
    security_auditor.audit_input('annonce', request.annonce_contenu)
    
    # Votre code existant...
    
# Dans api_client.py
 @monitor.track_performance('gemini_api_call')
def suggerer_competences_transferables(ancien_domaine: str, nouveau_domaine: str) -> str:
    # Code existant...

 @monitor.track_performance('france_travail_api')
def get_france_travail_offer_details(offer_id: str) -> Optional[dict]:
    # Code existant...

# Dans app.py
if uploaded_cv:
    user_tracker.track_action(st.session_state.user_id, 'upload_cv')
"""

class AlertSystem:
    """Système d'alertes en temps réel"""
    
    @staticmethod
    def check_performance_alerts():
        """Vérifie et affiche les alertes de performance"""
        metrics = monitor.get_metrics_summary()
        
        alerts = []
        
        # Alerte taux d'erreur
        if metrics['error_rate'] > 0.1:  # >10%
            alerts.append({
                'level': 'error',
                'message': f"Taux d'erreur critique: {metrics['error_rate']*100:.1f}%",
                'action': "Vérifier les logs immédiatement"
            })
        
        # Alerte performance
        for component, stats in metrics['components'].items():
            if stats['requests'] > 0 and stats['avg_time'] > 10:
                alerts.append({
                    'level': 'warning',
                    'message': f"{component} très lent: {stats['avg_time']:.1f}s en moyenne",
                    'action': "Optimiser ou augmenter les ressources"
            })
        
        # Alerte sécurité
        security = security_auditor.get_security_summary()
        if security['suspicious_events'] > 10:
            alerts.append({
                'level': 'error',
                'message': f"{security['suspicious_events']} tentatives suspectes détectées",
                'action': "Analyser les patterns d'attaque"
            })
        
        # Affichage des alertes
        if alerts:
            st.markdown("###  Alertes Actives")
            for alert in alerts:
                if alert['level'] == 'error':
                    st.error(f"**{alert['message']}**\n\n {alert['action']}")
                else:
                    st.warning(f"**{alert['message']}**\n\n {alert['action']}")

def export_monitoring_data():
    """Exporte les données de monitoring"""
    
    if st.sidebar.button(" Exporter rapport", key="export_monitoring"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Compilation des données
        report_data = {
            'timestamp': timestamp,
            'performance_metrics': monitor.get_metrics_summary(),
            'security_audit': security_auditor.get_security_summary(),
            'user_analytics': user_tracker.get_user_analytics(),
            'system_info': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
        }
        
        # Export JSON
        json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            label=" Télécharger JSON",
            data=json_str,
            file_name=f"phoenix_monitoring_{timestamp}.json",
            mime="application/json"
        )
        
        # Génération rapport HTML
        html_report = generate_html_report(report_data)
        
        st.download_button(
            label=" Télécharger HTML",
            data=html_report,
            file_name=f"phoenix_report_{timestamp}.html",
            mime="text/html"
        )

def generate_html_report(data):
    """Génère un rapport HTML formaté"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Phoenix Letters - Rapport Monitoring</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .metric {{ 
                background: #f0f0f0; 
                padding: 10px; 
                margin: 5px;
                border-radius: 5px;
                display: inline-block;
            }}
            .alert {{ 
                background: #ffcccc; 
                padding: 10px; 
                margin: 10px 0;
                border-left: 5px solid #ff0000;
            }}
            .success {{ 
                background: #ccffcc; 
                border-left-color: #00ff00;
            }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <h1> Rapport de Monitoring - Phoenix Letters</h1>
        <p>Généré le: {data['timestamp']}</p>
        
        <h2>Performance Globale</h2>
        <div class="metric">
            <strong>Uptime:</strong> {data['performance_metrics']['uptime_seconds']/60:.0f} minutes
        </div>
        <div class="metric">
            <strong>Requêtes:</strong> {data['performance_metrics']['total_requests']}
        </div>
        <div class="metric">
            <strong>Erreurs:</strong> {data['performance_metrics']['total_errors']}
        </div>
        
        <h2>Performances par Composant</h2>
        <table>
            <tr>
                <th>Composant</th>
                <th>Requêtes</th>
                <th>Temps Moyen</th>
                <th>Erreurs</th>
            </tr>
    """
    
    for comp, stats in data['performance_metrics']['components'].items():
        html += f"""
            <tr>
                <td>{comp}</td>
                <td>{stats['requests']}</td>
                <td>{stats['avg_time']:.2f}s</td>
                <td>{stats['errors']}</td>
            </tr>
        """
    
    html += """
        </table>
        
        <h2>Sécurité</h2>
    """
    
    if data['security_audit']['suspicious_events'] > 0:
        html += f"""
        <div class="alert">
            ⚠️ {data['security_audit']['suspicious_events']} événements suspects détectés
        </div>
        """
    else:
        html += """
        <div class="alert success">
            ✅ Aucun événement suspect détecté
        </div>
        """
    
    html += f"""
        <h2>Analytics Utilisateurs</h2>
        <ul>
            <li>Utilisateurs actifs: {data['user_analytics']['total_users']}</li>
            <li>Lettres générées: {data['user_analytics']['total_generations']}</li>
            <li>Moyenne par utilisateur: {data['user_analytics']['avg_generations_per_user']:.1f}</li>
        </ul>
        
        <h2>Ressources Système</h2>
        <div class="metric">
            <strong>CPU:</strong> {data['system_info']['cpu_percent']}% 
        </div>
        <div class="metric">
            <strong>RAM:</strong> {data['system_info']['memory_percent']}% 
        </div>
        <div class="metric">
            <strong>Disque:</strong> {data['system_info']['disk_usage']}% 
        </div>
    </body>
    </html>
    """
    
    return html