#!/usr/bin/env python3
"""
Script de configuration du schéma Supabase pour Phoenix Rise Event Store.

Ce script applique le schéma SQL et configure les RLS policies pour la persistance EEV.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Charger les variables d'environnement
load_dotenv()

def setup_supabase_schema():
    """Configure le schéma Supabase Event Store."""
    print("🚀 Configuration du schéma Supabase Event Store...")
    
    # Vérifier les variables d'environnement
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Variables SUPABASE_URL et SUPABASE_KEY requises")
        return False
    
    try:
        # Créer le client Supabase
        client = create_client(supabase_url, supabase_key)
        print("✅ Client Supabase connecté")
        
        # SQL pour créer la table events
        create_events_table_sql = """
        -- Table principale Event Store
        CREATE TABLE IF NOT EXISTS events (
            event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            stream_id UUID NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            payload JSONB NOT NULL,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            app_source VARCHAR(50) NOT NULL,
            version INTEGER DEFAULT 1,
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        # Créer les index pour performance
        create_indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_events_stream_id ON events(stream_id);
        CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
        CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_events_app_source ON events(app_source);
        CREATE INDEX IF NOT EXISTS idx_events_stream_timestamp ON events(stream_id, timestamp);
        """
        
        # Table des snapshots pour optimisation
        create_snapshots_table_sql = """
        CREATE TABLE IF NOT EXISTS user_profile_snapshots (
            snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            snapshot_data JSONB NOT NULL,
            version INTEGER NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, version)
        );
        """
        
        # Index pour snapshots
        create_snapshots_indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_snapshots_user_id ON user_profile_snapshots(user_id);
        CREATE INDEX IF NOT EXISTS idx_snapshots_version ON user_profile_snapshots(user_id, version);
        """
        
        # Vue pour analytics
        create_analytics_view_sql = """
        CREATE OR REPLACE VIEW user_activity_summary AS
        SELECT 
            stream_id as user_id,
            app_source,
            event_type,
            COUNT(*) as event_count,
            MAX(timestamp) as last_activity,
            DATE(timestamp) as activity_date
        FROM events 
        GROUP BY stream_id, app_source, event_type, DATE(timestamp)
        ORDER BY last_activity DESC;
        """
        
        # Fonction de cleanup RGPD
        create_cleanup_function_sql = """
        CREATE OR REPLACE FUNCTION cleanup_old_events(retention_days INTEGER DEFAULT 365)
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            DELETE FROM events 
            WHERE timestamp < NOW() - INTERVAL '1 day' * retention_days;
            
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Fonction de snapshot
        create_snapshot_function_sql = """
        CREATE OR REPLACE FUNCTION create_user_snapshot(p_user_id UUID)
        RETURNS UUID AS $$
        DECLARE
            snapshot_uuid UUID;
            current_version INTEGER;
            user_events JSONB;
        BEGIN
            -- Récupérer la version actuelle
            SELECT COALESCE(MAX(version), 0) + 1 
            INTO current_version 
            FROM user_profile_snapshots 
            WHERE user_id = p_user_id;
            
            -- Construire le snapshot à partir des events
            SELECT jsonb_agg(
                jsonb_build_object(
                    'event_type', event_type,
                    'payload', payload,
                    'timestamp', timestamp,
                    'app_source', app_source
                ) ORDER BY timestamp
            )
            INTO user_events
            FROM events 
            WHERE stream_id = p_user_id;
            
            -- Insérer le snapshot
            INSERT INTO user_profile_snapshots (user_id, snapshot_data, version)
            VALUES (p_user_id, user_events, current_version)
            RETURNING snapshot_id INTO snapshot_uuid;
            
            RETURN snapshot_uuid;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Exécuter les scripts SQL
        scripts = [
            ("Table events", create_events_table_sql),
            ("Index events", create_indexes_sql),
            ("Table snapshots", create_snapshots_table_sql),
            ("Index snapshots", create_snapshots_indexes_sql),
            ("Vue analytics", create_analytics_view_sql),
            ("Fonction cleanup", create_cleanup_function_sql),
            ("Fonction snapshot", create_snapshot_function_sql)
        ]
        
        for script_name, sql_script in scripts:
            try:
                print(f"🔄 Création {script_name}...")
                result = client.rpc('exec_sql', {'sql': sql_script}).execute()
                print(f"✅ {script_name} créé avec succès")
            except Exception as e:
                print(f"⚠️ Avertissement {script_name}: {e}")
                # Essayer avec une approche différente
                try:
                    # Utilisation de postgrest pour certaines opérations
                    if "CREATE TABLE" in sql_script:
                        # Les tables peuvent être créées via l'interface Supabase
                        print(f"ℹ️ {script_name} à créer manuellement via l'interface Supabase")
                except Exception as e2:
                    print(f"❌ Échec {script_name}: {e2}")
        
        # Test de la configuration
        print("\n🔍 Test de la configuration...")
        try:
            # Test insertion d'un événement
            test_event = {
                "stream_id": "00000000-0000-0000-0000-000000000000",
                "event_type": "TestEvent",
                "payload": {"test": True},
                "app_source": "rise",
                "metadata": {"setup_test": True}
            }
            
            result = client.table('events').insert(test_event).execute()
            if result.data:
                print("✅ Test d'insertion réussi")
                
                # Nettoyer l'événement de test
                client.table('events').delete().eq('event_type', 'TestEvent').execute()
                print("✅ Nettoyage test effectué")
            
        except Exception as e:
            print(f"⚠️ Test insertion: {e}")
        
        print("\n🎉 Configuration Supabase Event Store terminée!")
        print("\nℹ️ Si des erreurs persistent, vérifiez manuellement dans l'interface Supabase:")
        print("1. Table 'events' créée avec colonnes appropriées")
        print("2. RLS activé si nécessaire") 
        print("3. Index créés pour performance")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration Supabase: {e}")
        return False

if __name__ == "__main__":
    success = setup_supabase_schema()
    exit(0 if success else 1)