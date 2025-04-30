import os
import pytest
from app import create_app, db
from app.models.user import User
from app.models.offer import Offer
from app.models.cart import Cart
from app.models.order import Order
from app.models.ticket import Ticket
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """Fixture pour créer une application Flask de test."""
    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key',
        'SALT_KEY': 'test-salt',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'MAIL_SUPPRESS_SEND': True,
        'SERVER_NAME': 'localhost'
    })

    # Créer le contexte d'application
    with app.app_context():
        # Créer les tables
        db.create_all()
        yield app
        # Nettoyer après les tests
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Fixture pour créer un client de test."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture pour créer un runner de commande CLI."""
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    """Fixture pour fournir une session de base de données."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        session = db.session
        session.begin_nested()
        
        yield session
        
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def test_user(app, db_session):
    """Fixture pour créer un utilisateur de test."""
    from app import bcrypt
    
    # Créer un utilisateur
    user = User(
        username='testuser',
        email='test@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        nom='Test',
        prenom='User',
        role='utilisateur',
        est_verifie=True
    )
    db_session.add(user)
    db_session.commit()
    
    return user

@pytest.fixture
def admin_user(app, db_session):
    """Fixture pour créer un administrateur de test."""
    from app import bcrypt
    
    # Créer un administrateur
    user = User(
        username='adminuser',
        email='admin@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        nom='Admin',
        prenom='User',
        role='administrateur',
        est_verifie=True
    )
    db_session.add(user)
    db_session.commit()
    
    return user

@pytest.fixture
def test_offer(app, db_session):
    """Fixture pour créer une offre de test."""
    # Créer une offre
    offer = Offer(
        titre='Test Offer',
        description='Test Description',
        type='solo',
        nombre_personnes=1,
        prix=50.0,
        date_evenement=datetime.utcnow() + timedelta(days=30),
        disponibilite=100,
        est_publie=True
    )
    db_session.add(offer)
    db_session.commit()
    
    return offer

@pytest.fixture
def test_cart(app, db_session, test_user, test_offer):
    """Fixture pour créer un panier de test."""
    # Créer un panier
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    
    # Ajouter l'offre au panier
    cart.add_item(test_offer, 1)
    
    return cart

@pytest.fixture
def test_order(app, db_session, test_user, test_offer):
    """Fixture pour créer une commande de test."""
    # Créer une commande
    order = Order(
        user_id=test_user.id,
        total=test_offer.prix,
        adresse_email=test_user.email
    )
    db_session.add(order)
    db_session.commit()
    
    # Ajouter l'offre à la commande
    order.add_item(test_offer, 1, test_offer.prix)
    
    # Marquer comme payée
    order.set_paid()
    
    # Générer les billets
    order.generate_tickets(test_user)
    
    return order

@pytest.fixture
def auth(client):
    """Fixture pour simuler l'authentification dans les tests."""
    class AuthActions:
        def __init__(self, client):
            self._client = client
        
        def login(self, email='test@example.com', password='password123'):
            return self._client.post(
                '/auth/login',
                data={'email': email, 'password': password}
            )
        
        def logout(self):
            return self._client.get('/auth/logout')
        
        def register(self, username='newuser', email='new@example.com', 
                      password='Password123!', nom='New', prenom='User'):
            return self._client.post(
                '/auth/register',
                data={
                    'username': username,
                    'email': email,
                    'password': password,
                    'confirm_password': password,
                    'nom': nom,
                    'prenom': prenom
                }
            )
    
    return AuthActions(client)

@pytest.fixture
def auth_client(client, auth, test_user):
    """Client avec un utilisateur connecté."""
    auth.login()
    return client

@pytest.fixture
def admin_client(client, auth, admin_user):
    """Client avec un administrateur connecté."""
    auth.login(email='admin@example.com', password='password123')
    return client