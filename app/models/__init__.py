"""Regroupe les entités pour pouvoir écrire `from app.models import Talibe`.

Importer ce paquet enregistre aussi toutes les tables auprès de SQLAlchemy
(nécessaire pour que Flask-Migrate les détecte).
"""
from app.models.base import BaseModel
from app.models.classe import Classe
from app.models.maitre import Maitre
from app.models.progression import Progression
from app.models.talibe import Talibe

__all__ = ["BaseModel", "Maitre", "Classe", "Talibe", "Progression"]
