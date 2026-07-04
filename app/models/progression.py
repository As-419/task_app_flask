"""Entité Progression : une évaluation de mémorisation pour un talibé."""
from app.extension import db
from app.models.base import BaseModel


class Progression(BaseModel):
    __tablename__ = "progressions"

    # Seule entité à clé AUTO-GÉNÉRÉE (entier auto-incrémenté).
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sourate = db.Column(db.String(100), nullable=False)
    nombre_versets = db.Column(db.Integer, nullable=False)
    date_evaluation = db.Column(db.Date)
    observations = db.Column(db.Text)

    # Une progression est OBLIGATOIREMENT rattachée à un talibé.
    talibe_matricule = db.Column(
        db.String(50),
        db.ForeignKey("talibes.matricule"),
        nullable=False,
    )
    talibe = db.relationship("Talibe", back_populates="progressions")

    def __repr__(self):
        return f"<Progression {self.id} {self.sourate} ({self.talibe_matricule})>"
