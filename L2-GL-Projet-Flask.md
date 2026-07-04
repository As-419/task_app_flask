Projet d'examen Flask — Gestion d'une Daara 

**PROJET D'EXAMEN** 

**Gestion d'une Daara** 

*Système de gestion d'une école coranique* 

**Flask • SQLAlchemy (ORM) • Jinja2 • Architecture MVC**

| Niveau  | Licence 2 — Génie Logiciel |
| :---: | :---: |
| **Groupe autorisé**  | 3 à 4 étudiants |

ISI — Licence 2 Génie Logiciel | Page 1   
Projet d'examen Flask — Gestion d'une Daara 

**1\. Contexte** 

Une daara (école coranique) souhaite informatiser sa gestion. Elle accueille des talibés répartis  dans des classes (halqas), chacune encadrée par un maître (serigne). Pour chaque talibé, la  daara enregistre la progression dans la mémorisation du Coran au fil des évaluations. 

Vous devez développer une application web avec **Flask** permettant de gérer les maîtres, les  classes, les talibés et leur progression, puis d'exporter les listes au format CSV. 

**2\. Objectifs pédagogiques** 

• **SQLAlchemy** (ORM) et leurs relations. 

• **MVC stricte** : Modèle / Vue (Blueprint) / Template (Jinja2). 

• **formulaires WTForms** avec validation côté serveur. 

• **hiérarchie d'exceptions métier** propre à chaque entité. 

• Réaliser des recherches par clé unique et par critère (liste filtrée). 

• **CSV** téléchargé depuis le navigateur. 

**3\. Contraintes techniques (obligatoires)** 

| Technologie  | Détail |
| :---- | :---- |
| Langage  | Python 3.11 ou supérieur |
| Framework web  | Flask (Blueprint, app factory) |
| ORM / Persistance  | Flask-SQLAlchemy — aucun SQL brut pour les opérations  CRUD |
| Migration BDD  | Flask-Migrate (Alembic) |
| Formulaires  | Flask-WTF / WTForms avec validation |
| Templates  | Jinja2 (intégré à Flask) |
| Base de données  | PostgreSQL uniquement. Seule l'URL dans config.py change  selon l'environnement. |
| Architecture  | MVC imposée (voir section 5\) |

**4\. Modèle de données** 

L'application comporte quatre entités. Les relations forment une chaîne : un maître encadre des  classes, une classe regroupe des talibés, un talibé possède un historique de progressions. 

**Relations** 

• **Classe → 1 Maître** (ForeignKey \+ relationship, obligatoire) 

• **Talibe → 1 Classe** (ForeignKey \+ relationship, obligatoire) 

• **Progression → 1 Talibe** (ForeignKey \+ relationship, obligatoire)

| Entité (table)  | Attributs principaux |
| :---- | :---- |

ISI — Licence 2 Génie Logiciel | Page 2   
Projet d'examen Flask — Gestion d'une Daara 

| Maitre (maitres)  | matricule\* (PK, String saisi), prenom, nom, telephone |
| ----- | :---- |
| Classe (classes)  | code\* (PK, String saisi), libelle, niveau, maitre\_matricule (FK) |
| Talibe (talibes)  | matricule\* (PK, String saisi), prenom, nom, date\_naissance,  nom\_tuteur, telephone\_tuteur, classe\_code (FK) |
| Progression (progressions)  | id (PK, Integer auto-incrémenté), sourate, nombre\_versets,  date\_evaluation, observations, talibe\_matricule (FK) |

**Important :** la clé de Progression est auto-générée (entier), alors que les clés de Maitre, Classe et  Talibe sont des **codes saisis** par l'utilisateur (primary\_key=True de type String). 

**Exemple de modèle attendu (entité Talibe)** 

| class Talibe(BaseModel):   \_\_tablename\_\_ \= "talibes"   \# Clé saisie par l'utilisateur   matricule \= db.Column(db.String(50), primary\_key=True)  prenom \= db.Column(db.String(100), nullable=False)  nom \= db.Column(db.String(100), nullable=False)  date\_naissance \= db.Column(db.Date)   nom\_tuteur \= db.Column(db.String(200))   telephone\_tuteur \= db.Column(db.String(20))   \# Compléter la classe |
| :---- |

**Classe de base BaseModel** 

Toutes les entités héritent de BaseModel (\_\_abstract\_\_ \= True). Cette classe fournit les  colonnes communes cree\_le et maj\_le. Ne pas créer de table pour cette classe. 

