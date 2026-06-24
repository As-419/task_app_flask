# Gestion Daara — version web (Flask)

Application web de gestion d'une **daara** (école coranique), **même sujet que le
projet Java** : on gère les **maîtres** (serignes), les **classes** (halqas), les
**talibés** (élèves) et leur **progression** dans la mémorisation du Coran, avec
**export CSV**. Projet pédagogique construit pas à pas avec **Flask**.

## Stack technique

| Élément | Choix |
|---|---|
| Framework web | Flask 3 (application factory + blueprints) |
| Base de données | PostgreSQL (via Docker ou serveur local) |
| ORM / migrations | SQLAlchemy 2 + Flask-Migrate (Alembic) |
| Formulaires | Flask-WTF + WTForms (validation + protection CSRF) |
| Authentification | Flask-Login (sessions) + hash Werkzeug |
| Templates | Jinja2 (rendu côté serveur, **JavaScript minimal**) |
| Tests | pytest (base SQLite en mémoire) |

## Domaine métier (identique au projet Java)

- **Maître** : matricule unique ; suppression interdite s'il encadre ≥ 1 classe.
- **Classe** : code unique ; **maître obligatoire** (liste déroulante) ; niveau
  (Débutant/Intermédiaire/Avancé) ; suppression interdite si ≥ 1 talibé.
- **Talibé** : matricule unique ; **classe obligatoire** ; date de naissance ;
  sa suppression supprime ses progressions (cascade).
- **Progression** : clé auto-générée ; **talibé obligatoire** ; `nombre_versets ≥ 0`
  et sourate non vide ; la page se filtre par talibé.

Chaque page propose : **lister, rechercher/filtrer, ajouter, modifier, supprimer,
exporter en CSV**. Un portail de **connexion** protège l'accès.

## Démarrer avec Docker (recommandé)

```bash
cp .env.example .env          # créer sa configuration locale
docker compose up --build     # démarre PostgreSQL + l'application
```

L'application est disponible sur http://localhost:5000
(les migrations sont appliquées automatiquement au démarrage).

## Démarrer sans Docker

Il faut un PostgreSQL accessible (voir `DATABASE_URL` dans `.env`).

```bash
python -m venv venv
source venv/Scripts/activate   # (Windows Git Bash)  ou  source venv/bin/activate
pip install -r requirements-dev.txt

flask db upgrade   # crée les tables
flask run          # démarre le serveur de développement
```

## Lancer les tests

Les tests utilisent une base SQLite en mémoire : **aucun PostgreSQL ni Docker requis**.

```bash
pytest                       # lance tous les tests
pytest --cov=app             # avec la couverture de code
```

Une vérification end-to-end manuelle contre le serveur live est disponible :
`python scripts/live_check.py` (serveur démarré sur le port 5000).

## Structure du projet

```
app/
├── __init__.py        # create_app() : la factory + enregistrement des blueprints
├── config.py          # configurations development / testing / production
├── extensions.py      # instances des extensions (db, migrate, login, csrf…)
├── models.py          # modèles SQLAlchemy : User, Maitre, Classe, Talibe, Progression
├── csv_export.py      # génération des réponses CSV (équivalent du CsvExporter Java)
├── main/              # accueil + tableau de bord
├── auth/              # inscription, connexion, déconnexion
├── users/             # profil et gestion du compte
├── maitres/           # CRUD des maîtres        (1 blueprint par entité = 1 contrôleur)
├── classes/           # CRUD des classes
├── talibes/           # CRUD des talibés
├── progressions/      # CRUD des progressions
├── templates/         # gabarits Jinja2 (base + partials + un dossier par entité)
└── static/css/        # feuille de style moderne
migrations/            # migrations de base de données
tests/                 # tests pytest
```
