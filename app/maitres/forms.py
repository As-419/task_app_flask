"""Formulaire de création / modification d'un maître."""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class MaitreForm(FlaskForm):
    matricule = StringField(
        "Matricule", validators=[DataRequired(), Length(max=20)]
    )
    nom_complet = StringField(
        "Nom complet", validators=[DataRequired(), Length(max=150)]
    )
    telephone = StringField(
        "Téléphone", validators=[Optional(), Length(max=30)]
    )
    submit = SubmitField("Enregistrer")
