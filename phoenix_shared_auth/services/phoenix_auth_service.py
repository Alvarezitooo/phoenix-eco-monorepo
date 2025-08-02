"""
🚀 Phoenix Auth Service - Service d'authentification unifié
Gère l'authentification pour tout l'écosystème Phoenix (Letters, CV, Rise)
"""

import traceback
import uuid
from datetime import datetime
from typing import Optional, Tuple

import bcrypt

from ..database.phoenix_db_connection import PhoenixDatabaseConnection
from ..entities.phoenix_user import (
    AppUsageStats,
    PhoenixApp,
    PhoenixSubscription,
    PhoenixUser,
    UserTier,
)


class PhoenixAuthService:
    """
    Service d'authentification unifié pour l'écosystème Phoenix
    Gère les utilisateurs, sessions et permissions multi-applications
    """

    def __init__(self, db_connection: PhoenixDatabaseConnection, jwt_manager):
        self.db_connection = db_connection
        self.jwt_manager = jwt_manager
        self.client = db_connection.get_client()

    def register_user(
        self,
        email: str,
        password: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        newsletter_opt_in: bool = False,
        source_app: PhoenixApp = PhoenixApp.LETTERS,
    ) -> PhoenixUser:
        """
        Enregistre un nouvel utilisateur Phoenix

        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            username: Nom d'utilisateur optionnel
            first_name: Prénom optionnel
            last_name: Nom optionnel
            newsletter_opt_in: Consentement newsletter
            source_app: Application source de l'inscription

        Returns:
            PhoenixUser: Utilisateur créé
        """
        # Vérifier si l'utilisateur existe déjà
        response = self.client.from_("users").select("id").eq("email", email).execute()
        if response.data:
            raise ValueError(f"L'utilisateur avec l'email {email} existe déjà.")

        # Hacher le mot de passe
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        try:
            # Créer l'utilisateur dans Supabase
            user_data = {
                "email": email,
                "password_hash": hashed_password,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "newsletter_opt_in": newsletter_opt_in,
                "status": "active",  # Activé directement pour simplifier
                "created_at": datetime.utcnow().isoformat(),
            }

            response = self.client.from_("users").insert(user_data).execute()

            if not response.data:
                raise Exception("La création de l'utilisateur a échoué")

            user_record = response.data[0]

            # Créer l'abonnement par défaut
            subscription_data = {
                "user_id": user_record["id"],
                "current_tier": UserTier.FREE.value,
                "enabled_apps": [source_app.value],  # App source activée
                "created_at": datetime.utcnow().isoformat(),
            }

            self.client.from_("user_subscriptions").insert(subscription_data).execute()

            # Créer les statistiques initiales pour l'app source
            stats_data = {
                "user_id": user_record["id"],
                "app": source_app.value,
                "letters_generated": 0,
                "cvs_created": 0,
                "coaching_sessions": 0,
                "last_activity": datetime.utcnow().isoformat(),
            }

            self.client.from_("app_usage_stats").insert(stats_data).execute()

            # Créer et retourner l'entité PhoenixUser
            return self._build_phoenix_user(user_record, source_app)

        except Exception as e:
            raise Exception(f"Erreur lors de la création de l'utilisateur: {e}")

    def authenticate_user(
        self, email: str, password: str, app: PhoenixApp = PhoenixApp.LETTERS
    ) -> Tuple[PhoenixUser, str, str]:
        """
        Authentifie un utilisateur et retourne l'utilisateur avec les tokens

        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            app: Application demandant l'authentification

        Returns:
            Tuple[PhoenixUser, str, str]: Utilisateur, access_token, refresh_token
        """
        # Récupérer l'utilisateur avec ses données complètes
        response = (
            self.client.from_("users")
            .select(
                """
                *, 
                user_subscriptions(*),
                app_usage_stats(*)
            """
            )
            .eq("email", email)
            .execute()
        )

        if not response.data:
            raise ValueError(f"Aucun utilisateur trouvé avec l'email {email}")

        user_record = response.data[0]

        # Vérifier le mot de passe
        if not bcrypt.checkpw(
            password.encode("utf-8"), user_record["password_hash"].encode("utf-8")
        ):
            raise ValueError("Mot de passe incorrect")

        # Construire l'utilisateur Phoenix
        phoenix_user = self._build_phoenix_user(user_record, app)

        # Vérifier l'accès à l'application
        if not phoenix_user.can_access_app(app):
            raise ValueError(f"L'utilisateur n'a pas accès à l'application {app.value}")

        # Mettre à jour la dernière activité
        phoenix_user.update_last_activity(app)
        self._update_last_activity(phoenix_user.id, app)

        # Génération des tokens JWT
        access_token = self.jwt_manager.create_access_token(str(phoenix_user.id))
        refresh_token = self.jwt_manager.create_refresh_token(str(phoenix_user.id))

        return phoenix_user, access_token, refresh_token

    def get_user_by_id(
        self, user_id: str, app: PhoenixApp = PhoenixApp.LETTERS
    ) -> Optional[PhoenixUser]:
        """
        Récupère un utilisateur par son ID

        Args:
            user_id: ID de l'utilisateur
            app: Application demandant les informations

        Returns:
            Optional[PhoenixUser]: Utilisateur ou None
        """
        response = (
            self.client.from_("users")
            .select(
                """
                *, 
                user_subscriptions(*),
                app_usage_stats(*)
            """
            )
            .eq("id", user_id)
            .execute()
        )

        if response.data:
            return self._build_phoenix_user(response.data[0], app)

        return None

    def _build_phoenix_user(
        self, user_record: dict, current_app: PhoenixApp
    ) -> PhoenixUser:
        """
        Construit un objet PhoenixUser à partir des données Supabase

        Args:
            user_record: Données utilisateur de Supabase
            current_app: Application courante

        Returns:
            PhoenixUser: Utilisateur Phoenix
        """
        # Gestion de l'abonnement
        subscription_data = user_record.get("user_subscriptions", [])
        if (
            subscription_data
            and isinstance(subscription_data, list)
            and subscription_data
        ):
            sub_data = subscription_data[0]
            subscription = PhoenixSubscription(
                current_tier=UserTier(sub_data.get("current_tier", "free")),
                subscription_start=(
                    datetime.fromisoformat(sub_data["created_at"])
                    if sub_data.get("created_at")
                    else None
                ),
                enabled_apps={
                    PhoenixApp(app)
                    for app in sub_data.get("enabled_apps", ["letters", "cv"])
                },
            )
        else:
            subscription = PhoenixSubscription()

        # Gestion des statistiques d'usage
        stats_data = user_record.get("app_usage_stats", [])
        app_stats = {}

        if stats_data and isinstance(stats_data, list):
            for stat_record in stats_data:
                app_enum = PhoenixApp(stat_record["app"])
                app_stats[app_enum] = AppUsageStats(
                    app=app_enum,
                    letters_generated=stat_record.get("letters_generated", 0),
                    cvs_created=stat_record.get("cvs_created", 0),
                    coaching_sessions=stat_record.get("coaching_sessions", 0),
                    last_activity=(
                        datetime.fromisoformat(stat_record["last_activity"])
                        if stat_record.get("last_activity")
                        else None
                    ),
                )

        # Si pas de stats pour l'app courante, en créer
        if current_app not in app_stats:
            app_stats[current_app] = AppUsageStats(app=current_app)

        # Construire l'utilisateur Phoenix
        return PhoenixUser(
            id=uuid.UUID(user_record["id"]),
            email=user_record["email"],
            username=user_record.get("username"),
            first_name=user_record.get("first_name"),
            last_name=user_record.get("last_name"),
            status=user_record.get("status", "active"),
            email_verified=user_record.get("email_verified", False),
            newsletter_opt_in=user_record.get("newsletter_opt_in", False),
            created_at=(
                datetime.fromisoformat(user_record["created_at"])
                if user_record.get("created_at")
                else datetime.utcnow()
            ),
            last_login=(
                datetime.fromisoformat(user_record["last_login"])
                if user_record.get("last_login")
                else None
            ),
            subscription=subscription,
            app_stats=app_stats,
        )

    def _update_last_activity(self, user_id: uuid.UUID, app: PhoenixApp):
        """Met à jour la dernière activité dans la base de données"""
        try:
            # Mettre à jour les stats de l'app
            self.client.from_("app_usage_stats").update(
                {"last_activity": datetime.utcnow().isoformat()}
            ).eq("user_id", str(user_id)).eq("app", app.value).execute()

            # Mettre à jour le last_login de l'utilisateur
            self.client.from_("users").update(
                {"last_login": datetime.utcnow().isoformat()}
            ).eq("id", str(user_id)).execute()

        except Exception as e:
            print(f"Erreur mise à jour activité: {e}")  # Log simple, pas critique

    def enable_app_for_user(self, user_id: str, app: PhoenixApp) -> bool:
        """
        Active une nouvelle application pour un utilisateur

        Args:
            user_id: ID de l'utilisateur
            app: Application à activer

        Returns:
            bool: Succès de l'opération
        """
        try:
            # Récupérer l'abonnement actuel
            response = (
                self.client.from_("user_subscriptions")
                .select("enabled_apps")
                .eq("user_id", user_id)
                .execute()
            )

            if response.data:
                current_apps = response.data[0].get("enabled_apps", [])
                if app.value not in current_apps:
                    current_apps.append(app.value)

                    # Mettre à jour l'abonnement
                    self.client.from_("user_subscriptions").update(
                        {"enabled_apps": current_apps}
                    ).eq("user_id", user_id).execute()

                    # Créer les stats pour la nouvelle app
                    stats_data = {
                        "user_id": user_id,
                        "app": app.value,
                        "letters_generated": 0,
                        "cvs_created": 0,
                        "coaching_sessions": 0,
                        "last_activity": datetime.utcnow().isoformat(),
                    }

                    self.client.from_("app_usage_stats").insert(stats_data).execute()

                return True

            return False

        except Exception as e:
            print(f"Erreur activation app: {e}")
            return False
