# CLAUDE.md — Task App (projet pédagogique Flask)

Contexte pour les futures sessions Claude Code sur ce dépôt.

## But du projet

Application de tâches (todo) **pédagogique** : elle sert à enseigner Flask à des
étudiants **débutants**. Conséquences directes sur le style du code :

- **Privilégier la clarté sur l'astuce.** Le code doit être compréhensible par un débutant.
- **Commentaires en français**, concis, qui expliquent *pourquoi*.
- **JavaScript au strict minimum.** Tout passe par du rendu serveur (Jinja) et des
  formulaires HTML classiques (POST). N'ajouter du JS que si c'est réellement indispensable.
- Petits fichiers, petites fonctions, noms explicites.

## Stack & choix arrêtés

- Flask 3 — **application factory** (`create_app`) + **blueprints** (un par domaine).
- PostgreSQL via **Docker** en dev/prod ; **SQLite en mémoire** pour les tests.
- SQLAlchemy 2 (typé, `Mapped[...]`) + Flask-Migrate (Alembic).
- **Flask-WTF + WTForms** pour TOUS les formulaires (validation + CSRF).
- **Flask-Login** pour les sessions ; mots de passe hachés avec **werkzeug.security**
  (`generate_password_hash` / `check_password_hash`) — jamais en clair.
- Jinja2 avec héritage : `base.html` + partials dans `templates/partials/`.

## Architecture par blueprint

Chaque module (`auth/`, `tasks/`, `users/`) est un blueprint avec :
- `__init__.py` : définit le `Blueprint` et importe ses routes ;
- `routes.py` : les vues (logique HTTP) ;
- `forms.py` : les formulaires Flask-WTF ;
- ses gabarits dans `templates/<module>/`.

Les extensions sont créées **sans app** dans `extensions.py` et liées dans la factory
via `init_app(app)`. Les blueprints sont enregistrés dans `create_app()`.

## Modèle de branches (enseignement pas à pas)

Chaque grande étape = une branche, construite sur la précédente, et poussée :

1. `etape-1-socle` — fondations (factory, config, Docker, templates de base, tests).
2. `etape-2-authentification` — register / login / logout (Flask-Login + Flask-WTF).
3. `etape-3-todo` — CRUD des tâches, restreint à l'utilisateur connecté (`@login_required`).
4. `etape-4-gestion-utilisateurs` — profil, changement de mot de passe, gestion des comptes.

**Chaque branche doit livrer ses propres tests pytest** et rester verte avant le push.

## Commandes utiles

```bash
# Lancer l'app (dev, sans Docker)
flask run

# Lancer l'app complète avec Docker (Postgres + web)
docker compose up --build

# Migrations
flask db migrate -m "message"
flask db upgrade

# Tests (SQLite en mémoire, pas besoin de Docker)
pytest
pytest --cov=app --cov-report=term-missing
```

## Outillage `.claude/` du projet

- **skills/** : `neversight/flask`, `neversight/pytest`, `linkxzhou/docker-docker`,
  `jeremylongshore/generating-docker-compose-files`.
- **rules/** : `common/` + `python/` (style, tests, sécurité, git…).
- **agents/** : `python-reviewer`, `code-reviewer`, `security-reviewer`, `tdd-guide`, etc.
- **commands/** : `tdd`, `test-coverage`, `code-review`, `python-review`, `verify`, etc.

## Conventions de nommage

- Routes : verbe/nom clair (`home`, `login`, `register`, `task_create`).
- Formulaires : `LoginForm`, `RegisterForm`, `TaskForm`.
- Templates : `templates/<module>/<page>.html`.
- Tests : `tests/test_<module>.py`, structure Arrange-Act-Assert.
