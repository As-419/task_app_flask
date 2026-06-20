"""Fixtures partagées par tous les tests.

On crée une application en configuration "testing" (base SQLite en mémoire),
on génère le schéma avant chaque test puis on le supprime après. Les tests
sont ainsi isolés et ne dépendent ni de PostgreSQL ni de Docker.
"""
import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Application Flask configurée pour les tests."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Client HTTP de test (simule un navigateur)."""
    return app.test_client()
