"""Factory de l'application Flask (architecture MVC).

`create_app()` construit et configure l'application : configuration,
extensions, modèles puis blueprints (les contrôleurs MVC).
"""
import os

from flask import Flask

from app.extension import csrf, db, migrate
from config import config


def create_app(config_name=None):
    """Crée et configure l'application.

    :param config_name: "development" | "production".
                        Si None, on lit FLASK_CONFIG (défaut : development).
    """
    app = Flask(__name__)

    # 1. Choix du profil de configuration.
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "development")
    app.config.from_object(config[config_name])

    # 2. Initialisation des extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # 3. Importer les modèles pour que Flask-Migrate connaisse les tables.
    from app import models  # noqa: F401

    # 4. Enregistrement des blueprints (couche Vue/Contrôleur du MVC).
    from app.views.classe import bp_classes
    from app.views.main import bp_main
    from app.views.maitre import bp_maitres
    from app.views.progression import bp_progressions
    from app.views.talibe import bp_talibes

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_maitres)
    app.register_blueprint(bp_classes)
    app.register_blueprint(bp_talibes)
    app.register_blueprint(bp_progressions)

    return app
