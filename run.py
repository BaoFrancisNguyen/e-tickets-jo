from app import create_app, db
from app.models.user import User
from app.models.offer import Offer
from app.models.cart import Cart
from app.models.order import Order
from app.models.ticket import Ticket
from app.config import Config
import os

app = create_app(Config)

@app.before_first_request
def create_admin():
    """Crée un utilisateur administrateur s'il n'existe pas déjà."""
    from app import bcrypt
    
    admin_email = app.config['ADMIN_EMAIL']
    admin_username = app.config['ADMIN_USERNAME']
    admin_password = app.config['ADMIN_PASSWORD']
    
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            username=admin_username,
            password=bcrypt.generate_password_hash(admin_password).decode('utf-8'),
            nom='Admin',
            prenom='Admin',
            role='administrateur',
            est_verifie=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Administrateur créé: {admin_email}")

@app.shell_context_processor
def make_shell_context():
    """Configurez le contexte du shell Flask."""
    return {
        'db': db, 
        'User': User, 
        'Offer': Offer, 
        'Cart': Cart, 
        'Order': Order, 
        'Ticket': Ticket
    }



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
