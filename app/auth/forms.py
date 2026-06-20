"""Formulaires d'authentification (Flask-WTF / WTForms).

Chaque champ déclare ses règles de validation. WTForms s'occupe de vérifier
la saisie et d'afficher les messages d'erreur. La protection CSRF est ajoutée
automatiquement par Flask-WTF (champ caché via form.hidden_tag()).
"""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    """Formulaire de création de compte."""

    username = StringField(
        "Nom d'utilisateur",
        validators=[DataRequired(), Length(min=3, max=50)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=100)],
    )
    password = PasswordField(
        "Mot de passe",
        validators=[DataRequired(), Length(min=6)],
    )
    confirm = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(),
            EqualTo("password", message="Les mots de passe ne correspondent pas."),
        ],
    )
    submit = SubmitField("Créer mon compte")


class LoginForm(FlaskForm):
    """Formulaire de connexion."""

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")
