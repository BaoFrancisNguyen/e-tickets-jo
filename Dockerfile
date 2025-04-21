# Utiliser Python 3.11 comme image de base
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Créer un utilisateur non-root pour exécuter l'application
RUN useradd -m appuser
USER appuser

# Exposer le port sur lequel l'application va tourner
EXPOSE 5000

# Variable d'environnement pour indiquer à Flask de s'exécuter en mode production
ENV FLASK_ENV=production

# Commande pour démarrer l'application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]