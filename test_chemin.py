from app import create_app
from app.config import Config
import os

app = create_app(Config)

with app.app_context():
    # Vérifier le dossier static
    static_folder = app.static_folder
    print(f"Dossier static : {static_folder}")
    
    # Vérifier si le dossier images existe
    images_folder = os.path.join(static_folder, 'images')
    print(f"Dossier images : {images_folder}")
    print(f"Le dossier images existe : {os.path.exists(images_folder)}")
    
    # Vérifier si l'image default-offer.jpg existe
    default_image = os.path.join(images_folder, 'default-offer.jpg')
    print(f"Image par défaut : {default_image}")
    print(f"L'image par défaut existe : {os.path.exists(default_image)}")
    
    # Lister tous les fichiers dans le dossier images
    if os.path.exists(images_folder):
        print("\nContenu du dossier images :")
        for file in os.listdir(images_folder):
            print(f" - {file}")