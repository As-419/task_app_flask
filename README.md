# Gestion d'une Daara — projet d'examen Flask

Application web de gestion d'une école coranique (daara) : maîtres (serignes),
classes (halqas), talibés et suivi de leur progression dans la mémorisation du
Coran, avec export CSV. Sujet complet : [L2-GL-Projet-Flask.md](L2-GL-Projet-Flask.md).

## Stack technique (contraintes du sujet)

| Élément | Choix |
|---|---|
| Framework web | Flask 3 (application factory + blueprints) |
| ORM / persistance | Flask-SQLAlchemy (aucun SQL brut) |
| Migrations | Flask-Migrate (Alembic) |
| Formulaires | Flask-WTF + WTForms (validation + protection CSRF) |
| Templates | Jinja2 (rendu côté serveur) |
| Base de données | PostgreSQL uniquement |
| Architecture | MVC stricte : `models/` / `views/` (blueprints) / `templates/` |

## Architecture

```
├── run.py                  # Point d'entrée
├── config.py               # DevelopmentConfig, ProductionConfig
├── requirements.txt
└── app/
    ├── __init__.py         # create_app() — app factory
    ├── extension.py        # db, migrate, csrf
    ├── models/             # Entités SQLAlchemy (base, maitre, classe, talibe, progression)
    ├── forms/              # Formulaires WTForms (un par entité)
    ├── views/              # Blueprints Flask — contrôleurs MVC (main + un par entité)
    ├── exceptions/         # Hiérarchie d'exceptions métier (DaaraException...)
    ├── utils/              # csv_exporter.py (export CSV téléchargeable)
    └── templates/          # Jinja2 : base.html + liste.html / formulaire.html par entité
```

Pour chaque entité (Maître, Classe, Talibé, Progression) : **Lister,
Rechercher, Ajouter, Modifier, Supprimer, Exporter CSV**.

Règles métier : matricules/codes uniques, suppression interdite si relation
existante (maître→classes, classe→talibés), suppression d'un talibé en cascade
sur ses progressions, progression invalide refusée (versets < 0, sourate vide).

## Lancement

```bash
# 0. (Option) Démarrer PostgreSQL avec Docker (port hôte 5434) :
cp .env.example .env
docker compose up -d

# 1. Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Initialiser les migrations (la base "daara" doit exister)
flask db init
flask db migrate -m 'init'
flask db upgrade

# 4. Lancer l'application
flask run
```

L'application est disponible sur http://127.0.0.1:5000.

> Sans Docker : créez une base PostgreSQL `daara` et renseignez
> `DEV_DATABASE_URL` dans `.env` (seule l'URL change selon l'environnement).
