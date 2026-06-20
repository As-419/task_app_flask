"""Module des tâches (todo) : page d'accueil + CRUD des tâches."""
from flask import Blueprint

bp = Blueprint("tasks", __name__)

from app.tasks import routes  # noqa: E402, F401  (importé pour enregistrer les routes)
