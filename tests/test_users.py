"""Tests du module de gestion du compte (profil, mot de passe, suppression)."""
from app.extensions import db
from app.models import User


def _login(client, username="alice", email="alice@test.com", password="secret123"):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"email": email, "password": password})
    return user


# --- Accès protégé ----------------------------------------------------------

def test_profile_requires_login(client):
    response = client.get("/account/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_profile_shows_user_info(client):
    _login(client, username="alice", email="alice@test.com")
    response = client.get("/account/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "alice" in body
    assert "alice@test.com" in body


# --- Modification du profil -------------------------------------------------

def test_edit_profile_updates_user(client):
    user = _login(client)

    response = client.post(
        "/account/edit",
        data={"username": "alice2", "email": "alice2@test.com"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    refreshed = db.session.get(User, user.id)
    assert refreshed.username == "alice2"
    assert refreshed.email == "alice2@test.com"


def test_edit_profile_duplicate_email_rejected(client):
    # Un autre utilisateur occupe déjà cet email.
    other = User(username="bob", email="bob@test.com")
    other.set_password("secret123")
    db.session.add(other)
    db.session.commit()

    user = _login(client, username="alice", email="alice@test.com")

    response = client.post(
        "/account/edit",
        data={"username": "alice", "email": "bob@test.com"},
        follow_redirects=True,
    )

    assert "déjà utilisé" in response.get_data(as_text=True)
    # L'email d'Alice n'a pas changé.
    assert db.session.get(User, user.id).email == "alice@test.com"


# --- Changement de mot de passe --------------------------------------------

def test_change_password_success(client):
    user = _login(client, password="ancien123")

    response = client.post(
        "/account/password",
        data={
            "current_password": "ancien123",
            "new_password": "nouveau123",
            "confirm": "nouveau123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    refreshed = db.session.get(User, user.id)
    assert refreshed.check_password("nouveau123") is True
    assert refreshed.check_password("ancien123") is False


def test_change_password_wrong_current_rejected(client):
    user = _login(client, password="ancien123")

    response = client.post(
        "/account/password",
        data={
            "current_password": "mauvais",
            "new_password": "nouveau123",
            "confirm": "nouveau123",
        },
        follow_redirects=True,
    )

    assert "incorrect" in response.get_data(as_text=True)
    assert db.session.get(User, user.id).check_password("ancien123") is True


# --- Suppression du compte --------------------------------------------------

def test_delete_account_removes_user(client):
    user = _login(client)
    user_id = user.id

    response = client.post("/account/delete", follow_redirects=True)

    assert response.status_code == 200
    assert db.session.get(User, user_id) is None
