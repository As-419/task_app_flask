"""Modèles SQLAlchemy du domaine « Daara » (école coranique).

Le sujet est identique au projet Java : on gère des maîtres (serignes), des
classes (halqas), des talibés (élèves) et leur progression dans la mémorisation
du Coran. `User` reste présent uniquement pour la connexion (login).

Chaîne de relations :
    Maitre 1 ──< Classe 1 ──< Talibe 1 ──< Progression
"""
import enum
from datetime import date, datetime

from flask_login import UserMixin
from sqlalchemy import (
    CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Niveau(enum.Enum):
    """Niveau d'une classe (halqa)."""
    DEBUTANT = "Débutant"
    INTERMEDIAIRE = "Intermédiaire"
    AVANCE = "Avancé"

    @property
    def libelle(self) -> str:
        return self.value


# ---------------------------------------------------------------- Utilisateur

class User(UserMixin, db.Model):
    """Compte de connexion (le sujet Daara n'impose pas l'auth, mais l'app web
    expose un portail de connexion). UserMixin fournit les propriétés attendues
    par Flask-Login."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def set_password(self, raw_password: str) -> None:
        """Hache et enregistre le mot de passe (jamais stocké en clair)."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f"<User {self.username}>"


# ---------------------------------------------------------------------- Maitre

class Maitre(db.Model):
    """Maître (serigne) qui encadre des classes. Clé = matricule saisi."""
    __tablename__ = "maitres"

    matricule: Mapped[str] = mapped_column(String(20), primary_key=True)
    nom_complet: Mapped[str] = mapped_column(String(150), nullable=False)
    telephone: Mapped[str | None] = mapped_column(String(30))

    classes: Mapped[list["Classe"]] = relationship(
        "Classe", back_populates="maitre"
    )

    def __repr__(self):
        return f"<Maitre {self.matricule}>"


# ---------------------------------------------------------------------- Classe

class Classe(db.Model):
    """Classe (halqa) encadrée par un maître. Clé = code saisi."""
    __tablename__ = "classes"

    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    libelle: Mapped[str] = mapped_column(String(150), nullable=False)
    niveau: Mapped[Niveau] = mapped_column(Enum(Niveau), nullable=False)
    maitre_matricule: Mapped[str] = mapped_column(
        String(20), ForeignKey("maitres.matricule"), nullable=False
    )

    maitre: Mapped["Maitre"] = relationship("Maitre", back_populates="classes")
    talibes: Mapped[list["Talibe"]] = relationship(
        "Talibe", back_populates="classe"
    )

    def __repr__(self):
        return f"<Classe {self.code}>"


# ---------------------------------------------------------------------- Talibe

class Talibe(db.Model):
    """Talibé (élève) rattaché à une classe. Clé = matricule saisi."""
    __tablename__ = "talibes"

    matricule: Mapped[str] = mapped_column(String(20), primary_key=True)
    prenom: Mapped[str] = mapped_column(String(80), nullable=False)
    nom: Mapped[str] = mapped_column(String(80), nullable=False)
    date_naissance: Mapped[date | None] = mapped_column(Date)
    nom_tuteur: Mapped[str | None] = mapped_column(String(150))
    telephone_tuteur: Mapped[str | None] = mapped_column(String(30))
    classe_code: Mapped[str] = mapped_column(
        String(20), ForeignKey("classes.code"), nullable=False
    )

    classe: Mapped["Classe"] = relationship("Classe", back_populates="talibes")
    # Supprimer un talibé supprime ses progressions (cascade gérée par l'ORM,
    # ce qui fonctionne aussi bien sous SQLite que PostgreSQL).
    progressions: Mapped[list["Progression"]] = relationship(
        "Progression", back_populates="talibe",
        cascade="all, delete-orphan",
    )

    @property
    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}"

    def __repr__(self):
        return f"<Talibe {self.matricule}>"


# ------------------------------------------------------------------ Progression

class Progression(db.Model):
    """Évaluation de la mémorisation du Coran pour un talibé.

    Contrairement aux autres entités, la clé est AUTO-GÉNÉRÉE (entier)."""
    __tablename__ = "progressions"
    __table_args__ = (
        CheckConstraint("nombre_versets >= 0", name="check_versets_positifs"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    talibe_matricule: Mapped[str] = mapped_column(
        String(20), ForeignKey("talibes.matricule", ondelete="CASCADE"), nullable=False
    )
    sourate: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre_versets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date_evaluation: Mapped[date | None] = mapped_column(Date)
    appreciation: Mapped[str | None] = mapped_column(String(255))

    talibe: Mapped["Talibe"] = relationship("Talibe", back_populates="progressions")

    def __repr__(self):
        return f"<Progression {self.id} - {self.sourate}>"
