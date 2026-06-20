"""Factory de l'application Flask.

La fonction `create_app()` construit et configure l'application. Cette approche
(« application factory ») évite une variable globale `app` et facilite les tests.
"""
import os

from flask import Flask, render_template

from app.config import config
from app.extensions import csrf, db, login_manager, mail, migrate


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
    csrf.init_app(app)
    login_manager.init_app(app)

    # Vers quelle page rediriger un visiteur non connecté qui demande une page protégée.
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "info"

    # 4. Importer les modèles pour que Flask-Migrate les connaisse.
    from app import models  # noqa: F401

    # Flask-Login a besoin de savoir comment retrouver un utilisateur à partir de son id.
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    # 5. Enregistrement des blueprints (modules de l'application).
    from app.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # Le module "users" sera ajouté à l'étape 4.

    # 6. Pages d'erreur personnalisées.
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """Affiche des pages propres pour les erreurs courantes."""

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404
