"""Module des tâches (todo).

À l'étape 1, il fournit seulement la page d'accueil.
Le CRUD complet des tâches sera ajouté à l'ÉTAPE 3.
"""
from flask import Blueprint

bp = Blueprint("tasks", __name__)

from app.tasks import routes  # noqa: E402, F401  (importé pour enregistrer les routes)
