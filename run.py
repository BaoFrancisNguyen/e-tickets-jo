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
            prenom="JO E-Tickets",
            role="administrateur",
            est_verifie=True
        )
        if success:
            app.logger.info("Utilisateur administrateur créé avec succès")
        else:
            app.logger.error(f"Échec de la création de l'utilisateur administrateur: {admin_user}")

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