"""Tests du module des tâches (CRUD + isolation entre utilisateurs)."""
from app.extensions import db
from app.models import Task, User


def _login(client, username="alice", email="alice@test.com", password="secret123"):
    """Crée un utilisateur et le connecte. Renvoie l'utilisateur."""
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"email": email, "password": password})
    return user


def _make_task(user, title="Ma tâche", priority="medium"):
    task = Task(user_id=user.id, title=title, priority=priority)
    db.session.add(task)
    db.session.commit()
    return task


# --- Accès protégé ----------------------------------------------------------

def test_task_list_requires_login(client):
    response = client.get("/tasks")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_home_redirects_logged_in_user_to_tasks(client):
    _login(client)
    response = client.get("/")
    assert response.status_code == 302
    assert "/tasks" in response.headers["Location"]


# --- Création ---------------------------------------------------------------

def test_create_task(client):
    user = _login(client)

    response = client.post(
        "/tasks/create",
        data={"title": "Acheter du pain", "description": "", "priority": "high"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Acheter du pain" in response.get_data(as_text=True)
    tasks = Task.query.filter_by(user_id=user.id).all()
    assert len(tasks) == 1
    assert tasks[0].title == "Acheter du pain"
    assert tasks[0].priority == "high"


def test_create_task_empty_title_rejected(client):
    user = _login(client)

    response = client.post(
        "/tasks/create",
        data={"title": "", "description": "", "priority": "medium"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert Task.query.filter_by(user_id=user.id).count() == 0


# --- Terminer / réactiver ---------------------------------------------------

def test_toggle_task(client):
    user = _login(client)
    task = _make_task(user)
    assert task.done is False

    client.post(f"/tasks/{task.id}/toggle")
    assert db.session.get(Task, task.id).done is True

    client.post(f"/tasks/{task.id}/toggle")
    assert db.session.get(Task, task.id).done is False


# --- Modification -----------------------------------------------------------

def test_edit_task(client):
    user = _login(client)
    task = _make_task(user, title="Ancien titre")

    response = client.post(
        f"/tasks/{task.id}/edit",
        data={"title": "Nouveau titre", "description": "détails", "priority": "low"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    updated = db.session.get(Task, task.id)
    assert updated.title == "Nouveau titre"
    assert updated.priority == "low"


# --- Suppression ------------------------------------------------------------

def test_delete_task(client):
    user = _login(client)
    task = _make_task(user)

    client.post(f"/tasks/{task.id}/delete")

    assert db.session.get(Task, task.id) is None


# --- Isolation entre utilisateurs ------------------------------------------

def test_cannot_access_another_users_task(client):
    # Alice possède une tâche.
    alice = _make_task(
        _create_only(username="alice", email="alice@test.com"), title="Tâche d'Alice"
    )
    # Bob se connecte et tente d'agir sur la tâche d'Alice.
    _login(client, username="bob", email="bob@test.com")

    assert client.get(f"/tasks/{alice.id}/edit").status_code == 404
    assert client.post(f"/tasks/{alice.id}/toggle").status_code == 404
    assert client.post(f"/tasks/{alice.id}/delete").status_code == 404

    # La tâche d'Alice est intacte.
    assert db.session.get(Task, alice.id) is not None


def _create_only(username, email, password="secret123"):
    """Crée un utilisateur SANS le connecter."""
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
