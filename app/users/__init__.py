"""Module de gestion des utilisateurs (profil, mot de passe, suppression)."""
from flask import Blueprint

# url_prefix="/account" => routes /account, /account/edit, /account/password, /account/delete
bp = Blueprint("users", __name__, url_prefix="/account")

from app.users import routes  # noqa: E402, F401  (importé pour enregistrer les routes)
