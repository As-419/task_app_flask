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
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.users import bp as users_bp
    app.register_blueprint(users_bp)

    # Domaine métier « Daara » : un blueprint par entité (comme un contrôleur
    # par entité en MVC).
    from app.maitres import bp as maitres_bp
    app.register_blueprint(maitres_bp)

    from app.classes import bp as classes_bp
    app.register_blueprint(classes_bp)

    from app.talibes import bp as talibes_bp
    app.register_blueprint(talibes_bp)

    from app.progressions import bp as progressions_bp
    app.register_blueprint(progressions_bp)

    # 6. Garde-fou : en production, une vraie SECRET_KEY est obligatoire.
    if config_name == "production" and app.config.get("SECRET_KEY") in (None, "", "dev-secret-a-changer"):
        raise RuntimeError(
            "SECRET_KEY non définie en production : définissez la variable d'environnement."
        )

    # 7. En-têtes de sécurité HTTP sur toutes les réponses.
    register_security_headers(app)

    # 8. Pages d'erreur personnalisées.
    register_error_handlers(app)

    return app


def register_security_headers(app):
    """Ajoute des en-têtes de sécurité standards à chaque réponse."""

    @app.after_request
    def _ajouter_entetes(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


def register_error_handlers(app):
    """Affiche des pages propres pour les erreurs courantes."""

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        # Annule une éventuelle transaction laissée ouverte par l'erreur.
        db.session.rollback()
        return render_template("errors/500.html"), 500
