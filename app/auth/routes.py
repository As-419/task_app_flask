"""Routes du module d'authentification."""
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app.extensions import db
from app.models import User


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Création d'un nouveau compte."""
    # Un utilisateur déjà connecté n'a pas besoin de s'inscrire.
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        # Vérifie qu'aucun compte n'utilise déjà cet email ou ce nom d'utilisateur.
        email_pris = User.query.filter_by(email=form.email.data).first()
        nom_pris = User.query.filter_by(username=form.username.data).first()
        if email_pris or nom_pris:
            flash("Un compte existe déjà avec cet email ou ce nom d'utilisateur.", "error")
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)  # le mot de passe est haché
            db.session.add(user)
            db.session.commit()
            flash("Compte créé avec succès. Vous pouvez vous connecter.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Connexion d'un utilisateur existant."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Message volontairement générique (on ne révèle pas si l'email existe).
        if user is None or not user.check_password(form.password.data):
            flash("Email ou mot de passe incorrect.", "error")
        else:
            login_user(user)
            flash("Connexion réussie.", "success")
            return redirect(_safe_next_page())

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    """Déconnexion de l'utilisateur courant."""
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("main.home"))


def _safe_next_page():
    """Renvoie l'URL ?next= si elle est interne, sinon la page d'accueil.

    Empêche une « redirection ouverte » vers un site externe malveillant.
    """
    next_page = request.args.get("next")
    if next_page and next_page.startswith("/") and not next_page.startswith("//"):
        return next_page
    return url_for("main.home")
