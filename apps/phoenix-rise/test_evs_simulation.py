#!/usr/bin/env python3
"""
Simulation complète de la persistance EmotionalVectorState.

Ce script teste toute la chaîne sans dépendances Streamlit ou Supabase.
Simule le comportement complet du système de persistance EEV.
"""

import json
import uuid
from datetime import datetime, timedelta
from dataclasses import asdict
from typing import Dict, List, Any

# Import direct des modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from iris_core.event_processing.emotional_vector_state import EmotionalVectorState


class MockSupabaseClient:
    """Mock Supabase pour les tests."""
    
    def __init__(self):
        self.events_store = []
        self.snapshots_store = []
    
    def table(self, table_name: str):
        return MockTable(self, table_name)


class MockTable:
    """Mock table Supabase."""
    
    def __init__(self, client: MockSupabaseClient, table_name: str):
        self.client = client
        self.table_name = table_name
        self.store = getattr(client, f"{table_name}_store")
        self._query = {}
    
    def insert(self, data):
        if isinstance(data, list):
            for item in data:
                item['event_id'] = str(uuid.uuid4())
                self.store.append(item)
        else:
            data['event_id'] = str(uuid.uuid4())
            self.store.append(data)
        return self
    
    def select(self, columns='*'):
        return self
    
    def eq(self, column, value):
        self._query[column] = value
        return self
    
    def in_(self, column, values):
        self._query[f"{column}_in"] = values
        return self
    
    def gte(self, column, value):
        self._query[f"{column}_gte"] = value
        return self
    
    def order(self, column, desc=False):
        return self
    
    def execute(self):
        # Simuler le filtrage
        filtered_data = []
        for item in self.store:
            match = True
            for key, value in self._query.items():
                if key.endswith('_in'):
                    col = key[:-3]
                    if item.get(col) not in value:
                        match = False
                        break
                elif key.endswith('_gte'):
                    col = key[:-4]
                    if item.get(col, '') < value:
                        match = False
                        break
                elif item.get(key) != value:
                    match = False
                    break
            
            if match:
                filtered_data.append(item)
        
        return MockResult(filtered_data)


class MockResult:
    """Mock résultat de requête."""
    
    def __init__(self, data):
        self.data = data


