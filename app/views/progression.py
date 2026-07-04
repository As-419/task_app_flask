"""Blueprint Progression : cycle complet Lister (filtrable par talibé) /
Ajouter / Modifier / Supprimer / Exporter.

La règle « nombre_versets >= 0, sourate non vide, talibé renseigné » est
une règle MÉTIER : elle est vérifiée ici et lève ProgressionInvalideException.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.exceptions import (
    DaaraException,
    ProgressionIntrouvableException,
    ProgressionInvalideException,
)
from app.extension import db
from app.forms.progression import ProgressionForm
from app.models import Progression, Talibe
from app.utils.csv_exporter import exporter_csv

bp_progressions = Blueprint("progressions", __name__, url_prefix="/progressions")


def _rechercher_progressions(talibe_matricule):
    """Requête commune à la liste et à l'export : filtre par talibé."""
    query = Progression.query
    if talibe_matricule:
        query = query.filter_by(talibe_matricule=talibe_matricule)
    return query.order_by(Progression.date_evaluation.desc().nullslast()).all()


def _charger_choix_talibes(form):
    """Alimente la liste déroulante des talibés depuis la base (jamais de saisie libre)."""
    form.talibe_matricule.choices = [
        (t.matricule, f"{t.prenom} {t.nom}")
        for t in Talibe.query.order_by(Talibe.nom).all()
    ]


def _verifier_progression(form):
    """Règles métier du sujet : lève ProgressionInvalideException si incohérent."""
    if not form.sourate.data or not form.sourate.data.strip():
        raise ProgressionInvalideException("La sourate ne peut pas être vide.")
    if form.nombre_versets.data is None or form.nombre_versets.data < 0:
        raise ProgressionInvalideException(
            "Le nombre de versets doit être supérieur ou égal à 0."
        )
    if not form.talibe_matricule.data:
        raise ProgressionInvalideException("Le talibé doit être renseigné.")


@bp_progressions.route("/")
def lister():
    talibe_matricule = request.args.get("talibe", "").strip()
    progressions = _rechercher_progressions(talibe_matricule)
    talibes = Talibe.query.order_by(Talibe.nom).all()
    return render_template(
        "progressions/liste.html",
        progressions=progressions,
        talibes=talibes,
        talibe_matricule=talibe_matricule,
    )


@bp_progressions.route("/nouveau", methods=["GET", "POST"])
def creer():
    form = ProgressionForm()
    _charger_choix_talibes(form)
    if form.validate_on_submit():
        try:
            _verifier_progression(form)
            progression = Progression(
                sourate=form.sourate.data.strip(),
                nombre_versets=form.nombre_versets.data,
                date_evaluation=form.date_evaluation.data,
                observations=form.observations.data,
                talibe_matricule=form.talibe_matricule.data,
            )
            db.session.add(progression)
            db.session.commit()
            flash("Progression ajoutée.", "success")
            return redirect(url_for("progressions.lister"))
        except DaaraException as e:
            flash(str(e), "error")
    return render_template("progressions/formulaire.html", form=form, progression=None)


@bp_progressions.route("/<int:progression_id>/modifier", methods=["GET", "POST"])
def modifier(progression_id):
    try:
        progression = db.session.get(Progression, progression_id)
        if not progression:
            raise ProgressionIntrouvableException(progression_id)
    except DaaraException as e:
        flash(str(e), "error")
        return redirect(url_for("progressions.lister"))

    form = ProgressionForm(obj=progression)
    _charger_choix_talibes(form)
    if form.validate_on_submit():
        try:
            _verifier_progression(form)
            progression.sourate = form.sourate.data.strip()
            progression.nombre_versets = form.nombre_versets.data
            progression.date_evaluation = form.date_evaluation.data
            progression.observations = form.observations.data
            progression.talibe_matricule = form.talibe_matricule.data
            db.session.commit()
            flash("Progression modifiée.", "success")
            return redirect(url_for("progressions.lister"))
        except DaaraException as e:
            flash(str(e), "error")
    return render_template(
        "progressions/formulaire.html", form=form, progression=progression
    )


@bp_progressions.route("/<int:progression_id>/supprimer", methods=["POST"])
def supprimer(progression_id):
    try:
        progression = db.session.get(Progression, progression_id)
        if not progression:
            raise ProgressionIntrouvableException(progression_id)
        db.session.delete(progression)
        db.session.commit()
        flash("Progression supprimée.", "success")
    except DaaraException as e:
        flash(str(e), "error")
    return redirect(url_for("progressions.lister"))


@bp_progressions.route("/exporter")
def exporter():
    """Exporte la liste AFFICHÉE (filtrée ou complète) au format CSV."""
    talibe_matricule = request.args.get("talibe", "").strip()
    progressions = _rechercher_progressions(talibe_matricule)
    lignes = [
        [
            p.id,
            p.sourate,
            p.nombre_versets,
            p.date_evaluation.isoformat() if p.date_evaluation else "",
            p.observations or "",
            p.talibe_matricule,
        ]
        for p in progressions
    ]
    return exporter_csv(
        "progressions.csv",
        ["id", "sourate", "nombreVersets", "dateEvaluation", "observations", "talibe"],
        lignes,
    )
