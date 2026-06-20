"""Tests du module d'authentification (inscription, connexion, déconnexion)."""
from app.extensions import db
from app.models import User


# --- Petites fonctions utilitaires -----------------------------------------

def _create_user(username="alice", email="alice@test.com", password="secret123"):
    """Crée un utilisateur directement en base (pour préparer un test)."""
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def register(client, username="bob", email="bob@test.com",
             password="secret123", confirm=None):
    return client.post(
        "/auth/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm": confirm if confirm is not None else password,
        },
        follow_redirects=True,
    )


def login(client, email="alice@test.com", password="secret123"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


# --- Hachage du mot de passe -----------------------------------------------

def test_password_is_hashed_not_stored_in_clear():
    user = User(username="z", email="z@test.com")
    user.set_password("secret123")

    assert user.password != "secret123"
    assert user.check_password("secret123") is True
    assert user.check_password("mauvais") is False


# --- Affichage des pages ----------------------------------------------------

def test_register_page_loads(client):
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert "Créer un compte" in response.get_data(as_text=True)


def test_login_page_loads(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "Se connecter" in response.get_data(as_text=True)


# --- Inscription ------------------------------------------------------------

def test_register_creates_user_and_redirects_to_login(client):
    response = register(client, username="bob", email="bob@test.com")

    assert response.status_code == 200
    assert "Se connecter" in response.get_data(as_text=True)
    assert User.query.filter_by(email="bob@test.com").first() is not None


def test_register_password_mismatch_shows_error(client):
    response = register(client, email="x@test.com",
                        password="secret123", confirm="different")

    assert "ne correspondent pas" in response.get_data(as_text=True)
    assert User.query.filter_by(email="x@test.com").first() is None


def test_register_duplicate_email_rejected(client):
    _create_user(username="alice", email="alice@test.com")

    response = register(client, username="autre", email="alice@test.com")

    assert "existe déjà" in response.get_data(as_text=True)
    assert User.query.filter_by(email="alice@test.com").count() == 1


# --- Connexion / déconnexion ------------------------------------------------

def test_login_success_shows_logged_in_navbar(client):
    _create_user(username="alice", email="alice@test.com", password="secret123")

    response = login(client, email="alice@test.com", password="secret123")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Bonjour, alice" in body
    assert "Déconnexion" in body


def test_login_wrong_password_rejected(client):
    _create_user(email="alice@test.com", password="secret123")

    response = login(client, email="alice@test.com", password="mauvais")

    body = response.get_data(as_text=True)
    assert "incorrect" in body
    assert "Déconnexion" not in body


def test_logout_requires_login(client):
    response = client.get("/auth/logout")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_logout_logs_user_out(client):
    _create_user(email="alice@test.com", password="secret123")
    login(client, email="alice@test.com", password="secret123")

    response = client.get("/auth/logout", follow_redirects=True)

    body = response.get_data(as_text=True)
    assert "déconnecté" in body
    assert "Connexion" in body
