"""Routes du module des classes (halqas).

Règles métier (identiques au projet Java) :
- code unique (clé saisie) ;
- maître OBLIGATOIRE (liste déroulante alimentée depuis la base) ;
- suppression INTERDITE si la classe contient au moins un talibé.
"""
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.classes import bp
from app.classes.forms import ClasseForm
from app.csv_export import reponse_csv
from app.extensions import db
from app.models import Classe, Maitre, Niveau


def _charger_maitres(form):
    """Alimente la liste déroulante des maîtres."""
    form.maitre_matricule.choices = [
        (m.matricule, f"{m.nom_complet} ({m.matricule})")
        for m in Maitre.query.order_by(Maitre.nom_complet).all()
    ]


@bp.route("/")
@login_required
def liste():
    """Liste toutes les classes, avec recherche par libellé (par critère)."""
    recherche = request.args.get("q", "").strip()
    query = Classe.query
    if recherche:
        query = query.filter(Classe.libelle.ilike(f"%{recherche}%"))
    classes = query.order_by(Classe.libelle).all()
    return render_template("classes/liste.html", classes=classes, recherche=recherche)


@bp.route("/nouveau", methods=["GET", "POST"])
@login_required
def creer():
    form = ClasseForm()
    _charger_maitres(form)
    if not form.maitre_matricule.choices:
        flash("Créez d'abord un maître : une classe doit avoir un maître.", "info")
    if form.validate_on_submit():
        if db.session.get(Classe, form.code.data):
            flash(f"Une classe existe déjà avec le code {form.code.data}.", "error")
        elif not db.session.get(Maitre, form.maitre_matricule.data):
            flash("Maître introuvable.", "error")
        else:
            classe = Classe(
                code=form.code.data,
                libelle=form.libelle.data,
                niveau=Niveau[form.niveau.data],
                maitre_matricule=form.maitre_matricule.data,
            )
            db.session.add(classe)
            db.session.commit()
            flash("Classe ajoutée avec succès.", "success")
            return redirect(url_for("classes.liste"))
    return render_template("classes/form.html", form=form, mode="creer")


@bp.route("/<code>/modifier", methods=["GET", "POST"])
@login_required
def modifier(code):
    classe = _get_or_404(code)
    form = ClasseForm(obj=classe)
    _charger_maitres(form)
    if request.method == "GET":
        form.niveau.data = classe.niveau.name
        form.maitre_matricule.data = classe.maitre_matricule
    if form.validate_on_submit():
        if not db.session.get(Maitre, form.maitre_matricule.data):
            flash("Maître introuvable.", "error")
        else:
            classe.libelle = form.libelle.data
            classe.niveau = Niveau[form.niveau.data]
            classe.maitre_matricule = form.maitre_matricule.data
            db.session.commit()
            flash("Classe modifiée avec succès.", "success")
            return redirect(url_for("classes.liste"))
    return render_template("classes/form.html", form=form, mode="modifier", classe=classe)


@bp.route("/<code>/supprimer", methods=["POST"])
@login_required
def supprimer(code):
    classe = _get_or_404(code)
    if classe.talibes:
        flash(
            f"Suppression impossible : la classe {classe.libelle} contient "
            f"encore {len(classe.talibes)} talibé(s).",
            "error",
        )
        return redirect(url_for("classes.liste"))
    db.session.delete(classe)
    db.session.commit()
    flash("Classe supprimée.", "info")
    return redirect(url_for("classes.liste"))


@bp.route("/export")
@login_required
def exporter():
    classes = Classe.query.order_by(Classe.libelle).all()
    lignes = [
        [c.code, c.libelle, c.niveau.libelle, c.maitre.nom_complet]
        for c in classes
    ]
    return reponse_csv("classes.csv", ["code", "libelle", "niveau", "maitre"], lignes)


def _get_or_404(code):
    classe = db.session.get(Classe, code)
    if classe is None:
        abort(404)
    return classe
