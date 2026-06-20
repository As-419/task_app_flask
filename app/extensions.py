"""Instances des extensions Flask.

On crée ici les objets d'extension SANS les lier à une application :
la liaison se fait dans la factory `create_app()` via `init_app(app)`.
Cela permet d'avoir une seule instance partagée dans tout le projet.
"""
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()       # ORM : accès à la base de données
migrate = Migrate()     # migrations de schéma (Alembic)
mail = Mail()           # envoi d'e-mails (préparé pour les étapes suivantes)
