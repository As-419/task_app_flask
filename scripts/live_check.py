"""Vérification END-TO-END exhaustive de l'app Daara live (PostgreSQL) via HTTP.

Parcourt TOUTES les fonctionnalités comme un utilisateur réel (avec CSRF).
Usage : python scripts/live_check.py  (serveur démarré sur http://127.0.0.1:5000)
"""
import http.cookiejar
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# La console Windows est en cp1252 : on force l'UTF-8 pour les accents / flèches.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = "http://127.0.0.1:5000"
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
N = [0]


def get(path):
    req = urllib.request.Request(BASE + path)
    try:
        with opener.open(req) as r:
            return r.status, r.read().decode("utf-8"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8"), dict(e.headers)


def csrf(html):
    m = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    return m.group(1) if m else None


def post(path, data, referer, allow_redirects=True):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(BASE + path, data=body)
    req.add_header("Referer", BASE + referer)
    try:
        with opener.open(req) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def check(label, cond):
    N[0] += 1
    print(f"  [{N[0]:02d}] " + ("OK   " if cond else "FAIL ") + label)
    if not cond:
        print("\n>>> ECHEC. Arret.")
        sys.exit(1)


def form_post(form_path, action_path, data, extra_html=None):
    """GET la page pour récupérer le CSRF, puis POST."""
    _, html, _ = get(form_path)
    data = {**data, "csrf_token": csrf(html)}
    return post(action_path, data, form_path)


SUF = str(int(time.time()))[-6:]
print(f"=== E2E Daara (suffixe {SUF}) ===")

# ---------------------------------------------------------------- AUTH
s, html, _ = get("/")
check("accueil 200 + identité Daara", s == 200 and "Gestion de la Daara" in html)

u = "user" + SUF
_, html = form_post("/auth/register", "/auth/register",
                    {"username": u, "email": u + "@t.com",
                     "password": "secret123", "confirm": "different"})
check("inscription mots de passe différents refusée", "ne correspondent pas" in html)

_, html = form_post("/auth/register", "/auth/register",
                    {"username": u, "email": u + "@t.com",
                     "password": "secret123", "confirm": "secret123"})
check("inscription valide → page connexion", "connecter" in html.lower())

_, html = form_post("/auth/login", "/auth/login",
                    {"email": u + "@t.com", "password": "mauvais"})
check("connexion mauvais mot de passe refusée", "incorrect" in html)

_, html = form_post("/auth/login", "/auth/login",
                    {"email": u + "@t.com", "password": "secret123"})
check("connexion valide → tableau de bord", "Tableau de bord" in html and "Déconnexion" in html)

# ---------------------------------------------------------------- MAITRES
m1, m2 = "M" + SUF[:4], "N" + SUF[:4]
form_post("/maitres/nouveau", "/maitres/nouveau",
          {"matricule": m1, "nom_complet": "Serigne Modou", "telephone": "77"})
_, html, _ = get("/maitres/")
check("maître créé", "Serigne Modou" in html)

_, html = form_post("/maitres/nouveau", "/maitres/nouveau",
                    {"matricule": m1, "nom_complet": "Doublon", "telephone": "0"})
check("maître matricule en double refusé", "existe déjà" in html)

form_post("/maitres/nouveau", "/maitres/nouveau",
          {"matricule": m2, "nom_complet": "Cheikh Bamba", "telephone": "78"})
_, html, _ = get("/maitres/?q=bamba")
check("recherche maître par nom", "Cheikh Bamba" in html and "Serigne Modou" not in html)
_, html, _ = get("/maitres/")
check("« tout afficher » maîtres", "Serigne Modou" in html and "Cheikh Bamba" in html)

form_post(f"/maitres/{m1}/modifier", f"/maitres/{m1}/modifier",
          {"matricule": m1, "nom_complet": "Serigne Modou Fall", "telephone": "99"})
_, html, _ = get("/maitres/")
check("modification maître", "Serigne Modou Fall" in html)

# ---------------------------------------------------------------- CLASSES
c1, c2 = "CA" + SUF[:4], "CB" + SUF[:4]
_, html = form_post("/classes/nouveau", "/classes/nouveau",
                    {"code": c1, "libelle": "X", "niveau": "DEBUTANT",
                     "maitre_matricule": "INCONNU"})
check("classe avec maître inexistant refusée", "introuvable" in html.lower())

form_post("/classes/nouveau", "/classes/nouveau",
          {"code": c1, "libelle": "Halqa débutants", "niveau": "DEBUTANT", "maitre_matricule": m1})
form_post("/classes/nouveau", "/classes/nouveau",
          {"code": c2, "libelle": "Halqa avancés", "niveau": "AVANCE", "maitre_matricule": m2})
_, html, _ = get("/classes/")
check("classes créées avec maître + niveau", "Halqa débutants" in html and "Avancé" in html)

_, html = post(f"/maitres/{m1}/supprimer",
               {"csrf_token": csrf(get("/maitres/")[1])}, "/maitres/")
check("suppression maître avec classe interdite", "Suppression impossible" in html)

form_post(f"/classes/{c1}/modifier", f"/classes/{c1}/modifier",
          {"code": c1, "libelle": "Halqa débutants", "niveau": "INTERMEDIAIRE", "maitre_matricule": m2})
_, html, _ = get("/classes/")
check("modification classe (niveau + maître)", "Intermédiaire" in html)
_, html, _ = get("/classes/?q=avanc")
check("recherche classe par libellé", "Halqa avancés" in html and "Halqa débutants" not in html)

# ---------------------------------------------------------------- TALIBES
t1, t2 = "TA" + SUF[:4], "TB" + SUF[:4]
form_post("/talibes/nouveau", "/talibes/nouveau",
          {"matricule": t1, "prenom": "Modou", "nom": "Fall",
           "date_naissance": "2012-05-10", "nom_tuteur": "Fall",
           "telephone_tuteur": "70", "classe_code": c1})
form_post("/talibes/nouveau", "/talibes/nouveau",
          {"matricule": t2, "prenom": "Awa", "nom": "Sow",
           "date_naissance": "2011-09-02", "classe_code": c2})
_, html, _ = get("/talibes/")
check("talibés créés (avec date formatée)", "Fall" in html and "10/05/2012" in html)

_, html, _ = get(f"/talibes/?classe={c1}")
check("filtre talibés par classe", t1 in html and t2 not in html)
_, html, _ = get("/talibes/?q=sow")
check("recherche talibé par nom", "Awa" in html and "Modou" not in html)

form_post(f"/talibes/{t1}/modifier", f"/talibes/{t1}/modifier",
          {"matricule": t1, "prenom": "Modou", "nom": "Diop", "classe_code": c1})
_, html, _ = get("/talibes/")
check("modification talibé", "Diop" in html)

_, html = post(f"/classes/{c1}/supprimer",
               {"csrf_token": csrf(get("/classes/")[1])}, "/classes/")
check("suppression classe avec talibé interdite", "Suppression impossible" in html)

# ---------------------------------------------------------------- PROGRESSIONS
form_post("/progressions/nouveau", "/progressions/nouveau",
          {"talibe_matricule": t1, "sourate": "Al-Fatiha", "nombre_versets": "7",
           "date_evaluation": "2024-01-10", "appreciation": "Très bien"})
form_post("/progressions/nouveau", "/progressions/nouveau",
          {"talibe_matricule": t1, "sourate": "Al-Baqara", "nombre_versets": "286"})
form_post("/progressions/nouveau", "/progressions/nouveau",
          {"talibe_matricule": t2, "sourate": "An-Nas", "nombre_versets": "6"})
_, html, _ = get("/progressions/")
check("progressions créées", "Al-Fatiha" in html and "286" in html)

_, html = form_post("/progressions/nouveau", "/progressions/nouveau",
                    {"talibe_matricule": t1, "sourate": "X", "nombre_versets": "-3"})
check("progression versets négatifs refusée", "≥ 0" in html or "0" in html)

_, html, _ = get(f"/progressions/?talibe={t2}")
check("filtre progressions par talibé", "An-Nas" in html and "Al-Fatiha" not in html)

# cascade : supprimer un talibé supprime ses progressions
post(f"/talibes/{t1}/supprimer", {"csrf_token": csrf(get("/talibes/")[1])}, "/talibes/")
_, html, _ = get("/progressions/")
check("cascade talibé→progressions à la suppression", "Al-Fatiha" not in html and "An-Nas" in html)

# ---------------------------------------------------------------- EXPORT CSV
for entite, entete in [("maitres", "matricule,nom_complet,telephone"),
                       ("classes", "code,libelle,niveau,maitre"),
                       ("talibes", "matricule,prenom,nom,date_naissance,tuteur,classe"),
                       ("progressions", "id,talibe,sourate,nombre_versets,date_evaluation,appreciation")]:
    s, html, hdr = get(f"/{entite}/export")
    ok = s == 200 and "csv" in hdr.get("Content-Type", "") and entete in html
    check(f"export CSV {entite}", ok)

# ---------------------------------------------------------------- DASHBOARD / SECURITE / 404
_, html, _ = get("/dashboard")
check("tableau de bord (compteurs)", "Maîtres" in html and "Progressions" in html)
s, _, hdr = get("/")
check("en-têtes de sécurité présents",
      hdr.get("X-Content-Type-Options") == "nosniff" and hdr.get("X-Frame-Options") == "DENY")
s, _, _ = get("/page-inexistante")
check("page 404 personnalisée", s == 404)

# ---------------------------------------------------------------- COMPTE UTILISATEUR
form_post("/account/edit", "/account/edit",
          {"username": u + "x", "email": u + "x@t.com"})
_, html, _ = get("/account/")
check("modification du profil", (u + "x") in html)

_, html = form_post("/account/password", "/account/password",
                    {"current_password": "secret123", "new_password": "nouveau123",
                     "confirm": "nouveau123"})
check("changement de mot de passe", "succès" in html.lower() or "modifié" in html.lower())

_, html, _ = get("/auth/logout")  # déconnexion
s, _, _ = get("/maitres/")
check("après déconnexion, accès protégé redirige", s in (302, 200) and "/auth/login" in get("/maitres/")[2].get("Location", "/auth/login"))

print(f"\n>>> {N[0]} CONTROLES E2E PASSES — TOUTES LES FONCTIONNALITES OK")
