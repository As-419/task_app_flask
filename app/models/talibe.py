"""Entité Talibe : un élève de la daara, rattaché à une classe."""
from app.extension import db
from app.models.base import BaseModel


class Talibe(BaseModel):
    __tablename__ = "talibes"

    # Clé primaire SAISIE par l'utilisateur.
    matricule = db.Column(db.String(50), primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date)
    nom_tuteur = db.Column(db.String(200))
    telephone_tuteur = db.Column(db.String(20))

    # Un talibé est OBLIGATOIREMENT rattaché à une classe.
    classe_code = db.Column(
        db.String(50),
        db.ForeignKey("classes.code"),
        nullable=False,
    )
    classe = db.relationship("Classe", back_populates="talibes")

    # Historique des progressions. cascade : supprimer le talibé
    # supprime aussi toutes ses progressions (règle métier du sujet).
    progressions = db.relationship(
        "Progression",
        back_populates="talibe",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Talibe {self.matricule} {self.prenom} {self.nom}>"
