"""Formulaire de création / modification d'une progression."""
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProgressionForm(FlaskForm):
    # Les choix sont remplis dans la route depuis les talibés existants.
    talibe_matricule = SelectField(
        "Talibé évalué",
        validators=[DataRequired(message="Sélectionnez un talibé.")],
        validate_choice=False,
    )
    sourate = StringField("Sourate", validators=[DataRequired(), Length(max=100)])
    nombre_versets = IntegerField(
        "Nombre de versets mémorisés",
        validators=[
            DataRequired(),
            NumberRange(min=0, message="Le nombre de versets doit être ≥ 0."),
        ],
    )
    date_evaluation = DateField("Date d'évaluation", validators=[Optional()])
    appreciation = StringField("Appréciation", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Enregistrer")
