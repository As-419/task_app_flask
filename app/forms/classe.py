"""Formulaire WTForms de l'entité Classe."""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class ClasseForm(FlaskForm):
    code = StringField(
        "Code",
        validators=[DataRequired("Le code est obligatoire."), Length(max=50)],
    )
    libelle = StringField(
        "Libellé",
        validators=[DataRequired("Le libellé est obligatoire."), Length(max=100)],
    )
    niveau = StringField(
        "Niveau",
        validators=[Optional(), Length(max=50)],
    )
    # Liste déroulante alimentée depuis la base DANS LA VUE — jamais de saisie libre.
    maitre_matricule = SelectField(
        "Maître",
        validators=[DataRequired("Le maître est obligatoire.")],
    )
    submit = SubmitField("Enregistrer")
