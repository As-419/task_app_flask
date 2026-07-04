# CLAUDE.md — Gestion d'une Daara (projet d'examen Flask)

Contexte pour les futures sessions Claude Code sur ce dépôt.

## But du projet

Projet d'**examen** (ISI — Licence 2 Génie Logiciel) : application de gestion
d'une école coranique (daara). Le sujet complet et **obligatoire** est dans
[L2-GL-Projet-Flask.md](L2-GL-Projet-Flask.md) — le respecter à la lettre
(architecture, entités, exceptions, fonctionnalités). Public : étudiants
débutants, donc :

- **Privilégier la clarté sur l'astuce** ; petits fichiers, noms explicites.
- **Commentaires en français**, concis, qui expliquent *pourquoi*.
- **JavaScript au strict minimum** (uniquement le `confirm()` de suppression
  exigé par le sujet). Tout passe par du rendu serveur (Jinja) et des
  formulaires HTML classiques (POST).
- **Pas d'authentification** : le sujet ne la demande pas.

## Architecture imposée (MVC strict)

```
├── run.py                  # Point d'entrée
├── config.py               # DevelopmentConfig, ProductionConfig (PostgreSQL uniquement)
└── app/
    ├── __init__.py         # create_app() — app factory
    ├── extension.py        # db, migrate, csrf (init_app dans la factory)
    ├── models/             # Entités SQLAlchemy : base (abstrait), maitre, classe, talibe, progression
    ├── forms/              # WTForms (un module par entité) — aucun accès BDD
    ├── views/              # Blueprints (contrôleurs) : main, maitre, classe, talibe, progression
    ├── exceptions/         # DaaraException + hiérarchie (levées ET capturées dans views)
    ├── utils/              # csv_exporter.py — appelé par les vues uniquement
    └── templates/          # base.html + <entite>/liste.html, <entite>/formulaire.html
```

Points clés du sujet :
- Clés **saisies** (String, primary_key) pour Maitre/Classe/Talibe ; clé
  auto-incrémentée pour Progression uniquement.
- Les vues interrogent directement `db.session` / `Model.query`
  (pas de couche repository). Aucun SQL brut.
- Les SelectField (maître, classe, talibé) sont alimentés depuis la base
  **dans la vue** — jamais de saisie libre.
- Exceptions métier levées et capturées **dans les vues**, messages via `flash()`.
- Export CSV de la liste **affichée** (filtrée ou complète) via
  `utils/csv_exporter.py` (`Content-Disposition: attachment`).
- Suppression interdite si relation existante (maître→classes, classe→talibés) ;
  suppression d'un talibé en cascade sur ses progressions.

## Commandes utiles

```bash
docker compose up -d          # PostgreSQL (port hôte 5434, cf. .env)
flask db migrate -m "message" # migrations
flask db upgrade
flask run                     # http://127.0.0.1:5000
```

## Branches

Les branches `etape-1-socle` → `etape-4-gestion-utilisateurs` contiennent
l'ancien projet pédagogique (task app). Le projet Daara vit sur `projet-daara`.
