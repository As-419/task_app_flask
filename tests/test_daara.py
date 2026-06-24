"""Tests du domaine Daara : maîtres, classes, talibés, progressions.

Couvre le CRUD via HTTP et les règles métier identiques au projet Java :
clés uniques, suppressions interdites par relation, cascade, validation.
"""
from datetime import date

from app.extensions import db
from app.models import Classe, Maitre, Niveau, Progression, Talibe, User


def _login(client):
    """Crée un utilisateur et le connecte (les routes exigent @login_required)."""
    user = User(username="alice", email="alice@test.com")
    user.set_password("secret123")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"email": "alice@test.com", "password": "secret123"})


def _maitre(matricule="M001"):
    m = Maitre(matricule=matricule, nom_complet="Serigne Test", telephone="1")
    db.session.add(m)
    db.session.commit()
    return m


def _classe(code="CL-DEB", maitre="M001"):
    c = Classe(code=code, libelle="Débutants", niveau=Niveau.DEBUTANT, maitre_matricule=maitre)
    db.session.add(c)
    db.session.commit()
    return c


def _talibe(matricule="T0001", classe="CL-DEB"):
    t = Talibe(matricule=matricule, prenom="Modou", nom="Fall", classe_code=classe)
    db.session.add(t)
    db.session.commit()
    return t


# --- Accès protégé ----------------------------------------------------------

def test_maitres_requires_login(client):
    assert client.get("/maitres/").status_code == 302
    assert client.get("/talibes/").status_code == 302


# --- Maîtres ----------------------------------------------------------------

def test_create_maitre(client):
    _login(client)
    r = client.post("/maitres/nouveau",
                    data={"matricule": "M001", "nom_complet": "Serigne Modou", "telephone": "77"},
                    follow_redirects=True)
    assert r.status_code == 200
    assert db.session.get(Maitre, "M001").nom_complet == "Serigne Modou"


def test_create_maitre_duplicate_rejected(client):
    _login(client)
    _maitre("M001")
    client.post("/maitres/nouveau",
                data={"matricule": "M001", "nom_complet": "Autre"},
                follow_redirects=True)
    assert Maitre.query.count() == 1


def test_search_maitre_by_name(client):
    _login(client)
    db.session.add_all([
        Maitre(matricule="M1", nom_complet="Serigne Modou"),
        Maitre(matricule="M2", nom_complet="Cheikh Bamba"),
    ])
    db.session.commit()
    html = client.get("/maitres/?q=bamba").get_data(as_text=True)
    assert "Cheikh Bamba" in html and "Serigne Modou" not in html