**5\. Architecture MVC imposée** 

L'organisation des fichiers doit reproduire exactement celle du modèle de référence MonBlog :

| daara/  ├── run.py \# Point d'entrée  ├── config.py \# DevelopmentConfig, ProductionConfig... ├── requirements.txt  └── app/   ├── \_\_init\_\_.py \# create\_app() — app factory   ├── extension.py \# db, migrate, csrf   ├── models/ \# Entités SQLAlchemy   │ ├── base.py \# BaseModel (abstrait)   │ ├── maitre.py   │ ├── classe.py   │ ├── talibe.py   │ └── progression.py   ├── forms/ \# Formulaires WTForms   │ ├── maitre.py   │ ├── classe.py   │ ├── talibe.py   │ └── progression.py   ├── views/ \# Blueprints Flask (Contrôleurs MVC) |
| :---- |

ISI — Licence 2 Génie Logiciel | Page 3   
Projet d'examen Flask — Gestion d'une Daara 

|  │ ├── main.py   │ ├── maitre.py   │ ├── classe.py   │ ├── talibe.py   │ └── progression.py   ├── exceptions/ \# Exceptions métier   │ └── \_\_init\_\_.py   ├── utils/ \# csv\_exporter.py   └── templates/ \# Jinja2   ├── base.html   ├── maitres/ (liste.html, formulaire.html)   ├── classes/   ├── talibes/   └── progressions/ |
| :---- |

**Rôle de chaque couche (obligatoire)** 

| Couche  | Rôle |
| :---- | :---- |
| models/  | Entités SQLAlchemy. Aucune logique d'interface, aucun accès  HTTP. |
| views/ (Blueprints)  | Reçoit la requête HTTP, interroge directement la base via  db.session et Model.query, valide le formulaire, capture les  exceptions, redirige ou rend le template. Aucun SQL brut. |
| forms/  | Définit les champs et règles de validation WTForms. Aucun accès  BDD. |
| templates/  | HTML \+ Jinja2. Affiche les données reçues. Aucune logique  métier. |
| exceptions/  | Hiérarchie d'exceptions métier. Levées dans les vues, capturées  dans les vues. |
| utils/csv\_exporter.py  | Génère la réponse HTTP CSV. Appelé par les vues uniquement. |

**Configuration PostgreSQL** 

| \# config.py  class DevelopmentConfig(BaseConfig):   DEBUG \= True   SQLALCHEMY\_DATABASE\_URI \= os.getenv(   'DEV\_DATABASE\_URL',   'postgresql+psycopg2://postgres:motdepasse@localhost:5432/daara'  ) |
| :---- |

**6\. Gestion des exceptions** 

Toutes les exceptions héritent de DaaraException (qui étend RuntimeError). Chaque entité  possède sa propre exception « introuvable » et « déjà existant ».

| DaaraException (extends RuntimeError)  ├── MaitreIntrouvableException | MaitreDejaExistantException ├── ClasseIntrouvableException | ClasseDejaExistanteException ├── TalibeIntrouvableException | TalibeDejaExistantException ├── ProgressionIntrouvableException | ProgressionInvalideException └── SuppressionImpossibleException (relation existante) |
| :---- |

ISI — Licence 2 Génie Logiciel | Page 4   
Projet d'examen Flask — Gestion d'une Daara 

**Quand lever chaque exception** 

• **XIntrouvableException** : recherche par clé ne trouve aucun résultat (modification,  suppression, affichage du détail). 

• **XDejaExistantException** : insertion d'une entité dont la clé saisie existe déjà. • **ProgressionInvalideException** : nombre\_versets \< 0, sourate vide, ou talibé non  renseigné. 

• **SuppressionImpossibleException** : suppression d'un maître ayant des classes, ou d'une  classe ayant des talibés. 

| class TalibeIntrouvableException(DaaraException):   def \_\_init\_\_(self, matricule: str):   super().\_\_init\_\_(f'Aucun talibé pour le matricule : {matricule}') |
| :---- |

**Règle :** les exceptions sont levées et capturées dans la couche **views**. Le template n'attrape  jamais d'exception. Les messages sont affichés via flash().

ISI — Licence 2 Génie Logiciel | Page 5   
Projet d'examen Flask — Gestion d'une Daara 

