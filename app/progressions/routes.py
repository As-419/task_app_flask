"""Routes du module des progressions (évaluations de mémorisation).

Règles métier (identiques au projet Java) :
- talibé OBLIGATOIRE (liste déroulante) ;
- nombre de versets ≥ 0 et sourate non vide (sinon erreur) ;
- la page peut filtrer par talibé.
"""
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.csv_export import reponse_csv
from app.extensions import db
from app.models import Progression, Talibe
from app.progressions import bp
from app.progressions.forms import ProgressionForm


def _charger_talibes(form):
    form.talibe_matricule.choices = [
        (t.matricule, f"{t.nom_complet} ({t.matricule})")
        for t in Talibe.query.order_by(Talibe.nom, Talibe.prenom).all()
    ]


@bp.route("/")
@login_required
def liste():
    """Liste les progressions, avec filtre par talibé (par critère)."""
    talibe_matricule = request.args.get("talibe", "").strip()
    query = Progression.query
    if talibe_matricule:
        query = query.filter_by(talibe_matricule=talibe_matricule)
    progressions = query.order_by(Progression.date_evaluation.desc()).all()
    talibes = Talibe.query.order_by(Talibe.nom, Talibe.prenom).all()
    return render_template(
        "progressions/liste.html", progressions=progressions,
        talibes=talibes, talibe_matricule=talibe_matricule,
    )


@bp.route("/nouveau", methods=["GET", "POST"])
@login_required
def creer():
    form = ProgressionForm()
    _charger_talibes(form)
    if not form.talibe_matricule.choices:
        flash("Créez d'abord un talibé : une progression concerne un talibé.", "info")
    if form.validate_on_submit():
        if not db.session.get(Talibe, form.talibe_matricule.data):
            flash("Talibé introuvable.", "error")
        else:
            progression = Progression(
                talibe_matricule=form.talibe_matricule.data,
                sourate=form.sourate.data,
                nombre_versets=form.nombre_versets.data,
                date_evaluation=form.date_evaluation.data,
                appreciation=form.appreciation.data or None,
            )
            db.session.add(progression)
            db.session.commit()
            flash("Progression ajoutée avec succès.", "success")
            return redirect(url_for("progressions.liste"))
    return render_template("progressions/form.html", form=form, mode="creer")


@bp.route("/<int:id>/modifier", methods=["GET", "POST"])
@login_required
def modifier(id):
    progression = _get_or_404(id)
    form = ProgressionForm(obj=progression)
    _charger_talibes(form)
    if request.method == "GET":
        form.talibe_matricule.data = progression.talibe_matricule
    if form.validate_on_submit():
        if not db.session.get(Talibe, form.talibe_matricule.data):
            flash("Talibé introuvable.", "error")
        else:
            progression.talibe_matricule = form.talibe_matricule.data
            progression.sourate = form.sourate.data
            progression.nombre_versets = form.nombre_versets.data
            progression.date_evaluation = form.date_evaluation.data
            progression.appreciation = form.appreciation.data or None
            db.session.commit()
            flash("Progression modifiée avec succès.", "success")
            return redirect(url_for("progressions.liste"))
    return render_template("progressions/form.html", form=form, mode="modifier", progression=progression)


@bp.route("/<int:id>/supprimer", methods=["POST"])
@login_required
def supprimer(id):
    progression = _get_or_404(id)
    db.session.delete(progression)
    db.session.commit()
    flash("Progression supprimée.", "info")
    return redirect(url_for("progressions.liste"))


@bp.route("/export")
@login_required
def exporter():
    progressions = Progression.query.order_by(Progression.date_evaluation.desc()).all()
    lignes = [
        [p.id, p.talibe.nom_complet, p.sourate, p.nombre_versets,
         p.date_evaluation.isoformat() if p.date_evaluation else "", p.appreciation]
        for p in progressions
    ]
    return reponse_csv(
        "progressions.csv",
        ["id", "talibe", "sourate", "nombre_versets", "date_evaluation", "appreciation"],
        lignes,
    )


def _get_or_404(id):
    progression = db.session.get(Progression, id)
    if progression is None:
        abort(404)
    return progression
