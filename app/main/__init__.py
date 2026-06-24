"""Blueprint principal : page d'accueil publique et tableau de bord."""
from flask import Blueprint

bp = Blueprint("main", __name__)

from app.main import routes  # noqa: E402,F401