**7\. Couche Views — Blueprints Flask** 

Chaque Blueprint interroge directement la base via db.session et Model.query. Il n'y a pas de  couche repository intermédiaire. 

**Exemple — Blueprint Talibé** 

| bp\_talibes \= Blueprint('talibes', \_\_name\_\_, url\_prefix='/talibes')  @bp\_talibes.route('/')  def lister():   q \= request.args.get('q', '').strip()   classe\_code \= request.args.get('classe', '').strip()   query \= Talibe.query   if classe\_code:   query \= query.filter\_by(classe\_code=classe\_code)   if q:   query \= query.filter(   Talibe.nom.ilike(f'%{q}%') | Talibe.prenom.ilike(f'%{q}%')  )   talibes \= query.order\_by(Talibe.nom).all()   classes \= Classe.query.order\_by(Classe.libelle).all()   return render\_template('talibes/liste.html',   talibes=talibes, classes=classes, q=q)  @bp\_talibes.route('/nouveau', methods=\['GET', 'POST'\])  def creer():   form \= TalibeForm()   form.classe\_code.choices \= \[ \# SelectField alimenté BDD  (c.code, c.libelle) for c in Classe.query.all()   \]   if form.validate\_on\_submit():   if db.session.get(Talibe, form.matricule.data):   raise TalibeDejaExistantException(form.matricule.data)  talibe \= Talibe(   matricule=form.matricule.data,   prenom=form.prenom.data,   nom=form.nom.data,   classe\_code=form.classe\_code.data   )   db.session.add(talibe)   db.session.commit()   flash('Talibé ajouté.', 'success')   return redirect(url\_for('talibes.lister'))   return render\_template('talibes/formulaire.html', form=form, talibe=None)  @bp\_talibes.route('/\<matricule\>/supprimer', methods=\['POST'\])  def supprimer(matricule):   talibe \= db.session.get(Talibe, matricule)   if not talibe:   raise TalibeIntrouvableException(matricule)   db.session.delete(talibe) \# cascade supprime les progressions  db.session.commit()   flash('Talibé supprimé.', 'success')   return redirect(url\_for('talibes.lister')) |
| :---- |

**8\. Formulaires WTForms**

ISI — Licence 2 Génie Logiciel | Page 6   
Projet d'examen Flask — Gestion d'une Daara 

Chaque entité possède un formulaire dans forms/. Les champs SelectField pour maître, classe  et talibé sont obligatoirement alimentés depuis la base de données dans la vue — jamais une  saisie libre. 

| class TalibeForm(FlaskForm):   matricule \= StringField('Matricule',   validators=\[DataRequired(), Length(max=50)\])  prenom \= StringField('Prénom',   validators=\[DataRequired(), Length(max=100)\])  nom \= StringField('Nom',   validators=\[DataRequired(), Length(max=100)\])  date\_naissance \= DateField('Date de naissance', validators=\[Optional()\])  nom\_tuteur \= StringField('Nom du tuteur')   telephone\_tuteur \= StringField('Téléphone tuteur')   classe\_code \= SelectField('Classe', \# alimenté dans la vue  validators=\[DataRequired()\])   submit \= SubmitField('Enregistrer') |
| :---- |

**9\. Couche Templates (Jinja2)** 

Chaque entité possède deux templates : 

• **liste.html** : tableau des enregistrements \+ barre de recherche \+ bouton Exporter CSV \+  liens Modifier / Supprimer. 

• **formulaire.html** : formulaire de création et de modification. Le champ clé est en lecture  seule lors d'une modification. 

Tous les templates héritent de base.html qui contient la navbar, les messages flash() et le pied  de page. 

**Exemple — boucle d'affichage dans liste.html** 

| {% for t in talibes %}  \<tr\>   \<td\>{{ t.matricule }}\</td\>   \<td\>{{ t.prenom }} {{ t.nom }}\</td\>   \<td\>{{ t.classe.libelle }}\</td\>   \<td\>   \<a href="{{ url\_for('talibes.modifier', matricule=t.matricule)  }}"\>Modifier\</a\>   \<form method='post'   action="{{ url\_for('talibes.supprimer', matricule=t.matricule) }}"\>  {{ csrf\_token() }}   \<button onclick="return confirm('Supprimer ?')"\>Supprimer\</button\>  \</form\>   \</td\>  \</tr\>  {% endfor %} |
| :---- |

**10\. Export CSV (obligatoire)** 

Chaque page (Maître, Classe, Talibé, Progression) doit comporter un bouton « Exporter » qui  déclenche le téléchargement d'un fichier CSV : 

• ligne d'en-tête avec les noms des colonnes ;

ISI — Licence 2 Génie Logiciel | Page 7   
Projet d'examen Flask — Gestion d'une Daara 

• une ligne par enregistrement affiché (filtré ou complet), valeurs séparées par des virgules ; • **Content-Disposition: attachment**). 

Le code d'écriture va dans utils/csv\_exporter.py, appelé par la vue : 

| \# utils/csv\_exporter.py  def exporter\_csv(nom\_fichier: str, entetes: list, lignes: list):  output \= io.StringIO()   writer \= csv.writer(output)   writer.writerow(entetes)   for ligne in lignes:   writer.writerow(ligne)   response \= make\_response(output.getvalue())   response.headers\['Content-Disposition'\] \= \\   f'attachment; filename={nom\_fichier}'   response.headers\['Content-Type'\] \= 'text/csv; charset=utf-8'  return response |
| :---- |

Exemple de contenu CSV pour les talibés :

| matricule,prenom,nom,dateNaissance,classe  T0001,Modou,Fall,2012-05-10,CL-DEB  T0002,Awa,Sow,2011-09-02,CL-INT |
| :---- |

ISI — Licence 2 Génie Logiciel | Page 8 

**11\. Fonctionnalités demandées** 

Pour **chaque entité**, l'application doit offrir le cycle complet :   
Projet d'examen Flask — Gestion d'une Daara 

| Fonctionnalité  | Détail |
| :---- | :---- |
| Lister  | Afficher tous les enregistrements dans un tableau HTML. |
| Rechercher  | Filtrer le tableau selon un critère (nom, libellé…). Bouton «  Réinitialiser » pour supprimer le filtre. |
| Ajouter  | Formulaire de création avec validation des champs obligatoires  (WTForms). |
| Modifier  | Charger le formulaire avec les données existantes. La clé saisie est  en lecture seule. Enregistrer les changements. |
| Supprimer  | Bouton de suppression avec confirmation JavaScript, en respectant  les contraintes de relation. |
| Exporter  | Générer le fichier CSV de la liste affichée (filtrée ou complète). |

**Règles métier à respecter** 

• **Maître.** Le matricule est unique. Suppression INTERDITE si le maître encadre au moins une  classe. 

• **Classe.** Le code est unique. Une classe doit OBLIGATOIREMENT avoir un maître (liste  déroulante). Suppression INTERDITE si la classe contient au moins un talibé. • **Talibé.** Le matricule est unique. Un talibé doit OBLIGATOIREMENT être rattaché à une  classe (liste déroulante). Supprimer un talibé supprime aussi toutes ses progressions  (cascade). 

• **Progression.** Rattachée à un talibé (liste déroulante). nombre\_versets \>= 0 et sourate non  vide. La page Progressions doit pouvoir filtrer par talibé. 

**12\. Instructions de lancement** 

| \# 1\. Créer et activer l'environnement virtuel  python \-m venv venv  source venv/bin/activate \# Windows : venv\\Scripts\\activate  \# 2\. Installer les dépendances  pip install \-r requirements.txt  \# 3\. Créer la base de données PostgreSQL puis initialiser les migrations flask db init  flask db migrate \-m 'init'  flask db upgrade  \# 4\. Lancer l'application  flask run |
| :---- |

**13\. Critères d'évaluation**

| Critère  | Détail |
| :---- | :---- |

ISI — Licence 2 Génie Logiciel | Page 9   
Projet d'examen Flask — Gestion d'une Daara 

| Compréhension du code  | Chaque membre du groupe doit maîtriser l'ensemble du code. |
| :---- | ----- |
| Architecture MVC  | Respect strict de la séparation des couches (voir section 5). |
| Fonctionnalités  | Cycle complet pour les 4 entités (Lister, Rechercher, Ajouter,  Modifier, Supprimer, Exporter). |
| Exceptions métier  | Hiérarchie complète, levées et capturées au bon endroit. |
| Design (UX/UI)  | Interface claire et utilisable. |
| Qualité du code  | Code lisible, commenté, sans duplication. |

**Nombre de membres autorisé :** 3 à 4 étudiants.

ISI — Licence 2 Génie Logiciel | Page 10 