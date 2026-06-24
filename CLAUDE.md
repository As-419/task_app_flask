# CLAUDE.md — Gestion Daara (version web Flask)

Contexte pour les futures sessions Claude Code sur ce dépôt.

## But du projet

Version **web (Flask)** du **même sujet que le projet Java** : la gestion d'une
**daara** (école coranique). On gère **maîtres**, **classes** (halqas), **talibés**
et **progressions** de mémorisation du Coran, avec **export CSV**. Projet
**pédagogique** : clarté avant astuce, commentaires en français, **JavaScript minimal**
(rendu serveur Jinja + formulaires POST classiques ; seul `confirm()` est utilisé).

## Stack & choix arrêtés

- Flask 3 — **application factory** (`create_app`) + **blueprints** (un par entité).
- PostgreSQL en dev/prod ; **SQLite en mémoire** pour les tests.
- SQLAlchemy 2 (typé, `Mapped[...]`) + Flask-Migrate (Alembic).
- **Flask-WTF + WTForms** pour TOUS les formulaires (validation + CSRF).
- **Flask-Login** pour les sessions ; mots de passe hachés avec **werkzeug.security**.
- Jinja2 avec héritage : `base.html` + partials ; un dossier de templates par entité.

## Architecture par blueprint (≈ « un contrôleur par entité » en MVC)

Domaine métier « Daara » : **4 blueprints**, un par entité, plus l'infrastructure.

| Blueprint | Rôle |
|---|---|
| `main/` | accueil public + tableau de bord (compteurs) |
| `auth/` | inscription, connexion, déconnexion |
| `users/` | profil, mot de passe, suppression de compte |
| `maitres/` | CRUD maîtres + recherche + export CSV |
| `classes/` | CRUD classes (niveau + maître obligatoire) + recherche + export |
| `talibes/` | CRUD talibés (date, classe obligatoire) + recherche/filtre + export |
| `progressions/` | CRUD progressions (talibé obligatoire, versets ≥ 0) + filtre + export |

Chaque blueprint = `__init__.py` (le `Blueprint`), `routes.py` (vues), `forms.py`
(Flask-WTF), et ses gabarits dans `templates/<entité>/` (`liste.html`, `form.html`).
Les extensions sont créées sans app dans `extensions.py` et liées dans la factory.

## Modèle de données (`app/models.py`)

```
Maitre (matricule PK) 1 ──< Classe (code PK) 1 ──< Talibe (matricule PK) 1 ──< Progression (id auto)
```

- `User` : uniquement pour la connexion (le sujet n'impose pas l'auth ; l'app web
  expose un portail). Les données Daara sont **partagées** (pas de `user_id`).
- `Niveau` : enum (DEBUTANT / INTERMEDIAIRE / AVANCE).

## Règles métier (identiques au projet Java)

1. **Maître** : matricule unique ; suppression interdite s'il encadre ≥ 1 classe.
2. **Classe** : code unique ; **maître obligatoire** (`SelectField` alimenté en base) ;
   suppression interdite si ≥ 1 talibé.
3. **Talibé** : matricule unique ; **classe obligatoire** ; suppression → cascade
   des progressions (gérée par l'ORM, `cascade="all, delete-orphan"`).
4. **Progression** : **talibé obligatoire** ; `nombre_versets ≥ 0` (`NumberRange` +
   `CheckConstraint`) ; sourate non vide ; page filtrable par talibé.

Les listes déroulantes (maître/classe/talibé) sont **toujours** alimentées depuis la
base (`SelectField` avec `validate_choice=False` + revérification d'existence en route).
Les violations de règles sont signalées via `flash(..., "error")` (équivalent du
`JOptionPane` du projet Java).

## Export CSV

`app/csv_export.py` → `reponse_csv(nom, entetes, lignes)` construit une réponse HTTP
téléchargeable (UTF-8 + BOM pour Excel). Chaque liste a un bouton « Exporter CSV ».

## Commandes utiles

```bash
# Lancer l'app (dev, sans Docker) — nécessite PostgreSQL + .env
flask run
python run.py

# Docker (Postgres + web)
docker compose up --build

# Migrations
flask db migrate -m "message"
flask db upgrade

# Tests (SQLite en mémoire, pas besoin de Docker)
pytest
pytest --cov=app --cov-report=term-missing

# Vérification end-to-end live (serveur sur le port 5000)
python scripts/live_check.py
```

`app/config.py` charge `.env` depuis la racine du projet (robuste au cwd).
La config du serveur de preview est dans `.claude/launch.json`.

## Sécurité (acquis)

CSRF global (Flask-WTF), mots de passe hachés (werkzeug), requêtes via l'ORM (pas
d'injection SQL), redirection ouverte bouchée (`_safe_next_page`), gestionnaires 404/500,
validation de la couleur/dates/longueurs. `SECRET_KEY` et identifiants DB via `.env`
(non versionné).

## Outillage `.claude/` du projet

- **skills/** : `neversight/flask`, `neversight/pytest`, `linkxzhou/docker-docker`,
  `jeremylongshore/generating-docker-compose-files`.
- **rules/** : `common/` + `python/`.
- **agents/** : `python-reviewer`, `code-reviewer`, `security-reviewer`, `tdd-guide`, etc.
- **commands/** : `tdd`, `test-coverage`, `code-review`, `python-review`, `verify`, etc.

## Conventions de nommage

- Routes : `liste`, `creer`, `modifier`, `supprimer`, `exporter` par entité.
- Formulaires : `MaitreForm`, `ClasseForm`, `TalibeForm`, `ProgressionForm`.
- Templates : `templates/<entité>/{liste,form}.html`.
- Tests : `tests/test_<module>.py`, structure Arrange-Act-Assert.
