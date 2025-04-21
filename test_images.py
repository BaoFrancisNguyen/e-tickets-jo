from app import create_app, db
from app.models.offer import Offer
from app.config import Config

app = create_app(Config)

with app.app_context():
    # Définir un mapping spécifique pour chaque offre
    # Ajustez selon les noms de vos images et les titres de vos offres
    image_mapping = {
        "Natation 100m - Offre Solo": "swimming.jpg",
        "Gymnastique - Offre Duo": "gym.jpg",
        "Cérémonie d'ouverture - Offre Familiale": "ceremonie.jpg",
        "Athlétisme - 100m Finale - Offre Solo": "athletics.jpg",
        "Basketball - Demi-finale - Offre Duo": "basket.jpg"
    }
    
    # Mettre à jour chaque offre avec l'image correspondante
    offers = Offer.query.all()
    for offer in offers:
        if offer.titre in image_mapping:
            offer.image = image_mapping[offer.titre]
            print(f"Offre '{offer.titre}' - Nouvelle image : {offer.image}")
        else:
            # Pour les offres qui ne correspondent pas exactement, garder une image par défaut
            offer.image = "default-offer.jpg"
            print(f"Offre '{offer.titre}' - Image par défaut assignée")
    
    # Sauvegarder les modifications
    db.session.commit()
    print("Images mises à jour avec succès !")