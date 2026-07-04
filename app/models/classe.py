"""Entité Classe : une halqa encadrée par un maître et regroupant des talibés."""
from app.extension import db
from app.models.base import BaseModel


class Classe(BaseModel):
    __tablename__ = "classes"

    # Clé primaire SAISIE par l'utilisateur.
    code = db.Column(db.String(50), primary_key=True)
    libelle = db.Column(db.String(100), nullable=False)
    niveau = db.Column(db.String(50))

    # Une classe a OBLIGATOIREMENT un maître (ForeignKey + relationship).
    maitre_matricule = db.Column(
        db.String(50),
        db.ForeignKey("maitres.matricule"),
        nullable=False,
    )
    maitre = db.relationship("Maitre", back_populates="classes")

    # Une classe regroupe plusieurs talibés.
    talibes = db.relationship("Talibe", back_populates="classe")

    def __repr__(self):
        return f"<Classe {self.code} {self.libelle}>"
