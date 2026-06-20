"""Routes de gestion du compte de l'utilisateur connecté."""
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user

from app.extensions import db
from app.models import User
from app.users import bp
from app.users.forms import ChangePasswordForm, DeleteAccountForm, ProfileForm


@bp.route("/")
@login_required
def profile():
    """Affiche les informations du compte."""
    delete_form = DeleteAccountForm()
    return render_template("users/profile.html", delete_form=delete_form)


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def profile_edit():
    """Modifie le nom d'utilisateur et l'email."""
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # L'email / le nom doivent rester uniques (sauf vis-à-vis de soi-même).
        email_pris = User.query.filter(
            User.email == form.email.data, User.id != current_user.id
        ).first()
        nom_pris = User.query.filter(
            User.username == form.username.data, User.id != current_user.id
        ).first()
        if email_pris or nom_pris:
            flash("Cet email ou ce nom d'utilisateur est déjà utilisé.", "error")
        else:
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Profil mis à jour.", "success")
            return redirect(url_for("users.profile"))
    return render_template("users/edit.html", form=form)


@bp.route("/password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change le mot de passe après vérification de l'ancien."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Mot de passe actuel incorrect.", "error")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Mot de passe modifié avec succès.", "success")
            return redirect(url_for("users.profile"))
    return render_template("users/change_password.html", form=form)


@bp.route("/delete", methods=["POST"])
@login_required
def delete_account():
    """Supprime le compte de l'utilisateur connecté (et ses tâches)."""
    form = DeleteAccountForm()
    if form.validate_on_submit():
        # On récupère l'objet réel avant de déconnecter, puis on le supprime.
        user = db.session.get(User, current_user.id)
        logout_user()
        db.session.delete(user)  # supprime aussi ses tâches (cascade)
        db.session.commit()
        flash("Votre compte a été supprimé.", "info")
        return redirect(url_for("tasks.home"))
    return redirect(url_for("users.profile"))
