"""Formulaire de création / modification d'un talibé."""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class TalibeForm(FlaskForm):
    matricule = StringField("Matricule", validators=[DataRequired(), Length(max=20)])
    prenom = StringField("Prénom", validators=[DataRequired(), Length(max=80)])
    nom = StringField("Nom", validators=[DataRequired(), Length(max=80)])
    date_naissance = DateField("Date de naissance", validators=[Optional()])
    nom_tuteur = StringField("Nom du tuteur", validators=[Optional(), Length(max=150)])
    telephone_tuteur = StringField("Téléphone du tuteur", validators=[Optional(), Length(max=30)])
    # Les choix sont remplis dans la route depuis les classes existantes.
    classe_code = SelectField(
        "Classe d'affectation",
        validators=[DataRequired(message="Un talibé doit obligatoirement être rattaché à une classe.")],
        validate_choice=False,
    )
    submit = SubmitField("Enregistrer")
