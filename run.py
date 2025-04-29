from flask import Flask
from app import create_app, db
from app.models import User, Offer, Order, Ticket

# Création de l'application
app = create_app()

# Fonction d'initialisation à exécuter au démarrage de l'application
def init_app():
    """
    Initialisation de l'application au démarrage.
    Remplace l'ancien décorateur before_first_request qui a été supprimé dans Flask 2.x
    """
    # Créer les tables si elles n'existent pas
    db.create_all()
    
    # Créer un utilisateur administrateur par défaut si aucun n'existe
    admin_exists = User.query.filter_by(role='administrateur').first()
    if not admin_exists:
        from app.services.auth_service import register_user
        success, admin_user = register_user(
            username="admin",
            email="admin@jo-etickets.fr",
            password="AdminSecure123!",
            nom="Admin",
            prenom="JO E-Tickets"
        )
        if success:
            # Modifier manuellement le rôle de l'utilisateur après sa création
            admin_user.role = "administrateur"
            db.session.commit()
            app.logger.info("Utilisateur administrateur créé avec succès")
        else:
            app.logger.error(f"Échec de la création de l'utilisateur administrateur: {admin_user}")
    
    # Initialiser les données de l'application (offres)
    try:
        # Vérifier si des offres existent déjà
        offers_count = Offer.query.count()
        if offers_count == 0:
            # Création des offres
            from datetime import datetime, timedelta
            
            # Dates futures pour les événements
            date1 = datetime.now() + timedelta(days=30)
            date2 = datetime.now() + timedelta(days=32)
            date3 = datetime.now() + timedelta(days=35)
            
            # Créer des offres
            offers = [
                Offer(
                    titre="Natation 100m - Offre Solo",
                    description="Billet individuel pour la finale du 100m nage libre. Assistez à l'une des épreuves les plus attendues des Jeux olympiques.",
                    type="solo",
                    nombre_personnes=1,
                    prix=50.0,
                    date_evenement=date1,
                    disponibilite=100,
                    est_publie=True,
                    image="natation.jpg"
                ),
                Offer(
                    titre="Gymnastique - Offre Duo",
                    description="Billet pour 2 personnes pour assister aux épreuves de gymnastique artistique. Partagez ce moment unique avec votre accompagnateur.",
                    type="duo",
                    nombre_personnes=2,
                    prix=90.0,
                    date_evenement=date2,
                    disponibilite=50,
                    est_publie=True,
                    image="gymnastique.jpg"
                ),
                Offer(
                    titre="Cérémonie d'ouverture - Offre Familiale",
                    description="Billet pour 4 personnes pour assister à la cérémonie d'ouverture des JO. Vivez en famille ce moment historique et spectaculaire.",
                    type="familiale",
                    nombre_personnes=4,
                    prix=180.0,
                    date_evenement=date3,
                    disponibilite=30,
                    est_publie=True,
                    image="athletisme.jpg"
                ),
                Offer(
                    titre="Athlétisme - 100m Finale - Offre Solo",
                    description="Billet individuel pour la finale du 100m hommes. Ne manquez pas l'épreuve reine de l'athlétisme.",
                    type="solo",
                    nombre_personnes=1,
                    prix=65.0,
                    date_evenement=date2,
                    disponibilite=80,
                    est_publie=True,
                    image="athletisme.jpg"
                ),
                Offer(
                    titre="Basketball - Demi-finale - Offre Duo",
                    description="Billet pour 2 personnes pour assister à une demi-finale de basketball. Une ambiance électrique garantie !",
                    type="duo",
                    nombre_personnes=2,
                    prix=120.0,
                    date_evenement=date3,
                    disponibilite=40,
                    est_publie=True,
                    image="basketball.jpg"
                )
            ]
            
            # Ajouter les offres à la base de données
            db.session.add_all(offers)
            db.session.commit()
            app.logger.info(f"{len(offers)} offres ont été ajoutées avec succès !")
        else:
            app.logger.info(f"{offers_count} offres existantes, aucune nouvelle offre ajoutée.")
    except Exception as e:
        app.logger.error(f"Erreur lors de l'initialisation des offres: {str(e)}")

    # Toute autre initialisation nécessaire
    app.logger.info("Application initialisée avec succès")

# Exécuter l'initialisation au démarrage plutôt qu'à la première requête
with app.app_context():
    init_app()

# Définition des commandes CLI (si nécessaire)
@app.cli.command("init-db")
def init_db_command():
    """Initialise la base de données."""
    db.drop_all()
    db.create_all()
    # Ajouter des données initiales si nécessaire
    print("Base de données initialisée.")

@app.shell_context_processor
def make_shell_context():
    """Configure les imports automatiques dans le shell Flask."""
    return {
        "db": db,
        "User": User,
        "Offer": Offer,
        "Order": Order,
        "Ticket": Ticket
    }

# Point d'entrée pour Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)