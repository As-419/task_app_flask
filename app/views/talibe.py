"""Blueprint Talibe : cycle complet Lister / Rechercher / Ajouter /
Modifier / Supprimer / Exporter.

La liste peut être filtrée par texte (nom/prénom) ET par classe.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.exceptions import (
    DaaraException,
    TalibeDejaExistantException,
    TalibeIntrouvableException,
)
from app.extension import db
from app.forms.talibe import TalibeForm
from app.models import Classe, Talibe
from app.utils.csv_exporter import exporter_csv

bp_talibes = Blueprint("talibes", __name__, url_prefix="/talibes")


def _rechercher_talibes(q, classe_code):
    """Requête commune à la liste et à l'export : texte + filtre par classe."""
    query = Talibe.query
    if classe_code:
        query = query.filter_by(classe_code=classe_code)
    if q:
        query = query.filter(Talibe.nom.ilike(f"%{q}%") | Talibe.prenom.ilike(f"%{q}%"))
    return query.order_by(Talibe.nom).all()


def _charger_choix_classes(form):
    """Alimente la liste déroulante des classes depuis la base (jamais de saisie libre)."""
    form.classe_code.choices = [
        (c.code, c.libelle) for c in Classe.query.order_by(Classe.libelle).all()
    ]


@bp_talibes.route("/")
def lister():
    q = request.args.get("q", "").strip()
    classe_code = request.args.get("classe", "").strip()
    talibes = _rechercher_talibes(q, classe_code)
    classes = Classe.query.order_by(Classe.libelle).all()
    return render_template(
        "talibes/liste.html",
        talibes=talibes,
        classes=classes,
        q=q,
        classe_code=classe_code,
    )


@bp_talibes.route("/nouveau", methods=["GET", "POST"])
def creer():
    form = TalibeForm()
    _charger_choix_classes(form)
    if form.validate_on_submit():
        try:
            if db.session.get(Talibe, form.matricule.data):
                raise TalibeDejaExistantException(form.matricule.data)
            talibe = Talibe(
                matricule=form.matricule.data,
                prenom=form.prenom.data,
                nom=form.nom.data,
                date_naissance=form.date_naissance.data,
                nom_tuteur=form.nom_tuteur.data,
                telephone_tuteur=form.telephone_tuteur.data,
                classe_code=form.classe_code.data,
            )
            db.session.add(talibe)
            db.session.commit()
            flash("Talibé ajouté.", "success")
            return redirect(url_for("talibes.lister"))
        except DaaraException as e:
            flash(str(e), "error")
    return render_template("talibes/formulaire.html", form=form, talibe=None)


@bp_talibes.route("/<matricule>/modifier", methods=["GET", "POST"])
def modifier(matricule):
    try:
        talibe = db.session.get(Talibe, matricule)
        if not talibe:
            raise TalibeIntrouvableException(matricule)
    except DaaraException as e:
        flash(str(e), "error")
        return redirect(url_for("talibes.lister"))

    form = TalibeForm(obj=talibe)
    _charger_choix_classes(form)
    if form.validate_on_submit():
        # La clé (matricule) est en lecture seule : on ne la modifie jamais.
        talibe.prenom = form.prenom.data
        talibe.nom = form.nom.data
        talibe.date_naissance = form.date_naissance.data
        talibe.nom_tuteur = form.nom_tuteur.data
        talibe.telephone_tuteur = form.telephone_tuteur.data
        talibe.classe_code = form.classe_code.data
        db.session.commit()
        flash("Talibé modifié.", "success")
        return redirect(url_for("talibes.lister"))
    return render_template("talibes/formulaire.html", form=form, talibe=talibe)


@bp_talibes.route("/<matricule>/supprimer", methods=["POST"])
def supprimer(matricule):
    try:
        talibe = db.session.get(Talibe, matricule)
        if not talibe:
            raise TalibeIntrouvableException(matricule)
        # La cascade du modèle supprime aussi toutes ses progressions.
        db.session.delete(talibe)
        db.session.commit()
        flash("Talibé supprimé (ainsi que ses progressions).", "success")
    except DaaraException as e:
        flash(str(e), "error")
    return redirect(url_for("talibes.lister"))


@bp_talibes.route("/exporter")
def exporter():
    """Exporte la liste AFFICHÉE (filtrée ou complète) au format CSV."""
    q = request.args.get("q", "").strip()
    classe_code = request.args.get("classe", "").strip()
    talibes = _rechercher_talibes(q, classe_code)
    lignes = [
        [
            t.matricule,
            t.prenom,
            t.nom,
            t.date_naissance.isoformat() if t.date_naissance else "",
            t.classe_code,
        ]
        for t in talibes
    ]
    return exporter_csv(
        "talibes.csv",
        ["matricule", "prenom", "nom", "dateNaissance", "classe"],
        lignes,
    )
