from app import create_app, db
from app.models.offer import Offer
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Vérifier si des offres existent déjà
    existing_count = Offer.query.count()
    print(f"Nombre d'offres existantes : {existing_count}")
    
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
            est_publie=True
        ),
        Offer(
            titre="Gymnastique - Offre Duo",
            description="Billet pour 2 personnes pour assister aux épreuves de gymnastique artistique. Partagez ce moment unique avec votre accompagnateur.",
            type="duo",
            nombre_personnes=2,
            prix=90.0,
            date_evenement=date2,
            disponibilite=50,
            est_publie=True
        ),
        Offer(
            titre="Cérémonie d'ouverture - Offre Familiale",
            description="Billet pour 4 personnes pour assister à la cérémonie d'ouverture des JO. Vivez en famille ce moment historique et spectaculaire.",
            type="familiale",
            nombre_personnes=4,
            prix=180.0,
            date_evenement=date3,
            disponibilite=30,
            est_publie=True
        ),
        Offer(
            titre="Athlétisme - 100m Finale - Offre Solo",
            description="Billet individuel pour la finale du 100m hommes. Ne manquez pas l'épreuve reine de l'athlétisme.",
            type="solo",
            nombre_personnes=1,
            prix=65.0,
            date_evenement=date2,
            disponibilite=80,
            est_publie=True
        ),
        Offer(
            titre="Basketball - Demi-finale - Offre Duo",
            description="Billet pour 2 personnes pour assister à une demi-finale de basketball. Une ambiance électrique garantie !",
            type="duo",
            nombre_personnes=2,
            prix=120.0,
            date_evenement=date3,
            disponibilite=40,
            est_publie=True
        )
    ]
    
    # Ajouter les offres à la base de données
    db.session.add_all(offers)
    db.session.commit()
    
    # Vérifier que les offres ont été ajoutées
    new_count = Offer.query.count()
    print(f"Nombre d'offres après ajout : {new_count}")
    print(f"{len(offers)} offres ont été ajoutées avec succès !")