"""Routes principales : accueil et tableau de bord."""
from flask import render_template
from flask_login import current_user, login_required

from app.main import bp
from app.models import Classe, Maitre, Progression, Talibe


@bp.route("/")
def home():
    """Accueil : tableau de bord si connecté, page de présentation sinon."""
    if current_user.is_authenticated:
        return dashboard()
    return render_template("home.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    """Vue d'ensemble : compteurs des quatre entités."""
    stats = {
        "maitres": Maitre.query.count(),
        "classes": Classe.query.count(),
        "talibes": Talibe.query.count(),
        "progressions": Progression.query.count(),
    }
    return render_template("dashboard.html", stats=stats)
