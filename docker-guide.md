# Guide Docker pour JO E-Tickets

Ce guide détaille l'utilisation de Docker avec l'application JO E-Tickets.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Structure Docker

L'application utilise une architecture multi-conteneurs avec Docker Compose :

- **web** : Service principal exécutant l'application Flask
- **db** : Base de données PostgreSQL
- **redis** : Serveur Redis pour la gestion des sessions
- **mailhog** : Serveur de mail pour le développement et les tests

## Configuration

1. **Variables d'environnement** :
   - Copiez le fichier `.env.example` vers `.env`
   - Modifiez les valeurs selon vos besoins (particulièrement les clés secrètes en production)

2. **Volumes** :
   - `postgres_data` : Persiste les données de la base PostgreSQL
   - `redis_data` : Stocke les données Redis
   - `./app/static/uploads` : Stocke les fichiers téléchargés par les utilisateurs

## Commandes utiles

### Démarrage de l'application

```bash
# Construire et démarrer tous les services en arrière-plan
docker-compose up -d

# Suivre les logs
docker-compose logs -f
```

### Arrêt de l'application

```bash
# Arrêter tous les conteneurs
docker-compose stop

# Arrêter et supprimer tous les conteneurs
docker-compose down

# Arrêter, supprimer les conteneurs et les volumes (efface toutes les données)
docker-compose down -v
```

### Gestion de la base de données

```bash
# Accéder au shell PostgreSQL
docker-compose exec db psql -U postgres -d jo_etickets

# Sauvegarder la base de données
docker-compose exec db pg_dump -U postgres jo_etickets > backup.sql

# Restaurer la base de données
cat backup.sql | docker-compose exec -T db psql -U postgres -d jo_etickets
```

### Autres commandes utiles

```bash
# Exécuter des migrations Flask
docker-compose exec web flask db upgrade

# Exécuter un shell Python dans le conteneur
docker-compose exec web python -c "from app import create_app; app = create_app(); print('Flask shell actif')"

# Reconstruire les images (en cas de modification des dépendances)
docker-compose build
```

## Développement avec Docker

Pour développer avec Docker :

1. **Hot Reload** : En mode développement, le code est automatiquement rechargé si vous montez le répertoire source comme volume :
   ```yaml
   volumes:
     - .:/app
   ```

2. **Déboguer** : Pour voir les logs de débogage en temps réel :
   ```bash
   docker-compose logs -f web
   ```

## Déploiement en production

Pour un déploiement en production :

1. **Modifiez les variables d'environnement** :
   - Générez des clés secrètes fortes
   - Configurez un serveur SMTP réel
   - Activez HTTPS

2. **Configuration de sécurité** :
   - Utilisez un serveur web frontal comme Nginx
   - Configurez SSL/TLS
   - Ajoutez des restrictions d'accès appropriées

3. **Sauvegarde** :
   - Mettez en place des sauvegardes automatiques de la base de données
   - Sauvegardez régulièrement les volumes Docker

## Dépannage

### Problèmes courants

1. **Le conteneur web ne démarre pas** :
   - Vérifiez les logs : `docker-compose logs web`
   - Vérifiez les variables d'environnement

2. **Problèmes de connexion à la base de données** :
   - Assurez-vous que le conteneur `db` est en cours d'exécution
   - Vérifiez la configuration de `DATABASE_URL`

3. **Erreurs "Permission denied"** :
   - Vérifiez les droits sur les volumes montés
   - Assurez-vous que l'utilisateur dans le conteneur a les droits d'accès nécessaires

### Réinitialisation complète

Si vous rencontrez des problèmes majeurs, vous pouvez réinitialiser complètement l'environnement :

```bash
# Arrêter et supprimer tous les conteneurs, volumes, réseaux
docker-compose down -v

# Supprimer les images
docker rmi $(docker images -q jo_etickets_*)

# Redémarrer
docker-compose up -d
```

## Ressources supplémentaires

- [Documentation Docker](https://docs.docker.com/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation Redis](https://redis.io/documentation)