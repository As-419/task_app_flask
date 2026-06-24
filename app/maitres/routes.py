"""Routes du module des maîtres.

Règles métier (identiques au projet Java) :
- matricule unique (clé saisie) ;
- suppression INTERDITE si le maître encadre au moins une classe.
"""
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.csv_export import reponse_csv
from app.extensions import db
from app.maitres import bp
from app.maitres.forms import MaitreForm
from app.models import Maitre


@bp.route("/")
@login_required
def liste():
    """Liste tous les maîtres, avec recherche par nom (par critère)."""
    recherche = request.args.get("q", "").strip()
    query = Maitre.query
    if recherche:
        query = query.filter(Maitre.nom_complet.ilike(f"%{recherche}%"))
    maitres = query.order_by(Maitre.nom_complet).all()
    return render_template("maitres/liste.html", maitres=maitres, recherche=recherche)


@bp.route("/nouveau", methods=["GET", "POST"])
@login_required
def creer():
    """Crée un nouveau maître (refuse un matricule déjà existant)."""
    form = MaitreForm()
    if form.validate_on_submit():
        if db.session.get(Maitre, form.matricule.data):
            flash(f"Un maître existe déjà avec le matricule {form.matricule.data}.", "error")
        else:
            maitre = Maitre(
                matricule=form.matricule.data,
                nom_complet=form.nom_complet.data,
                telephone=form.telephone.data or None,
            )
            db.session.add(maitre)
            db.session.commit()
            flash("Maître ajouté avec succès.", "success")
            return redirect(url_for("maitres.liste"))
    return render_template("maitres/form.html", form=form, mode="creer")


@bp.route("/<matricule>/modifier", methods=["GET", "POST"])
@login_required
def modifier(matricule):
    """Modifie un maître existant (le matricule n'est pas modifiable)."""
    maitre = _get_or_404(matricule)
    form = MaitreForm(obj=maitre)
    if form.validate_on_submit():
        maitre.nom_complet = form.nom_complet.data
        maitre.telephone = form.telephone.data or None
        db.session.commit()
        flash("Maître modifié avec succès.", "success")
        return redirect(url_for("maitres.liste"))
    return render_template("maitres/form.html", form=form, mode="modifier", maitre=maitre)


@bp.route("/<matricule>/supprimer", methods=["POST"])
@login_required
def supprimer(matricule):
    """Supprime un maître, sauf s'il encadre au moins une classe."""
    maitre = _get_or_404(matricule)
    if maitre.classes:
        flash(
            f"Suppression impossible : le maître {maitre.nom_complet} encadre "
            f"encore {len(maitre.classes)} classe(s).",
            "error",
        )
        return redirect(url_for("maitres.liste"))
    db.session.delete(maitre)
    db.session.commit()
    flash("Maître supprimé.", "info")
    return redirect(url_for("maitres.liste"))


@bp.route("/export")
@login_required
def exporter():
    """Exporte la liste des maîtres au format CSV."""
    maitres = Maitre.query.order_by(Maitre.nom_complet).all()
    lignes = [[m.matricule, m.nom_complet, m.telephone] for m in maitres]
    return reponse_csv("maitres.csv", ["matricule", "nom_complet", "telephone"], lignes)


def _get_or_404(matricule):
    from flask import abort
    maitre = db.session.get(Maitre, matricule)
    if maitre is None:
        abort(404)
    return maitre
