"""Routes du module des tâches.

Toutes les opérations sur les tâches exigent d'être connecté (@login_required)
et ne concernent QUE les tâches de l'utilisateur courant.
"""
from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Task
from app.tasks import bp
from app.tasks.forms import TaskForm


@bp.route("/")
def home():
    """Page d'accueil : tableau des tâches si connecté, sinon page d'accueil."""
    if current_user.is_authenticated:
        return redirect(url_for("tasks.task_list"))
    return render_template("home.html")


@bp.route("/tasks")
@login_required
def task_list():
    """Liste les tâches de l'utilisateur connecté + formulaire d'ajout."""
    tasks = (
        Task.query.filter_by(user_id=current_user.id)
        .order_by(Task.created_at.desc())
        .all()
    )
    form = TaskForm()
    return render_template("tasks/list.html", tasks=tasks, form=form)


@bp.route("/tasks/create", methods=["POST"])
@login_required
def task_create():
    """Crée une nouvelle tâche pour l'utilisateur connecté."""
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data or None,
            priority=form.priority.data,
        )
        db.session.add(task)
        db.session.commit()
        flash("Tâche ajoutée.", "success")
        return redirect(url_for("tasks.task_list"))

    # Saisie invalide : on réaffiche la liste avec le formulaire et ses erreurs.
    tasks = (
        Task.query.filter_by(user_id=current_user.id)
        .order_by(Task.created_at.desc())
        .all()
    )
    return render_template("tasks/list.html", tasks=tasks, form=form)


@bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def task_toggle(task_id):
    """Bascule l'état « terminé » d'une tâche."""
    task = _get_own_task_or_404(task_id)
    task.done = not task.done
    db.session.commit()
    return redirect(url_for("tasks.task_list"))


@bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def task_edit(task_id):
    """Modifie une tâche existante."""
    task = _get_own_task_or_404(task_id)
    form = TaskForm(obj=task)  # pré-remplit le formulaire avec la tâche
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data or None
        task.priority = form.priority.data
        db.session.commit()
        flash("Tâche modifiée.", "success")
        return redirect(url_for("tasks.task_list"))
    return render_template("tasks/edit.html", form=form, task=task)


@bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def task_delete(task_id):
    """Supprime une tâche."""
    task = _get_own_task_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Tâche supprimée.", "info")
    return redirect(url_for("tasks.task_list"))


def _get_own_task_or_404(task_id):
    """Récupère une tâche SI elle appartient à l'utilisateur connecté.

    Sinon renvoie une erreur 404 (on ne révèle pas l'existence de la tâche
    d'un autre utilisateur).
    """
    task = db.session.get(Task, task_id)
    if task is None or task.user_id != current_user.id:
        abort(404)
    return task
