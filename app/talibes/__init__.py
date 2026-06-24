"""Blueprint de gestion des talibés (élèves)."""
from flask import Blueprint

bp = Blueprint("talibes", __name__, url_prefix="/talibes")

from app.talibes import routes  # noqa: E402,F401
