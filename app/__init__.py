"""Factory de l'application Flask.

La fonction `create_app()` construit et configure l'application. Cette approche
(« application factory ») évite une variable globale `app` et facilite les tests.
"""
import os

from flask import Flask, render_template

from app.config import config
from app.extensions import db, mail, migrate


def create_app(config_name=None, test_config=None):
    """Crée et configure l'application.

    :param config_name: "development" | "testing" | "production".
                        Si None, on lit la variable FLASK_CONFIG (défaut: development).
    :param test_config: dictionnaire de réglages supplémentaires (utile en test).
    """
    app = Flask(__name__)

    # 1. Choix du profil de configuration.
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")
    app.config.from_object(config[config_name])

    # 2. Réglages additionnels éventuels (passés directement par les tests).
    if test_config is not None:
        app.config.update(test_config)

    # 3. Initialisation des extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # 4. Importer les modèles pour que Flask-Migrate les connaisse.
    from app import models  # noqa: F401

    # 5. Enregistrement des blueprints (modules de l'application).
    #    Le module "tasks" fournit la page d'accueil.
    #    Les modules "auth" et "users" seront ajoutés aux étapes suivantes.
    from app.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp)

    # 6. Pages d'erreur personnalisées.
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """Affiche des pages propres pour les erreurs courantes."""

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404