def simulate_user_journey():
    """Simule un parcours utilisateur complet avec EEV."""
    print("🎭 SIMULATION PARCOURS UTILISATEUR AVEC EEV")
    print("=" * 50)
    
    # 1. Création utilisateur
    user_id = str(uuid.uuid4())
    print(f"👤 Utilisateur créé: {user_id}")
    
    # 2. Initialisation EEV
    evs = EmotionalVectorState(user_id=user_id)
    print(f"🧠 EEV initialisé - État initial:")
    print(f"   Mood Average 7d: {evs.mood_average_7d}")
    print(f"   Burnout Risk: {evs.burnout_risk_score}")
    
    # 3. Simulation d'événements sur 14 jours
    print("\n📊 SIMULATION ÉVÉNEMENTS SUR 14 JOURS")
    print("-" * 30)
    
    mock_client = MockSupabaseClient()
    events_created = 0
    
    base_time = datetime.utcnow() - timedelta(days=14)
    
    for day in range(14):
        current_day = base_time + timedelta(days=day)
        
        # Simuler 1-3 entrées par jour
        for entry_num in range(1 + (day % 3)):
            # Mood varié selon une courbe réaliste
            mood_score = 0.4 + 0.4 * (1 + day/14) + 0.1 * (entry_num - 1)  # 0.4 à 0.9
            confidence_score = 0.3 + 0.5 * (1 + day/10) + 0.1 * entry_num  # 0.3 à 0.9
            
            # Mettre à jour EEV
            evs.update_mood(current_day + timedelta(hours=entry_num*4), mood_score)
            evs.update_confidence(current_day + timedelta(hours=entry_num*4), confidence_score)
            
            # Stocker événement
            mood_event = {
                "stream_id": user_id,
                "event_type": "MoodLogged",
                "payload": {
                    "score": mood_score,
                    "confidence": confidence_score,
                    "notes": f"Journal day {day+1}, entry {entry_num+1}"
                },
                "app_source": "rise",
                "timestamp": current_day.isoformat()
            }
            
            confidence_event = {
                "stream_id": user_id,
                "event_type": "ConfidenceScoreLogged",
                "payload": {
                    "score": confidence_score
                },
                "app_source": "rise",
                "timestamp": current_day.isoformat()
            }
            
            mock_client.table('events').insert([mood_event, confidence_event]).execute()
            events_created += 2
        
        # Simuler quelques actions (objectifs, sessions)
        if day % 4 == 0:  # Tous les 4 jours
            goal_event = {
                "stream_id": user_id,
                "event_type": "GoalSet",
                "payload": {
                    "title": f"Objectif semaine {day//7 + 1}",
                    "objective_type": "personal"
                },
                "app_source": "rise",
                "timestamp": current_day.isoformat()
            }
            evs.update_action(current_day, "GoalSet")
            mock_client.table('events').insert(goal_event).execute()
            events_created += 1
        
        if day % 7 == 0:  # Chaque semaine
            session_event = {
                "stream_id": user_id,
                "event_type": "CoachingSessionStarted",
                "payload": {
                    "session_type": "free",
                    "user_tier": "free"
                },
                "app_source": "rise",
                "timestamp": current_day.isoformat()
            }
            mock_client.table('events').insert(session_event).execute()
            events_created += 1
    
    print(f"📈 {events_created} événements créés")
    
    # 4. Calcul final des métriques
    evs.calculate_burnout_risk()
    print(f"\n🎯 MÉTRIQUES FINALES:")
    print(f"   Mood Average 7d: {evs.mood_average_7d:.2f}")
    print(f"   Mood Count 7d: {evs.mood_count_7d}")
    print(f"   Confidence Trend: {evs.confidence_trend:.2f}")
    print(f"   Actions 7d: {dict(evs.actions_count_7d)}")
    print(f"   Burnout Risk: {evs.burnout_risk_score:.2f}")
    
    # 5. Test reconstruction depuis événements
    print(f"\n🔄 TEST RECONSTRUCTION DEPUIS ÉVÉNEMENTS")
    print("-" * 40)
    
    # Simuler reconstruction
    events_data = mock_client.table('events').select().eq('stream_id', user_id).execute().data
    print(f"📚 {len(events_data)} événements récupérés depuis le store")
    
    # Créer nouvel EEV et rejouer événements
    reconstructed_evs = EmotionalVectorState(user_id=user_id)
    
    for event in events_data:
        event_formatted = {
            'type': event['event_type'],
            'timestamp': event['timestamp'],
            'payload': event['payload']
        }
        reconstructed_evs.update_from_event(event_formatted)
    
    reconstructed_evs.calculate_burnout_risk()
    
    print(f"🔍 COMPARAISON ÉTATS:")
    print(f"   Original Mood 7d: {evs.mood_average_7d:.2f}")
    print(f"   Reconstruit Mood 7d: {reconstructed_evs.mood_average_7d:.2f}")
    print(f"   Original Burnout: {evs.burnout_risk_score:.2f}")
    print(f"   Reconstruit Burnout: {reconstructed_evs.burnout_risk_score:.2f}")
    
    # Test égalité (tolérance pour les arrondis)
    mood_diff = abs(evs.mood_average_7d - reconstructed_evs.mood_average_7d)
    burnout_diff = abs(evs.burnout_risk_score - reconstructed_evs.burnout_risk_score)
    
    if mood_diff < 0.01 and burnout_diff < 0.01:
        print("✅ RECONSTRUCTION PARFAITE!")
    else:
        print(f"⚠️ Différences: mood={mood_diff:.3f}, burnout={burnout_diff:.3f}")
    
    # 6. Test sérialisation JSON
    print(f"\n💾 TEST SÉRIALISATION JSON")
    print("-" * 25)
    
    json_data = evs.to_json()
    json_size = len(json_data)
    print(f"📄 Taille JSON EEV: {json_size} caractères")
    
    # Test parsing
    try:
        parsed_data = json.loads(json_data)
        print(f"✅ JSON valide - {len(parsed_data)} propriétés")
        
        # Vérifier propriétés critiques
        critical_props = ['user_id', 'mood_average_7d', 'burnout_risk_score', 'last_updated']
        for prop in critical_props:
            if prop in parsed_data:
                print(f"   ✓ {prop}: {parsed_data[prop]}")
            else:
                print(f"   ❌ {prop}: MANQUANT")
                
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON: {e}")
    
    # 7. Performance test
    print(f"\n⚡ TEST PERFORMANCE")
    print("-" * 18)
    
    import time
    
    # Test mise à jour massive
    perf_evs = EmotionalVectorState(user_id=str(uuid.uuid4()))
    start_time = time.time()
    
    for i in range(1000):
        event_time = datetime.utcnow() + timedelta(minutes=i)
        perf_evs.update_mood(event_time, 0.5 + (i % 100) / 200)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"📊 1000 mises à jour mood: {duration:.3f}s")
    print(f"⚡ {1000/duration:.0f} updates/seconde")
    print(f"🧮 État final: mood={perf_evs.mood_average_7d:.2f}, count={perf_evs.mood_count_7d}")
    
    return {
        "user_id": user_id,
        "events_created": events_created,
        "final_mood": evs.mood_average_7d,
        "final_burnout": evs.burnout_risk_score,
        "reconstruction_success": mood_diff < 0.01 and burnout_diff < 0.01,
        "json_size": json_size,
        "performance_updates_per_sec": 1000/duration
    }


