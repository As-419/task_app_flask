"""Blueprint principal : page d'accueil (tableau de bord)."""
from flask import Blueprint, render_template

from app.models import Classe, Maitre, Progression, Talibe

bp_main = Blueprint("main", __name__)


@bp_main.route("/")
def accueil():
    """Petit tableau de bord : effectifs et accès rapide aux 4 entités."""
    compteurs = {
        "maitres": Maitre.query.count(),
        "classes": Classe.query.count(),
        "talibes": Talibe.query.count(),
        "progressions": Progression.query.count(),
    }
    return render_template("index.html", compteurs=compteurs)
