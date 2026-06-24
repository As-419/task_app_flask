"""Routes du module des talibés (élèves).

Règles métier (identiques au projet Java) :
- matricule unique (clé saisie) ;
- classe OBLIGATOIRE (liste déroulante alimentée depuis la base) ;
- supprimer un talibé supprime aussi ses progressions (cascade).
"""
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.csv_export import reponse_csv
from app.extensions import db
from app.models import Classe, Talibe
from app.talibes import bp
from app.talibes.forms import TalibeForm


def _charger_classes(form):
    form.classe_code.choices = [
        (c.code, f"{c.libelle} ({c.code})")
        for c in Classe.query.order_by(Classe.libelle).all()
    ]


@bp.route("/")
@login_required
def liste():
    """Liste les talibés, avec recherche par nom et filtre par classe."""
    recherche = request.args.get("q", "").strip()
    classe_code = request.args.get("classe", "").strip()
    query = Talibe.query
    if recherche:
        query = query.filter(Talibe.nom.ilike(f"%{recherche}%"))
    if classe_code:
        query = query.filter_by(classe_code=classe_code)
    talibes = query.order_by(Talibe.nom, Talibe.prenom).all()
    classes = Classe.query.order_by(Classe.libelle).all()
    return render_template(
        "talibes/liste.html", talibes=talibes, classes=classes,
        recherche=recherche, classe_code=classe_code,
    )


@bp.route("/nouveau", methods=["GET", "POST"])
@login_required
def creer():
    form = TalibeForm()
    _charger_classes(form)
    if not form.classe_code.choices:
        flash("Créez d'abord une classe : un talibé doit être rattaché à une classe.", "info")
    if form.validate_on_submit():
        if db.session.get(Talibe, form.matricule.data):
            flash(f"Un talibé existe déjà avec le matricule {form.matricule.data}.", "error")
        elif not db.session.get(Classe, form.classe_code.data):
            flash("Classe introuvable.", "error")
        else:
            talibe = Talibe(
                matricule=form.matricule.data,
                prenom=form.prenom.data,
                nom=form.nom.data,
                date_naissance=form.date_naissance.data,
                nom_tuteur=form.nom_tuteur.data or None,
                telephone_tuteur=form.telephone_tuteur.data or None,
                classe_code=form.classe_code.data,
            )
            db.session.add(talibe)
            db.session.commit()
            flash("Talibé ajouté avec succès.", "success")
            return redirect(url_for("talibes.liste"))
    return render_template("talibes/form.html", form=form, mode="creer")


@bp.route("/<matricule>/modifier", methods=["GET", "POST"])
@login_required
def modifier(matricule):
    talibe = _get_or_404(matricule)
    form = TalibeForm(obj=talibe)
    _charger_classes(form)
    if request.method == "GET":
        form.classe_code.data = talibe.classe_code
    if form.validate_on_submit():
        if not db.session.get(Classe, form.classe_code.data):
            flash("Classe introuvable.", "error")
        else:
            talibe.prenom = form.prenom.data
            talibe.nom = form.nom.data
            talibe.date_naissance = form.date_naissance.data
            talibe.nom_tuteur = form.nom_tuteur.data or None
            talibe.telephone_tuteur = form.telephone_tuteur.data or None
            talibe.classe_code = form.classe_code.data
            db.session.commit()
            flash("Talibé modifié avec succès.", "success")
            return redirect(url_for("talibes.liste"))
    return render_template("talibes/form.html", form=form, mode="modifier", talibe=talibe)


@bp.route("/<matricule>/supprimer", methods=["POST"])
@login_required
def supprimer(matricule):
    """Supprime un talibé (et ses progressions, par cascade)."""
    talibe = _get_or_404(matricule)
    db.session.delete(talibe)
    db.session.commit()
    flash("Talibé supprimé (ainsi que ses progressions).", "info")
    return redirect(url_for("talibes.liste"))


@bp.route("/export")
@login_required
def exporter():
    talibes = Talibe.query.order_by(Talibe.nom, Talibe.prenom).all()
    lignes = [
        [t.matricule, t.prenom, t.nom,
         t.date_naissance.isoformat() if t.date_naissance else "",
         t.nom_tuteur, t.classe.libelle]
        for t in talibes
    ]
    return reponse_csv(
        "talibes.csv",
        ["matricule", "prenom", "nom", "date_naissance", "tuteur", "classe"],
        lignes,
    )


def _get_or_404(matricule):
    talibe = db.session.get(Talibe, matricule)
    if talibe is None:
        abort(404)
    return talibe
