"""Instances des extensions Flask.

Les objets sont créés ici SANS application : la liaison se fait dans la
factory `create_app()` via `init_app(app)`. On dispose ainsi d'une seule
instance partagée dans tout le projet.
"""
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()        # ORM : accès à la base de données
migrate = Migrate()      # migrations de schéma (Alembic)
csrf = CSRFProtect()     # protection CSRF des formulaires
