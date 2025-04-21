# JO E-Tickets

Application de billetterie électronique pour les Jeux olympiques 2024.

## Description

JO E-Tickets est une plateforme complète permettant l'achat et la gestion de billets électroniques pour les événements des Jeux olympiques de Paris 2024. L'application permet aux utilisateurs de créer un compte, de parcourir les offres disponibles, d'acheter des billets et de les présenter sous forme de QR code le jour de l'événement.

## Fonctionnalités

- Inscription et connexion des utilisateurs
- Authentification à deux facteurs
- Parcours et filtrage des offres
- Panier d'achat
- Paiement sécurisé (simulé)
- Génération de billets électroniques avec QR codes
- Vérification et validation des billets
- Administration des utilisateurs, offres, commandes et billets

## Démarrage rapide avec Docker

### Prérequis

- Docker
- Docker Compose

### Installation et lancement

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/username/jo-etickets.git
   cd jo-etickets
   ```

2. Créez un fichier `.env` à partir du modèle fourni :
   ```bash
   cp .env.example .env
   ```

3. Lancez l'application avec Docker Compose :
   ```bash
   docker-compose up -d
   ```

4. L'application est maintenant accessible à l'adresse http://localhost:5000

### Accès à l'administration

Un compte administrateur est automatiquement créé lors du premier démarrage :
- **Identifiant** : admin
- **Email** : admin@jo-etickets.fr
- **Mot de passe** : Admin123!

## Ports exposés

- **5000** : Application Flask
- **5432** : Base de données PostgreSQL
- **6379** : Redis
- **8025** : Interface web MailHog (pour tester les emails)

## Arrêt et nettoyage

Pour arrêter tous les conteneurs :
```bash
docker-compose down
```

Pour arrêter et supprimer tous les volumes (cette action supprimera toutes les données) :
```bash
docker-compose down -v
```

## Structure du projet

```
jo-etickets/
├── app/                  # Code source de l'application
│   ├── forms/            # Formulaires Flask-WTF
│   ├── models/           # Modèles SQLAlchemy
│   ├── routes/           # Routes et vues Flask
│   ├── services/         # Services métier
│   ├── static/           # Fichiers statiques (CSS, JS, images)
│   ├── templates/        # Templates Jinja2
│   ├── __init__.py       # Initialisation de l'application
│   └── config.py         # Configuration de l'application
├── init-db/              # Scripts d'initialisation de la base de données
├── .env.example          # Exemple de fichier de variables d'environnement
├── docker-compose.yml    # Configuration Docker Compose
├── Dockerfile            # Configuration Docker
├── requirements.txt      # Dépendances Python
└── run.py                # Point d'entrée de l'application
```

## Développement

Pour lancer l'application en mode développement sans Docker :

1. Créez un environnement virtuel Python :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez les variables d'environnement dans le fichier `.env`

4. Lancez l'application :
   ```bash
   flask run
   ```

## Tests

Pour exécuter les tests :
```bash
pytest
```

## Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

## Captures d'écran

![Page d'accueil](docs/screenshots/home.png)
![Liste des offres](docs/screenshots/offers.png)
![Détail du billet](docs/screenshots/ticket_detail.png)
![Administration](docs/screenshots/admin.png)