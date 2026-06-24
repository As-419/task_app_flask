"""Blueprint de gestion des progressions (évaluations)."""
from flask import Blueprint

bp = Blueprint("progressions", __name__, url_prefix="/progressions")

from app.progressions import routes  # noqa: E402,F401
