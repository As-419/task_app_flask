"""Tests « de fumée » (smoke tests) : vérifient que le socle fonctionne."""


def test_app_factory_creates_testing_app(app):
    # Arrange / Act : la fixture `app` a déjà créé l'application.
    # Assert
    assert app.config["TESTING"] is True


def test_home_page_returns_200(client):
    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "Gestion de la Daara" in response.get_data(as_text=True)


def test_unknown_page_returns_404(client):
    # Act
    response = client.get("/page-qui-nexiste-pas")

    # Assert
    assert response.status_code == 404
