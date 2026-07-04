"""Entité Maitre : le serigne qui encadre des classes (halqas)."""
from app.extension import db
from app.models.base import BaseModel


class Maitre(BaseModel):
    __tablename__ = "maitres"

    # Clé primaire SAISIE par l'utilisateur (pas d'auto-incrément).
    matricule = db.Column(db.String(50), primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20))

    # Un maître encadre plusieurs classes (côté « 1 » de la relation).
    classes = db.relationship("Classe", back_populates="maitre")

    def __repr__(self):
        return f"<Maitre {self.matricule} {self.prenom} {self.nom}>"
