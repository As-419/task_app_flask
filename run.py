"""Point d'entrée de l'application.

Lancement en développement :
    flask run
    # ou
    python run.py
"""
from app import create_app

# create_app() lit la variable d'environnement FLASK_CONFIG (par défaut "development").
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
