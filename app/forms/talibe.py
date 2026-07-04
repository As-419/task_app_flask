"""Formulaire WTForms de l'entité Talibe."""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class TalibeForm(FlaskForm):
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
    date_naissance = DateField("Date de naissance", validators=[Optional()])
    nom_tuteur = StringField(
        "Nom du tuteur",
        validators=[Optional(), Length(max=200)],
    )
    telephone_tuteur = StringField(
        "Téléphone tuteur",
        validators=[Optional(), Length(max=20)],
    )
    # Liste déroulante alimentée depuis la base DANS LA VUE.
    classe_code = SelectField(
        "Classe",
        validators=[DataRequired("La classe est obligatoire.")],
    )
    submit = SubmitField("Enregistrer")
