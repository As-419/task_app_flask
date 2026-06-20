"""Module d'authentification : inscription, connexion, déconnexion."""
from flask import Blueprint

# url_prefix="/auth" => les routes deviennent /auth/register, /auth/login, /auth/logout
bp = Blueprint("auth", __name__, url_prefix="/auth")

from app.auth import routes  # noqa: E402, F401  (importé pour enregistrer les routes)
