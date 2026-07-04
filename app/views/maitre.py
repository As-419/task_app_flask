"""Blueprint Maitre : cycle complet Lister / Rechercher / Ajouter /
Modifier / Supprimer / Exporter.

Règle du sujet : les exceptions métier sont levées ET capturées ici,
puis affichées via flash().
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.exceptions import (
    DaaraException,
    MaitreDejaExistantException,
    MaitreIntrouvableException,
    SuppressionImpossibleException,
)
from app.extension import db
from app.forms.maitre import MaitreForm
from app.models import Maitre
from app.utils.csv_exporter import exporter_csv

bp_maitres = Blueprint("maitres", __name__, url_prefix="/maitres")


def _rechercher_maitres(q):
    """Requête commune à la liste et à l'export : filtre par nom ou prénom."""
    query = Maitre.query
    if q:
        query = query.filter(Maitre.nom.ilike(f"%{q}%") | Maitre.prenom.ilike(f"%{q}%"))
    return query.order_by(Maitre.nom).all()


@bp_maitres.route("/")
def lister():
    q = request.args.get("q", "").strip()
    maitres = _rechercher_maitres(q)
    return render_template("maitres/liste.html", maitres=maitres, q=q)


@bp_maitres.route("/nouveau", methods=["GET", "POST"])
def creer():
    form = MaitreForm()
    if form.validate_on_submit():
        try:
            # Clé saisie par l'utilisateur : refuser un doublon.
            if db.session.get(Maitre, form.matricule.data):
                raise MaitreDejaExistantException(form.matricule.data)
            maitre = Maitre(
                matricule=form.matricule.data,
                prenom=form.prenom.data,
                nom=form.nom.data,
                telephone=form.telephone.data,
            )
            db.session.add(maitre)
            db.session.commit()
            flash("Maître ajouté.", "success")
            return redirect(url_for("maitres.lister"))
        except DaaraException as e:
            flash(str(e), "error")
    return render_template("maitres/formulaire.html", form=form, maitre=None)


@bp_maitres.route("/<matricule>/modifier", methods=["GET", "POST"])
def modifier(matricule):
    try:
        maitre = db.session.get(Maitre, matricule)
        if not maitre:
            raise MaitreIntrouvableException(matricule)
    except DaaraException as e:
        flash(str(e), "error")
        return redirect(url_for("maitres.lister"))

    form = MaitreForm(obj=maitre)
    if form.validate_on_submit():
        # La clé (matricule) est en lecture seule : on ne la modifie jamais.
        maitre.prenom = form.prenom.data
        maitre.nom = form.nom.data
        maitre.telephone = form.telephone.data
        db.session.commit()
        flash("Maître modifié.", "success")
        return redirect(url_for("maitres.lister"))
    return render_template("maitres/formulaire.html", form=form, maitre=maitre)


@bp_maitres.route("/<matricule>/supprimer", methods=["POST"])
def supprimer(matricule):
    try:
        maitre = db.session.get(Maitre, matricule)
        if not maitre:
            raise MaitreIntrouvableException(matricule)
        # Règle métier : suppression INTERDITE si le maître encadre des classes.
        if maitre.classes:
            raise SuppressionImpossibleException(
                f"Impossible de supprimer le maître {matricule} : "
                f"il encadre encore {len(maitre.classes)} classe(s)."
            )
        db.session.delete(maitre)
        db.session.commit()
        flash("Maître supprimé.", "success")
    except DaaraException as e:
        flash(str(e), "error")
    return redirect(url_for("maitres.lister"))


@bp_maitres.route("/exporter")
def exporter():
    """Exporte la liste AFFICHÉE (filtrée ou complète) au format CSV."""
    q = request.args.get("q", "").strip()
    maitres = _rechercher_maitres(q)
    lignes = [[m.matricule, m.prenom, m.nom, m.telephone or ""] for m in maitres]
    return exporter_csv(
        "maitres.csv",
        ["matricule", "prenom", "nom", "telephone"],
        lignes,
    )