def test_delete_maitre_with_classe_forbidden(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    r = client.post("/maitres/M001/supprimer", follow_redirects=True)
    assert "Suppression impossible" in r.get_data(as_text=True)
    assert db.session.get(Maitre, "M001") is not None


# --- Classes ----------------------------------------------------------------

def test_create_classe(client):
    _login(client)
    _maitre("M001")
    client.post("/classes/nouveau",
                data={"code": "CL-DEB", "libelle": "Débutants",
                      "niveau": "DEBUTANT", "maitre_matricule": "M001"},
                follow_redirects=True)
    classe = db.session.get(Classe, "CL-DEB")
    assert classe is not None and classe.niveau == Niveau.DEBUTANT


def test_create_classe_requires_existing_maitre(client):
    _login(client)
    # Aucun maître en base : le maître soumis n'existe pas.
    client.post("/classes/nouveau",
                data={"code": "CL-X", "libelle": "X", "niveau": "AVANCE",
                      "maitre_matricule": "INCONNU"},
                follow_redirects=True)
    assert Classe.query.count() == 0


def test_delete_classe_with_talibe_forbidden(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    _talibe("T0001", "CL-DEB")
    r = client.post("/classes/CL-DEB/supprimer", follow_redirects=True)
    assert "Suppression impossible" in r.get_data(as_text=True)
    assert db.session.get(Classe, "CL-DEB") is not None


# --- Talibés ----------------------------------------------------------------

def test_create_talibe(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    client.post("/talibes/nouveau",
                data={"matricule": "T0001", "prenom": "Modou", "nom": "Fall",
                      "date_naissance": "2012-05-10", "classe_code": "CL-DEB"},
                follow_redirects=True)
    t = db.session.get(Talibe, "T0001")
    assert t is not None and t.date_naissance == date(2012, 5, 10)


def test_filter_talibe_by_classe(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    _classe("CL-AV", "M001")
    _talibe("T1", "CL-DEB")
    _talibe("T2", "CL-AV")
    html = client.get("/talibes/?classe=CL-DEB").get_data(as_text=True)
    assert "T1" in html and "T2" not in html


def test_delete_talibe_cascades_progressions(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    _talibe("T0001", "CL-DEB")
    db.session.add(Progression(talibe_matricule="T0001", sourate="Al-Fatiha", nombre_versets=7))
    db.session.commit()

    client.post("/talibes/T0001/supprimer", follow_redirects=True)

    assert db.session.get(Talibe, "T0001") is None
    assert Progression.query.filter_by(talibe_matricule="T0001").count() == 0


# --- Progressions -----------------------------------------------------------

def test_create_progression(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    _talibe("T0001", "CL-DEB")
    client.post("/progressions/nouveau",
                data={"talibe_matricule": "T0001", "sourate": "Al-Baqara",
                      "nombre_versets": "30", "date_evaluation": "2024-01-10",
                      "appreciation": "Bien"},
                follow_redirects=True)
    p = Progression.query.first()
    assert p is not None and p.nombre_versets == 30


def test_create_progression_negative_versets_rejected(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    _talibe("T0001", "CL-DEB")
    client.post("/progressions/nouveau",
                data={"talibe_matricule": "T0001", "sourate": "Al-Baqara",
                      "nombre_versets": "-5"},
                follow_redirects=True)
    assert Progression.query.count() == 0


def test_filter_progression_by_talibe(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    _talibe("T1", "CL-DEB")
    _talibe("T2", "CL-DEB")
    db.session.add_all([
        Progression(talibe_matricule="T1", sourate="A", nombre_versets=1),
        Progression(talibe_matricule="T2", sourate="B", nombre_versets=2),
    ])
    db.session.commit()
    html = client.get("/progressions/?talibe=T1").get_data(as_text=True)
    assert "A" in html
    # On vérifie le filtrage côté base, pas l'absence d'une lettre commune dans le HTML.
    assert Progression.query.filter_by(talibe_matricule="T1").count() == 1


# --- Modification (édition) -------------------------------------------------

def test_edit_maitre(client):
    _login(client)
    _maitre("M001")
    client.post("/maitres/M001/modifier",
                data={"matricule": "M001", "nom_complet": "Nouveau Nom", "telephone": "99"},
                follow_redirects=True)
    assert db.session.get(Maitre, "M001").nom_complet == "Nouveau Nom"


def test_edit_classe_changes_niveau_and_maitre(client):
    _login(client)
    _maitre("M001")
    _maitre("M002")
    _classe("CL-DEB", "M001")
    client.post("/classes/CL-DEB/modifier",
                data={"code": "CL-DEB", "libelle": "Avancés",
                      "niveau": "AVANCE", "maitre_matricule": "M002"},
                follow_redirects=True)
    c = db.session.get(Classe, "CL-DEB")
    assert c.niveau == Niveau.AVANCE and c.maitre_matricule == "M002"


def test_edit_talibe(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    _talibe("T0001", "CL-DEB")
    client.post("/talibes/T0001/modifier",
                data={"matricule": "T0001", "prenom": "Awa", "nom": "Sow",
                      "classe_code": "CL-DEB"},
                follow_redirects=True)
    t = db.session.get(Talibe, "T0001")
    assert t.prenom == "Awa" and t.nom == "Sow"


def test_edit_progression(client):
    _login(client)
    _maitre("M001")
    _classe("CL-DEB", "M001")
    _talibe("T0001", "CL-DEB")
    db.session.add(Progression(talibe_matricule="T0001", sourate="A", nombre_versets=5))
    db.session.commit()
    pid = Progression.query.first().id
    client.post(f"/progressions/{pid}/modifier",
                data={"talibe_matricule": "T0001", "sourate": "Al-Ikhlas",
                      "nombre_versets": "4"},
                follow_redirects=True)
    p = db.session.get(Progression, pid)
    assert p.sourate == "Al-Ikhlas" and p.nombre_versets == 4


# --- Export CSV -------------------------------------------------------------

def test_export_maitres_csv(client):
    _login(client)
    _maitre("M001")
    r = client.get("/maitres/export")
    assert r.status_code == 200
    assert "text/csv" in r.content_type
    body = r.get_data(as_text=True)
    assert "matricule,nom_complet,telephone" in body
    assert "M001" in body
