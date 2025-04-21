from datetime import datetime
from app import db

class Offer(db.Model):
    __tablename__ = 'offers'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'solo', 'duo', 'familiale'
    nombre_personnes = db.Column(db.Integer, nullable=False)  # 1, 2 ou 4
    prix = db.Column(db.Float, nullable=False)
    disponibilite = db.Column(db.Integer, nullable=False, default=100)  # Nombre de billets disponibles
    date_evenement = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.String(255), nullable=True)  # URL de l'image
    est_publie = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    tickets = db.relationship('Ticket', backref='offer', lazy=True)
    
    def __init__(self, titre, description, type, nombre_personnes, prix, date_evenement, 
                 disponibilite=100, image=None, est_publie=True):
        self.titre = titre
        self.description = description
        self.type = type
        self.nombre_personnes = nombre_personnes
        self.prix = prix
        self.date_evenement = date_evenement
        self.disponibilite = disponibilite
        self.image = image
        self.est_publie = est_publie
    
    def is_available(self):
        """Vérifie si l'offre est disponible."""
        return self.est_publie and self.disponibilite > 0 and self.date_evenement > datetime.utcnow()
    
    def decrease_availability(self, quantity=1):
        """Diminue la disponibilité de l'offre."""
        if self.disponibilite >= quantity:
            self.disponibilite -= quantity
            db.session.commit()
            return True
        return False
    
    def increase_availability(self, quantity=1):
        """Augmente la disponibilité de l'offre."""
        self.disponibilite += quantity
        db.session.commit()
        return True
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'titre': self.titre,
            'description': self.description,
            'type': self.type,
            'nombre_personnes': self.nombre_personnes,
            'prix': self.prix,
            'disponibilite': self.disponibilite,
            'date_evenement': self.date_evenement.isoformat(),
            'image': self.image,
            'est_publie': self.est_publie
        }
    
    def __repr__(self):
        return f"Offer('{self.titre}', '{self.type}', '{self.prix}€')"
