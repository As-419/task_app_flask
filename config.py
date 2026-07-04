"""Configuration de l'application Daara.

Une classe par environnement. Conformément au sujet, seule l'URL de la base
PostgreSQL change selon l'environnement (variable d'environnement ou valeur
par défaut).
"""
import os

from dotenv import load_dotenv

# Charge les variables définies dans le fichier .env (s'il existe).
load_dotenv()


class BaseConfig:
    """Réglages communs à tous les environnements."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-a-changer")
    # Désactive un suivi coûteux et inutile des objets par SQLAlchemy.
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Environnement de développement (machine de l'étudiant)."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DEV_DATABASE_URL",
        "postgresql+psycopg2://postgres:motdepasse@localhost:5432/daara",
    )


class ProductionConfig(BaseConfig):
    """Environnement de production."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")


# Table de correspondance : nom d'environnement -> classe de configuration.
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
