"""Formulaire de création / modification d'une tâche."""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class TaskForm(FlaskForm):
    """Champs communs à l'ajout et à la modification d'une tâche."""

    title = StringField(
        "Titre",
        validators=[DataRequired(), Length(max=255)],
    )
    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=2000)],
    )
    priority = SelectField(
        "Priorité",
        choices=[("low", "Basse"), ("medium", "Moyenne"), ("high", "Haute")],
        default="medium",
    )
    submit = SubmitField("Enregistrer")
