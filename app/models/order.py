from datetime import datetime
import uuid
from app import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    quantite = db.Column(db.Integer, default=1)
    prix_unitaire = db.Column(db.Float, nullable=False)
    
    # Relations
    offer = db.relationship('Offer')
    
    def __init__(self, order_id, offer_id, quantite, prix_unitaire):
        self.order_id = order_id
        self.offer_id = offer_id
        self.quantite = quantite
        self.prix_unitaire = prix_unitaire
    
    def sous_total(self):
        """Calcule le sous-total pour cet élément de la commande."""
        return self.quantite * self.prix_unitaire
    
    def __repr__(self):
        return f"OrderItem(order_id={self.order_id}, offer_id={self.offer_id}, quantite={self.quantite})"

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    total = db.Column(db.Float, nullable=False)
    statut = db.Column(db.String(20), default='en attente')  # 'en attente', 'payée', 'annulée'
    date_commande = db.Column(db.DateTime, default=datetime.utcnow)
    date_paiement = db.Column(db.DateTime, nullable=True)
    cle_achat = db.Column(db.String(255), unique=True, nullable=False)
    adresse_email = db.Column(db.String(120), nullable=False)
    
    # Relations
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    tickets = db.relationship('Ticket', backref='order', lazy=True)
    
    def __init__(self, user_id, total, adresse_email):
        self.user_id = user_id
        self.total = total
        self.reference = self._generate_reference()
        self.cle_achat = self._generate_purchase_key()
        self.adresse_email = adresse_email
    
    def _generate_reference(self):
        """Génère une référence unique pour la commande."""
        date_str = datetime.utcnow().strftime('%Y%m%d')
        random_str = str(uuid.uuid4())[:8]
        return f"JO-{date_str}-{random_str}".upper()
    
    def _generate_purchase_key(self):
        """Génère une clé d'achat unique pour la commande."""
        from flask import current_app
        import hashlib
        
        key_material = f"{uuid.uuid4()}{self.user_id}{datetime.utcnow().timestamp()}{current_app.config['SALT_KEY']}"
        return hashlib.sha256(key_material.encode()).hexdigest()
    
    def add_item(self, offer, quantite, prix_unitaire):
        """Ajoute un élément à la commande."""
        item = OrderItem(
            order_id=self.id,
            offer_id=offer.id if hasattr(offer, 'id') else offer,
            quantite=quantite,
            prix_unitaire=prix_unitaire
        )
        db.session.add(item)
        db.session.commit()
        return item
    
    def set_paid(self):
        """Marque la commande comme payée."""
        self.statut = 'payée'
        self.date_paiement = datetime.utcnow()
        db.session.commit()
        return True
    
    def cancel(self):
        """Annule la commande."""
        if self.statut == 'payée':
            # Remettre les tickets en disponibilité
            from app.models.ticket import Ticket
            for ticket in Ticket.query.filter_by(order_id=self.id).all():
                ticket.cancel()
            
        self.statut = 'annulée'
        db.session.commit()
        return True
    
    def generate_tickets(self, user):
        """Génère les tickets pour cette commande."""
        from app.models.ticket import Ticket
        
        tickets = []
        for item in self.items:
            offer = item.offer
            for _ in range(item.quantite):
                ticket = Ticket(
                    order_id=self.id,
                    offer_id=offer.id,
                    user_id=user.id,
                    cle_utilisateur=user.cle_securite,
                    cle_achat=self.cle_achat
                )
                db.session.add(ticket)
                tickets.append(ticket)
        
        db.session.commit()
        return tickets
    
    def to_dict(self):
        """Convertit la commande en dictionnaire."""
        return {
            'id': self.id,
            'reference': self.reference,
            'total': self.total,
            'statut': self.statut,
            'date_commande': self.date_commande.isoformat(),
            'date_paiement': self.date_paiement.isoformat() if self.date_paiement else None,
            'items': [
                {
                    'id': item.id,
                    'offer_id': item.offer_id,
                    'titre': item.offer.titre,
                    'quantite': item.quantite,
                    'prix_unitaire': item.prix_unitaire,
                    'sous_total': item.sous_total()
                } for item in self.items
            ],
            'tickets': [ticket.id for ticket in self.tickets]
        }
    
    def __repr__(self):
        return f"Order(reference='{self.reference}', statut='{self.statut}', total={self.total}€)"
