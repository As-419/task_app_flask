from flask import Flask, render_template

from app.config import Config
from app.extensions import mail, db, migrate


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .models import User, Category, Task


    # import du module task
    from app.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp)

    # import du module auth
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app