"""Blueprint de gestion des maîtres (serignes)."""
from flask import Blueprint

bp = Blueprint("maitres", __name__, url_prefix="/maitres")

from app.maitres import routes  # noqa: E402,F401
