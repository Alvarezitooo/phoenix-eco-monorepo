import hashlib
import json

def generate_cache_key(data: dict) -> str:
    """
    Génère une clé de cache unique à partir d'un dictionnaire de données.
    Utilise un hash SHA256 pour garantir l'unicité.
    """
    # Convertir le dictionnaire en une chaîne JSON triée pour une clé cohérente
    # ensure_ascii=False pour gérer les caractères non-ASCII correctement
    # separators=(',', ':') pour minimiser la taille de la chaîne JSON
    serialized_data = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(serialized_data.encode('utf-8')).hexdigest()

# Décorateur de cache simple pour les fonctions
# maxsize=128 signifie que les 128 dernières requêtes uniques seront mises en cache
# typed=False signifie que les arguments de types différents ne seront pas traités comme des entrées différentes
# (par exemple, 1 et 1.0 seraient traités comme la même entrée si typed=False)
# Pour notre cas, nous allons l'utiliser avec une clé générée manuellement.

# Nous n'allons pas utiliser lru_cache directement comme décorateur ici,
# mais plutôt la logique de génération de clé et une implémentation manuelle
# pour un contrôle plus fin sur la clé de cache.
