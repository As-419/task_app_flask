"""Formulaire WTForms de l'entité Progression.

Remarque pédagogique : `nombre_versets` n'a volontairement PAS de
NumberRange(min=0) ici. La règle « nombre_versets >= 0 » est une règle
MÉTIER : elle est vérifiée dans la vue, qui lève
ProgressionInvalideException (voir section 6 du sujet).
"""
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, Optional


class ProgressionForm(FlaskForm):
    sourate = StringField(
        "Sourate",
        validators=[DataRequired("La sourate est obligatoire."), Length(max=100)],
    )
    # InputRequired accepte 0 (DataRequired refuserait la valeur 0).
    nombre_versets = IntegerField(
        "Nombre de versets",
        validators=[InputRequired("Le nombre de versets est obligatoire.")],
    )
    date_evaluation = DateField("Date d'évaluation", validators=[Optional()])
    observations = TextAreaField("Observations", validators=[Optional()])
    # Liste déroulante alimentée depuis la base DANS LA VUE.
    talibe_matricule = SelectField(
        "Talibé",
        validators=[DataRequired("Le talibé est obligatoire.")],
    )
    submit = SubmitField("Enregistrer")
