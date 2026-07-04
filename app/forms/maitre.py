"""Formulaire WTForms de l'entité Maitre."""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class MaitreForm(FlaskForm):
    matricule = StringField(
        "Matricule",
        validators=[DataRequired("Le matricule est obligatoire."), Length(max=50)],
    )
    prenom = StringField(
        "Prénom",
        validators=[DataRequired("Le prénom est obligatoire."), Length(max=100)],
    )
    nom = StringField(
        "Nom",
        validators=[DataRequired("Le nom est obligatoire."), Length(max=100)],
    )
    telephone = StringField(
        "Téléphone",
        validators=[Optional(), Length(max=20)],
    )
    submit = SubmitField("Enregistrer")
