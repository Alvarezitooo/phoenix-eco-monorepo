import asyncio
import aiohttp
import time
import random
import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

class PhoenixLoadTester:
    """Tests de charge pour Phoenix Letters"""
    
    def __init__(self, base_url="http://localhost:8501"):
        self.base_url = base_url
        self.results = []
        
        # Données de test
        self.test_cvs = [
            "10 ans d'expérience en aide-soignant, gestion d'équipe de 5 personnes",
            "Commercial B2B pendant 15 ans, CA généré 2M€/an",
            "Professeur de mathématiques, 20 ans Education Nationale",
            "Manager retail, gestion de 3 magasins, 50 employés"
        ]
        
        self.test_annonces = [
            "Recherche développeur Python junior motivé",
            "Pentester junior pour start-up cybersécurité",
            "Data analyst avec esprit analytique",
            "Chef de projet digital transformation"
        ]
    
    async def simulate_user_session(self, session_id: int):
        """Simule une session utilisateur complète"""
        start_time = time.time()
        errors = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # 1. Page d'accueil
                async with session.get(self.base_url) as resp:
                    if resp.status != 200:
                        errors.append(f"Home page error: {resp.status}")
                
                # 2. Simulation upload CV (POST simulé)
                cv_content = random.choice(self.test_cvs)
                annonce_content = random.choice(self.test_annonces)
                
                # 3. Génération lettre (simulation API call)
                generation_start = time.time()
                
                # Simuler le délai de génération
                await asyncio.sleep(random.uniform(2, 5))
                
                generation_time = time.time() - generation_start
                
                # Résultats
                result = {
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'total_time': time.time() - start_time,
                    'generation_time': generation_time,
                    'errors': errors,
                    'success': len(errors) == 0
                }
                
                self.results.append(result)
                
        except Exception as e:
            self.results.append({
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'total_time': time.time() - start_time,
                'generation_time': 0,
                'errors': [str(e)],
                'success': False
            })
    
    async def run_load_test(self, num_users=10, ramp_up_time=10):
        """Execute le test de charge"""
        print(f" Démarrage test de charge: {num_users} utilisateurs sur {ramp_up_time}s")
        
        tasks = []
        
        for i in range(num_users):
            # Ramp-up progressif
            delay = (i / num_users) * ramp_up_time
            task = self.schedule_user(i, delay)
            tasks.append(task)
        
        # Attendre toutes les sessions
        await asyncio.gather(*tasks)
        
        print(f"✅ Test terminé: {len(self.results)} sessions")
        
    async def schedule_user(self, session_id: int, delay: float):
        """Schedule un utilisateur avec délai"""
        await asyncio.sleep(delay)
        await self.simulate_user_session(session_id)
    
    def analyze_results(self):
        """Analyse les résultats du test"""
        if not self.results:
            print("Aucun résultat à analyser")
            return
        
        df = pd.DataFrame(self.results)
        
        # Métriques globales
        total_sessions = len(df)
        successful_sessions = df['success'].sum()
        success_rate = (successful_sessions / total_sessions) * 100
        
        # Temps de réponse
        avg_total_time = df['total_time'].mean()
        p95_total_time = df['total_time'].quantile(0.95)
        p99_total_time = df['total_time'].quantile(0.99)
        
        # Temps de génération
        successful_df = df[df['success']]
        if not successful_df.empty:
            avg_generation_time = successful_df['generation_time'].mean()
            p95_generation_time = successful_df['generation_time'].quantile(0.95)
        else:
            avg_generation_time = p95_generation_time = 0
        
        # Rapport
        report = f"""
 RAPPORT DE TEST DE CHARGE - PHOENIX LETTERS
================================================

 Résumé Exécutif:
• Sessions totales: {total_sessions}
• Sessions réussies: {successful_sessions} ({success_rate:.1f}%)
• Taux d'erreur: {100 - success_rate:.1f}%

⏱️ Performances:
• Temps total moyen: {avg_total_time:.2f}s
• P95 temps total: {p95_total_time:.2f}s
• P99 temps total: {p99_total_time:.2f}s

✨ Génération IA:
• Temps moyen: {avg_generation_time:.2f}s
• P95 génération: {p95_generation_time:.2f}s

 Erreurs détectées:
"""
        
        # Analyse des erreurs
        error_types = {}
        for result in self.results:
            for error in result['errors']:
                error_type = error.split(':')[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            report += f"• {error_type}: {count} occurrences\n"
        
        return report, df
    
    def generate_charts(self, df):
        """Génère des graphiques de performance"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Distribution temps de réponse
        ax1.hist(df['total_time'], bins=20, alpha=0.7, color='blue')
        ax1.axvline(df['total_time'].mean(), color='red', linestyle='--', label='Moyenne')
        ax1.set_title('Distribution Temps de Réponse Total')
        ax1.set_xlabel('Temps (s)')
        ax1.set_ylabel('Fréquence')
        ax1.legend()
        
        # 2. Temps de réponse dans le temps
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        ax2.scatter(df['timestamp'], df['total_time'], alpha=0.6)
        ax2.set_title('Temps de Réponse au Fil du Test')
        ax2.set_xlabel('Temps')
        ax2.set_ylabel('Temps de réponse (s)')
        
        # 3. Taux de succès cumulé
        df['cumulative_success_rate'] = df['success'].expanding().mean() * 100
        ax3.plot(df.index, df['cumulative_success_rate'])
        ax3.set_title('Taux de Succès Cumulé')
        ax3.set_xlabel('Nombre de sessions')
        ax3.set_ylabel('Taux de succès (%)')
        ax3.set_ylim(0, 105)
        
        # 4. Comparaison temps génération vs total
        successful_df = df[df['success']]
        if not successful_df.empty:
            ax4.scatter(successful_df['generation_time'], successful_df['total_time'], alpha=0.6)
            ax4.set_title('Temps Génération vs Temps Total')
            ax4.set_xlabel('Temps génération (s)')
            ax4.set_ylabel('Temps total (s)')
        
        plt.tight_layout()
        return fig


class MemoryLeakDetector:
    """Détection de fuites mémoire"""
    
    def __init__(self):
        self.memory_snapshots = []
    
    def take_snapshot(self, label: str):
        """Prend un snapshot mémoire"""
        import tracemalloc
        
        snapshot = tracemalloc.take_snapshot()
        self.memory_snapshots.append({
            'label': label,
            'timestamp': datetime.now().isoformat(),
            'snapshot': snapshot
        })
    
    def analyze_growth(self):
        """Analyse la croissance mémoire"""
        if len(self.memory_snapshots) < 2:
            return "Pas assez de snapshots pour analyser"
        
        first = self.memory_snapshots[0]['snapshot']
        last = self.memory_snapshots[-1]['snapshot']
        
        # Top différences
        top_stats = last.compare_to(first, 'lineno')
        
        report = "TOP 10 CROISSANCE MÉMOIRE:\n"
        report += "=" * 50 + "\n"
        
        for stat in top_stats[:10]:
            report += f"{stat}\n"
        
        return report


# Script de test principal
async def main():
    """Execute une suite complète de tests"""
    
    print(" AUDIT DYNAMIQUE PHOENIX LETTERS")
    print("=" * 50)
    
    # 1. Test de charge léger
    print("\n Test de charge (10 utilisateurs simultanés)...")
    tester = PhoenixLoadTester()
    await tester.run_load_test(num_users=10, ramp_up_time=5)
    
    report, df = tester.analyze_results()
    print(report)
    
    # 2. Test de stress
    print("\n Test de stress (50 utilisateurs)...")
    stress_tester = PhoenixLoadTester()
    await stress_tester.run_load_test(num_users=50, ramp_up_time=10)
    
    stress_report, stress_df = stress_tester.analyze_results()
    print(stress_report)
    
    # 3. Comparaison
    print("\n COMPARAISON CHARGE vs STRESS:")
    print(f"• Dégradation temps réponse: {(stress_df['total_time'].mean() / df['total_time'].mean() - 1) * 100:.1f}%")
    print(f"• Baisse taux succès: {df['success'].mean() * 100:.1f}% → {stress_df['success'].mean() * 100:.1f}%")
    
    # Génération graphiques
    fig = tester.generate_charts(df)
    fig.savefig('phoenix_load_test_results.png')
    print("\n Graphiques sauvegardés: phoenix_load_test_results.png")


if __name__ == "__main__":
    asyncio.run(main())
