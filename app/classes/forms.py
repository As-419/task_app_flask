"""Formulaire de création / modification d'une classe."""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app.models import Niveau


class ClasseForm(FlaskForm):
    code = StringField("Code", validators=[DataRequired(), Length(max=20)])
    libelle = StringField("Libellé", validators=[DataRequired(), Length(max=150)])
    niveau = SelectField(
        "Niveau",
        choices=[(n.name, n.libelle) for n in Niveau],
        validators=[DataRequired()],
    )
    # Les choix sont remplis dans la route depuis les maîtres existants.
    maitre_matricule = SelectField(
        "Maître encadrant",
        validators=[DataRequired(message="Une classe doit obligatoirement avoir un maître.")],
        validate_choice=False,
    )
    submit = SubmitField("Enregistrer")
