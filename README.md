# Task App — application de tâches en Flask

Projet pédagogique : on construit une petite application de gestion de tâches
(todo) avec **Flask**, **pas à pas**. Chaque grande étape vit sur sa propre
branche Git pour pouvoir être expliquée séparément.

## Stack technique

| Élément | Choix |
|---|---|
| Framework web | Flask 3 (application factory + blueprints) |
| Base de données | PostgreSQL (via Docker) |
| ORM / migrations | SQLAlchemy 2 + Flask-Migrate (Alembic) |
| Formulaires | Flask-WTF + WTForms (validation + protection CSRF) |
| Authentification | Flask-Login (sessions) + hash Werkzeug |
| Templates | Jinja2 (rendu côté serveur, **JavaScript minimal**) |
| Tests | pytest (base SQLite en mémoire) |

## Les étapes (branches Git)

1. **`etape-1-socle`** — fondations : factory, configuration, Docker, templates de base, tests.
2. **`etape-2-authentification`** — inscription, connexion, déconnexion.
3. **`etape-3-todo`** — gestion des tâches (créer, lister, terminer, modifier, supprimer).
4. **`etape-4-gestion-utilisateurs`** — profil et gestion des comptes.

Chaque branche est construite par-dessus la précédente.

## Démarrer avec Docker (recommandé)

```bash
cp .env.example .env          # créer sa configuration locale
docker compose up --build     # démarre PostgreSQL + l'application
```

L'application est disponible sur http://localhost:5000
(les migrations de base de données sont appliquées automatiquement au démarrage).

## Démarrer sans Docker

Il faut un PostgreSQL accessible (voir `DATABASE_URL` dans `.env`).

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

flask db upgrade   # crée les tables
flask run          # démarre le serveur de développement
```

## Lancer les tests

Les tests utilisent une base SQLite en mémoire : **aucun PostgreSQL ni Docker requis**.

```bash
source venv/bin/activate
pytest                       # lance tous les tests
pytest --cov=app             # avec la couverture de code
```

## Structure du projet

```
app/
├── __init__.py        # create_app() : la factory
├── config.py          # configurations development / testing / production
├── extensions.py      # instances des extensions (db, migrate, mail…)
├── models.py          # modèles SQLAlchemy : User, Category, Task
├── auth/              # module d'authentification        (étape 2)
├── tasks/             # module des tâches                 (étapes 1 et 3)
├── users/             # module de gestion des utilisateurs (étape 4)
├── templates/         # gabarits Jinja2 (base + partials)
└── static/css/        # feuille de style
migrations/            # migrations de base de données
tests/                 # tests pytest
```
