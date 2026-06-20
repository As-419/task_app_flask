# Image de l'application Flask.
FROM python:3.12-slim

# Bonnes pratiques Python en conteneur.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# On installe d'abord les dépendances (meilleure mise en cache des couches Docker).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Puis on copie le code de l'application.
COPY . .

EXPOSE 5000

# Commande par défaut (surchargée par docker-compose en développement).
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
