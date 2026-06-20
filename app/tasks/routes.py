"""Routes du module des tâches."""
from flask import render_template

from app.tasks import bp


@bp.route("/")
def home():
    """Page d'accueil de l'application."""
    return render_template("home.html")
