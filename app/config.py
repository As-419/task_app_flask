"""Configuration de l'application.

On définit une classe de base `Config` puis une classe par environnement
(développement, test, production). Le bon profil est choisi au démarrage
selon la variable d'environnement FLASK_CONFIG.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Charge les variables définies dans le fichier .env (s'il existe).
# On vise explicitement la racine du projet pour que le chargement
# fonctionne quel que soit le répertoire de travail courant.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class Config:
    """Réglages communs à tous les environnements."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-a-changer")
    # Désactive un suivi inutile et coûteux des modifications par SQLAlchemy.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Cookies de session durcis dès le développement (le cookie n'est pas
    # lisible en JS et n'est pas envoyé en contexte cross-site).
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    """Environnement de développement (sur la machine du développeur)."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://taskapp:taskapp@localhost:5432/taskapp",
    )


class TestingConfig(Config):
    """Environnement de test.

    On utilise une base SQLite EN MÉMOIRE : les tests sont rapides et
    ne nécessitent ni PostgreSQL ni Docker. La protection CSRF est
    désactivée pour simplifier l'envoi de formulaires dans les tests.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Environnement de production."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    # En production, le cookie n'est transmis qu'en HTTPS.
    SESSION_COOKIE_SECURE = True


# Table de correspondance : nom -> classe de configuration.
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
