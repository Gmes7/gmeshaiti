import json
import sqlite3
from datetime import datetime
import os


class OfflineManager:
    def __init__(self):
        self.db_path = "gmes_offline.db"
        self.init_offline_db()

    def init_offline_db(self):
        """Initialise la base de données hors ligne"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table pour les données en attente de synchronisation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced BOOLEAN DEFAULT FALSE
            )
        ''')

        # Cache des données
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_data (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def save_offline_operation(self, operation_type, data):
        """Sauvegarde une opération pour synchronisation ultérieure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO pending_operations (operation_type, data)
            VALUES (?, ?)
        ''', (operation_type, json.dumps(data)))

        conn.commit()
        conn.close()

        return cursor.lastrowid

    def get_pending_operations(self):
        """Récupère les opérations en attente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, operation_type, data, created_at 
            FROM pending_operations 
            WHERE synced = FALSE
            ORDER BY created_at
        ''')

        operations = []
        for row in cursor.fetchall():
            operations.append({
                'id': row[0],
                'type': row[1],
                'data': json.loads(row[2]),
                'created_at': row[3]
            })

        conn.close()
        return operations

    def mark_operation_synced(self, operation_id):
        """Marque une opération comme synchronisée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE pending_operations 
            SET synced = TRUE 
            WHERE id = ?
        ''', (operation_id,))

        conn.commit()
        conn.close()

    def cache_data(self, key, value):
        """Met en cache des données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO cache_data (key, value)
            VALUES (?, ?)
        ''', (key, json.dumps(value)))

        conn.commit()
        conn.close()

    def get_cached_data(self, key, max_age_hours=24):
        """Récupère des données du cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT value, updated_at 
            FROM cache_data 
            WHERE key = ? AND datetime(updated_at) > datetime('now', ?)
        ''', (key, f'-{max_age_hours} hours'))

        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def sync_with_server(self, api_base_url, token):
        """Synchronise les données avec le serveur"""
        pending_ops = self.get_pending_operations()
        successful_syncs = 0

        for op in pending_ops:
            try:
                # Envoyer l'opération au serveur
                response = requests.post(
                    f"{api_base_url}/sync/operation",
                    headers={"Authorization": f"Bearer {token}"},
                    json=op
                )

                if response.status_code == 200:
                    self.mark_operation_synced(op['id'])
                    successful_syncs += 1

            except Exception as e:
                print(f"Erreur sync opération {op['id']}: {e}")

        return successful_syncs, len(pending_ops)


# Instance globale
offline_manager = OfflineManager()