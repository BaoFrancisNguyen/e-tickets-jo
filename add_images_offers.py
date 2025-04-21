from app import create_app, db
from app.models.offer import Offer

app = create_app()

with app.app_context():
    # Images disponibles dans le dossier uploads
    available_images = [
        'natation.jpg', 
        'athletisme.jpg', 
        'gymnastique.jpg', 
        'basketball.jpg', 
        'football.jpg',
        'equitation.jpg',
        'tennis.jpg',
        'judo.jpg',
        'cyclisme.jpg',
        'volleyball.jpg'
    ]
    
    # Récupérer toutes les offres
    offers = Offer.query.all()
    
    # Associer une image à chaque offre
    for i, offer in enumerate(offers):
        # Utiliser l'image disponible correspondant à l'index (en bouclant si nécessaire)
        image_index = i % len(available_images)
        offer.image = available_images[image_index]
    
    # Sauvegarder les modifications
    db.session.commit()
    print(f"Images associées à {len(offers)} offres avec succès!")