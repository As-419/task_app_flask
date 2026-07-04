"""Classe de base commune à toutes les entités.

`__abstract__ = True` : SQLAlchemy ne crée PAS de table pour cette classe ;
elle sert uniquement à partager les colonnes `cree_le` et `maj_le`.
"""
from datetime import datetime

from app.extension import db


class BaseModel(db.Model):
    __abstract__ = True

    # Date de création de la ligne (remplie automatiquement à l'insertion).
    cree_le = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Date de dernière modification (mise à jour automatiquement).
    maj_le = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
