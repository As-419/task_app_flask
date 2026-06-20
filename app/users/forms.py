"""Formulaires de gestion du compte utilisateur."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class ProfileForm(FlaskForm):
    """Modification du nom d'utilisateur et de l'email."""

    username = StringField(
        "Nom d'utilisateur",
        validators=[DataRequired(), Length(min=3, max=50)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=100)],
    )
    submit = SubmitField("Enregistrer")


class ChangePasswordForm(FlaskForm):
    """Changement de mot de passe."""

    current_password = PasswordField(
        "Mot de passe actuel",
        validators=[DataRequired()],
    )
    new_password = PasswordField(
        "Nouveau mot de passe",
        validators=[DataRequired(), Length(min=6)],
    )
    confirm = PasswordField(
        "Confirmer le nouveau mot de passe",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Les mots de passe ne correspondent pas."),
        ],
    )
    submit = SubmitField("Changer le mot de passe")


class DeleteAccountForm(FlaskForm):
    """Formulaire (vide) servant uniquement à protéger la suppression par CSRF."""

    submit = SubmitField("Supprimer définitivement mon compte")
