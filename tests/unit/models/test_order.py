#------------------------------------------------------
# tests/unit/models/test_order.py - Tests du modèle Order
#------------------------------------------------------

import pytest
from app.models.order import Order, OrderItem
from datetime import datetime

def test_order_creation(db_session, test_user):
    """Test la création d'une commande."""
    order = Order(
        user_id=test_user.id,
        total=150.0,
        adresse_email=test_user.email
    )
    db_session.add(order)
    db_session.commit()
    
    saved_order = Order.query.filter_by(user_id=test_user.id).first()
    assert saved_order is not None
    assert saved_order.total == 150.0
    assert saved_order.statut == 'en attente'
    assert saved_order.reference is not None
    assert saved_order.cle_achat is not None
    assert saved_order.adresse_email == test_user.email

def test_order_add_item(db_session, test_user, test_offer):
    """Test l'ajout d'un élément à une commande."""
    order = Order(
        user_id=test_user.id,
        total=0.0,  # Mise à jour plus tard
        adresse_email=test_user.email
    )
    db_session.add(order)
    db_session.commit()
    
    # Ajouter un élément
    item = order.add_item(test_offer, 2, test_offer.prix)
    assert item is not None
    assert item.order_id == order.id
    assert item.offer_id == test_offer.id
    assert item.quantite == 2
    assert item.prix_unitaire == test_offer.prix
    
    # Vérifier que l'élément est bien dans la commande
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    assert len(order_items) == 1
    assert order_items[0].id == item.id

def test_order_set_paid(db_session, test_user):
    """Test le passage d'une commande à l'état 'payée'."""
    order = Order(
        user_id=test_user.id,
        total=100.0,
        adresse_email=test_user.email
    )
    db_session.add(order)
    db_session.commit()
    
    # Vérifier l'état initial
    assert order.statut == 'en attente'
    assert order.date_paiement is None
    
    # Passer à l'état payée
    assert order.set_paid() is True
    assert order.statut == 'payée'
    assert order.date_paiement is not None
    
    # Vérifier en base de données
    saved_order = Order.query.get(order.id)
    assert saved_order.statut == 'payée'
    assert saved_order.date_paiement is not None

def test_order_cancel(db_session, test_user, test_offer):
    """Test l'annulation d'une commande."""
    # Créer une commande
    order = Order(
        user_id=test_user.id,
        total=50.0,
        adresse_email=test_user.email
    )
    db_session.add(order)
    db_session.commit()
    
    # Ajouter un élément
    order.add_item(test_offer, 1, test_offer.prix)
    
    # Vérifier l'état initial
    assert order.statut == 'en attente'
    
    # Annuler la commande
    assert order.cancel() is True
    assert order.statut == 'annulée'
    
    # Vérifier en base de données
    saved_order = Order.query.get(order.id)
    assert saved_order.statut == 'annulée'

def test_order_generate_tickets(db_session, test_user, test_offer):
    """Test la génération de billets pour une commande."""
    # Créer une commande
    order = Order(
        user_id=test_user.id,
        total=50.0,
        adresse_email=test_user.email
    )
    db_session.add(order)
    db_session.commit()
    
    # Ajouter un élément
    order.add_item(test_offer, 2, test_offer.prix)
    
    # Passer la commande à l'état payée
    order.set_paid()
    
    # Générer les billets
    tickets = order.generate_tickets(test_user)
    
    # Vérifier les billets
    assert len(tickets) == 2
    for ticket in tickets:
        assert ticket.order_id == order.id
        assert ticket.offer_id == test_offer.id
        assert ticket.user_id == test_user.id
        assert ticket.est_valide is True
        assert ticket.cle_utilisateur == test_user.cle_securite
        assert ticket.cle_achat == order.cle_achat
        assert ticket.cle_billet is not None
        assert ticket.qr_code is not None