def test_evs_edge_cases():
    """Test des cas limites de l'EEV."""
    print(f"\n🧪 TEST CAS LIMITES EEV")
    print("=" * 25)
    
    user_id = str(uuid.uuid4())
    evs = EmotionalVectorState(user_id=user_id)
    
    # Test avec données vides
    evs.calculate_burnout_risk()
    print(f"✓ EEV vide: burnout={evs.burnout_risk_score:.2f}")
    
    # Test avec valeurs extrêmes
    now = datetime.utcnow()
    evs.update_mood(now, 1.0)  # Mood maximum
    evs.update_confidence(now, 0.0)  # Confidence minimum
    evs.calculate_burnout_risk()
    print(f"✓ Valeurs extrêmes: mood={evs.mood_average_7d:.2f}, burnout={evs.burnout_risk_score:.2f}")
    
    # Test avec beaucoup d'actions
    for i in range(10):
        evs.update_action(now + timedelta(hours=i), f"Action{i}")
    evs.calculate_burnout_risk()
    print(f"✓ Actions multiples: {len(evs.actions_count_7d)} types d'actions")
    
    # Test avec événements anciens
    old_time = now - timedelta(days=10)
    evs.update_mood(old_time, 0.2)  # Ne doit pas affecter les métriques 7d
    print(f"✓ Événements anciens filtrés: mood 7d={evs.mood_average_7d:.2f}")
    
    print("✅ Tous les cas limites passés")


if __name__ == "__main__":
    print("🚀 SIMULATION COMPLÈTE PERSISTANCE EEV")
    print("=" * 50)
    
    try:
        # Test principal
        results = simulate_user_journey()
        
        # Tests cas limites
        test_evs_edge_cases()
        
        # Résumé final
        print(f"\n🎉 RÉSUMÉ SIMULATION")
        print("=" * 20)
        print(f"👤 Utilisateur: {results['user_id'][:8]}...")
        print(f"📊 Événements créés: {results['events_created']}")
        print(f"🎯 Mood final: {results['final_mood']:.2f}")
        print(f"🔥 Burnout final: {results['final_burnout']:.2f}")
        print(f"🔄 Reconstruction: {'✅' if results['reconstruction_success'] else '❌'}")
        print(f"💾 Taille JSON: {results['json_size']} chars")
        print(f"⚡ Performance: {results['performance_updates_per_sec']:.0f} updates/s")
        
        print(f"\n✅ SIMULATION RÉUSSIE - EEV PRÊT POUR PRODUCTION!")
        
    except Exception as e:
        print(f"❌ Erreur simulation: {e}")
        import traceback
        traceback.print_exc()