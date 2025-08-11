## Instructions de Validation de l'Étape 2 : Construire le Pont (API)

Pour valider l'implémentation de l'API Dojo Mental, suivez les étapes ci-dessous :

1.  **Installation des dépendances :**
    Ouvrez votre terminal, naviguez vers le répertoire `apps/phoenix-iris-api/` et exécutez la commande suivante :
    ```bash
    pip install fastapi uvicorn supabase
    ```

2.  **Configuration des variables d'environnement :**
    Créez un fichier nommé `.env` dans le répertoire `apps/phoenix-iris-api/` avec le contenu suivant (remplacez les placeholders par vos vraies clés Supabase) :

    ```
    SUPABASE_URL="VOTRE_URL_SUPABASE"
    SUPABASE_KEY="VOTRE_CLE_ANON_SUPABASE"
    ```

    **Note importante :** Ne committez jamais ce fichier `.env` dans votre dépôt Git ! Assurez-vous qu'il est bien listé dans votre `.gitignore`.

3.  **Lancement de l'API :**
    Ouvrez un terminal, naviguez vers le répertoire `apps/phoenix-iris-api/` et exécutez la commande suivante :

    ```bash
    uvicorn dojo_api:app --reload
    ```
    Vous devriez voir l'API démarrer, généralement sur `http://127.0.0.1:8000`.

4.  **Test des endpoints :**
    Une fois l'API lancée, vous pouvez accéder à la documentation interactive (Swagger UI) à l'adresse `http://127.0.0.1:8000/docs`.

    Utilisez cette interface pour tester les endpoints :

    *   **`POST /kaizen` :** Créez un nouveau Kaizen.
        *   Exemple de corps de requête :
            ```json
            {
              "user_id": "votre_uuid_utilisateur",
              "action": "Méditer 5 minutes",
              "date": "2025-08-07",
              "completed": false
            }
            ```
    *   **`PUT /kaizen/{kaizen_id}` :** Mettez à jour un Kaizen existant (utilisez l'ID retourné par le POST).
        *   Exemple de corps de requête :
            ```json
            {
              "completed": true
            }
            ```
    *   **`GET /kaizen/{user_id}` :** Récupérez tous les Kaizen d'un utilisateur.
    *   **`POST /zazen-session` :** Enregistrez une nouvelle session Zazen.
        *   Exemple de corps de requête :
            ```json
            {
              "user_id": "votre_uuid_utilisateur",
              "timestamp": "2025-08-07T10:00:00Z",
              "duration": 120,
              "triggered_by": "iris"
            }
            ```

**Validation :**

Confirmez que vous avez pu :
*   Installer les dépendances.
*   Configurer les variables d'environnement.
*   Lancer l'API sans erreur.
*   Tester avec succès chaque endpoint via la documentation Swagger UI, et que les données sont bien enregistrées/récupérées dans votre base de données Supabase.

---

## Instructions de Validation de l'Étape 4 : Donner la Voix (UI & Dialogues)

Pour valider l'implémentation de l'interface utilisateur du Dojo Mental, suivez les étapes ci-dessous :

1.  **Intégration du composant `DojoMental` :**
    Ouvrez le fichier `apps/phoenix-rise/app/page.tsx` (ou la page où vous souhaitez l'intégrer) et ajoutez l'import et l'utilisation du composant `DojoMental`.

    ```typescript
    // apps/phoenix-rise/app/page.tsx (exemple)
    'use client'; // Assurez-vous que la page est un Client Component si elle ne l'est pas déjà

    import DojoMental from '../components/DojoMental/DojoMental';

    export default function HomePage() {
      // Remplacez 'some_user_id' par un ID utilisateur réel ou simulé
      const userId = "user_12345"; 
      return (
        <main className="flex min-h-screen flex-col items-center justify-between p-24">
          <DojoMental userId={userId} />
        </main>
      );
    }
    ```

2.  **Configuration des variables d'environnement pour Next.js :**
    Créez un fichier `.env.local` dans le répertoire `apps/phoenix-rise/` (ou `apps/phoenix-website/` si c'est là que votre Next.js est) avec :
    ```
    NEXT_PUBLIC_DOJO_API_URL="http://127.0.0.1:8000"
    ```
    (Adaptez l'URL si votre API FastAPI tourne sur un port différent ou une adresse différente).

3.  **Lancement de l'application Next.js :**
    Naviguez vers le répertoire `apps/phoenix-rise/` et exécutez :
    ```bash
    npm run dev
    ```

4.  **Vérification visuelle et fonctionnelle :**
    Ouvrez votre navigateur à l'adresse indiquée par `npm run dev` (généralement `http://localhost:3000`).

    *   Assurez-vous que le `ZazenTimer` et le `KaizenGrid` s'affichent correctement. Le `KaizenGrid` devrait maintenant afficher les données réelles de votre base de données Supabase.
    *   Testez l'interactivité :
        *   Entrez un Kaizen et cliquez sur "Enregistrer mon Kaizen". Vérifiez que le dialogue change, l'input se vide, et **surtout, que le Kaizen apparaît dans votre base de données Supabase et se rafraîchit dans la grille après un court délai (ou un rafraîchissement manuel de la page pour l'instant)**.
        *   Cliquez sur une cellule du KaizenGrid. Vérifiez que son état visuel change et que la modification est **réfléchie dans votre base de données Supabase**.
        *   Cliquez sur "Commencer un Zazen de 2 minutes". Vérifiez que le dialogue change et qu'une nouvelle session Zazen est **enregistrée dans votre base de données Supabase**.
