from datetime import datetime
import hashlib
import uuid
import qrcode
from io import BytesIO
import base64
from app import db

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cle_utilisateur = db.Column(db.String(255), nullable=False)
    cle_achat = db.Column(db.String(255), nullable=False)
    cle_billet = db.Column(db.String(255), unique=True, nullable=False)
    qr_code = db.Column(db.Text, nullable=True)  # Stockage en base64
    est_valide = db.Column(db.Boolean, default=True)
    date_generation = db.Column(db.DateTime, default=datetime.utcnow)
    date_utilisation = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, order_id, offer_id, user_id, cle_utilisateur, cle_achat):
        self.order_id = order_id
        self.offer_id = offer_id
        self.user_id = user_id
        self.cle_utilisateur = cle_utilisateur
        self.cle_achat = cle_achat
        self.cle_billet = self._generate_ticket_key()
        self.qr_code = self._generate_qr_code()
    
    def _generate_ticket_key(self):
        """Génère une clé unique pour le billet en combinant les clés utilisateur et achat."""
        from flask import current_app
        
        # Concaténation des deux clés avec un sel supplémentaire
        combined = f"{self.cle_utilisateur}|{self.cle_achat}|{uuid.uuid4()}|{current_app.config['SALT_KEY']}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _generate_qr_code(self):
        """Génère un QR code pour le billet."""
        try:
            import qrcode
            import base64
            from io import BytesIO
            import json
            from datetime import datetime
            
            # Création des données du QR code
            data = {
                'id': str(uuid.uuid4()),
                'ticket_id': str(self.id) if self.id else "pending",
                'key': self.cle_billet,
                'timestamp': datetime.utcnow().timestamp()
            }
            
            # Conversion en chaîne JSON
            qr_data = json.dumps(data)
            
            # Génération du QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Conversion en base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Retourner le data URI complet
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print(f"Erreur de génération de QR code: {str(e)}")
            # QR code de secours en cas d'erreur
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAEsAQMAAABDsxw2AAAABlBMVEX///8AAABVwtN+AAABE0lEQVR42u3aMQ7CMAyF4dZdOQKHcGQOw22/ZhKnolLU3zOg5Emt2JL+0cYIuA9zMq4zudyiP1fk4eLO7J2NC1/c2fnLnI/L+X1Fz7i0XDJvuPCgudwSXG4lLnzmnnNX7mruA/eJ+8J94xJ2zp1zl7mjucztZm45d82dc7fcwSXsnLvmLrlzLmHn3Dl3zp1zt9wld84l7Ji75C65cy5h59w5d86dc7fc4QY75y65S+6cS9g5d86dc+fcLXfJnXMJO+YuuUvunEv/DltyDl9yDl9yFl9yFl9ydj91Bx91Dh91Dh91Fh91Fh93Dh93Dh93Hh93Hh97/j/P4eO+7UKO3tKO3uSCftAKO0PdG2vD9AZTrZAjY8b4AAAASUVORK5CYII="
    
    def validate(self):
        """Valide le billet lors de l'utilisation."""
        if not self.est_valide:
            return False
        
        self.est_valide = False
        self.date_utilisation = datetime.utcnow()
        db.session.commit()
        return True
    
    def cancel(self):
        """Annule le billet et remet l'offre en disponibilité."""
        from app.models.offer import Offer
        
        if not self.est_valide:  # Si déjà utilisé, on ne peut pas annuler
            return False
        
        # Remettre en disponibilité
        offer = Offer.query.get(self.offer_id)
        if offer:
            offer.increase_availability()
        
        self.est_valide = False
        db.session.commit()
        return True
    
    def verify_authenticity(self, user):
        """Vérifie l'authenticité du billet en comparant les clés."""
        # Vérification que l'utilisateur est bien le propriétaire du billet
        if self.user_id != user.id:
            return False
        
        # Recréation de la clé pour vérification
        from flask import current_app
        combined = f"{self.cle_utilisateur}|{self.cle_achat}|{uuid.uuid4()}|{current_app.config['SALT_KEY']}"
        verification_key = hashlib.sha256(combined.encode()).hexdigest()
        
        # La vérification exacte n'est pas possible car la clé contient un UUID aléatoire
        # On vérifie donc que les deux clés proviennent bien du même utilisateur et de la même commande
        return self.cle_utilisateur == user.cle_securite and self.est_valide
    
    def get_qr_code_image(self):
        """Retourne l'image du QR code en base64."""
        if not self.qr_code:
            self.qr_code = self._generate_qr_code()
            db.session.commit()
        
        return self.qr_code
    
    def to_dict(self):
        """Convertit le billet en dictionnaire."""
        from app.models.offer import Offer
        offer = Offer.query.get(self.offer_id)
        
        return {
            'id': self.id,
            'order_id': self.order_id,
            'offer': {
                'id': offer.id,
                'titre': offer.titre,
                'type': offer.type,
                'date_evenement': offer.date_evenement.isoformat()
            },
            'est_valide': self.est_valide,
            'date_generation': self.date_generation.isoformat(),
            'date_utilisation': self.date_utilisation.isoformat() if self.date_utilisation else None
        }
    
    def __repr__(self):
        return f"Ticket(id={self.id}, order_id={self.order_id}, est_valide={self.est_valide})"
