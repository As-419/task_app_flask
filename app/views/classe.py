"""Blueprint Classe : cycle complet Lister / Rechercher / Ajouter /
Modifier / Supprimer / Exporter.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.exceptions import (
    ClasseDejaExistanteException,
    ClasseIntrouvableException,
    DaaraException,
    SuppressionImpossibleException,
)
from app.extension import db
from app.forms.classe import ClasseForm
from app.models import Classe, Maitre
from app.utils.csv_exporter import exporter_csv

bp_classes = Blueprint("classes", __name__, url_prefix="/classes")


def _rechercher_classes(q):
    """Requête commune à la liste et à l'export : filtre par libellé ou niveau."""
    query = Classe.query
    if q:
        query = query.filter(Classe.libelle.ilike(f"%{q}%") | Classe.niveau.ilike(f"%{q}%"))
    return query.order_by(Classe.libelle).all()


def _charger_choix_maitres(form):
    """Alimente la liste déroulante des maîtres depuis la base (jamais de saisie libre)."""
    form.maitre_matricule.choices = [
        (m.matricule, f"{m.prenom} {m.nom}")
        for m in Maitre.query.order_by(Maitre.nom).all()
    ]


@bp_classes.route("/")
def lister():
    q = request.args.get("q", "").strip()
    classes = _rechercher_classes(q)
    return render_template("classes/liste.html", classes=classes, q=q)


@bp_classes.route("/nouveau", methods=["GET", "POST"])
def creer():
    form = ClasseForm()
    _charger_choix_maitres(form)
    if form.validate_on_submit():
        try:
            if db.session.get(Classe, form.code.data):
                raise ClasseDejaExistanteException(form.code.data)
            classe = Classe(
                code=form.code.data,
                libelle=form.libelle.data,
                niveau=form.niveau.data,
                maitre_matricule=form.maitre_matricule.data,
            )
            db.session.add(classe)
            db.session.commit()
            flash("Classe ajoutée.", "success")
            return redirect(url_for("classes.lister"))
        except DaaraException as e:
            flash(str(e), "error")
    return render_template("classes/formulaire.html", form=form, classe=None)


@bp_classes.route("/<code>/modifier", methods=["GET", "POST"])
def modifier(code):
    try:
        classe = db.session.get(Classe, code)
        if not classe:
            raise ClasseIntrouvableException(code)
    except DaaraException as e:
        flash(str(e), "error")
        return redirect(url_for("classes.lister"))

    form = ClasseForm(obj=classe)
    _charger_choix_maitres(form)
    if form.validate_on_submit():
        # La clé (code) est en lecture seule : on ne la modifie jamais.
        classe.libelle = form.libelle.data
        classe.niveau = form.niveau.data
        classe.maitre_matricule = form.maitre_matricule.data
        db.session.commit()
        flash("Classe modifiée.", "success")
        return redirect(url_for("classes.lister"))
    return render_template("classes/formulaire.html", form=form, classe=classe)


@bp_classes.route("/<code>/supprimer", methods=["POST"])
def supprimer(code):
    try:
        classe = db.session.get(Classe, code)
        if not classe:
            raise ClasseIntrouvableException(code)
        # Règle métier : suppression INTERDITE si la classe contient des talibés.
        if classe.talibes:
            raise SuppressionImpossibleException(
                f"Impossible de supprimer la classe {code} : "
                f"elle contient encore {len(classe.talibes)} talibé(s)."
            )
        db.session.delete(classe)
        db.session.commit()
        flash("Classe supprimée.", "success")
    except DaaraException as e:
        flash(str(e), "error")
    return redirect(url_for("classes.lister"))


@bp_classes.route("/exporter")
def exporter():
    """Exporte la liste AFFICHÉE (filtrée ou complète) au format CSV."""
    q = request.args.get("q", "").strip()
    classes = _rechercher_classes(q)
    lignes = [
        [c.code, c.libelle, c.niveau or "", c.maitre_matricule]
        for c in classes
    ]
    return exporter_csv(
        "classes.csv",
        ["code", "libelle", "niveau", "maitre"],
        lignes,
    )
