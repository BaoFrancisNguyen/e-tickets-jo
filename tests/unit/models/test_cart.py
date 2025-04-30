#------------------------------------------------------
# tests/unit/models/test_cart.py - Tests du modèle Cart
#------------------------------------------------------

import pytest
from app.models.cart import Cart, CartItem

def test_cart_creation(db_session, test_user):
    """Test la création d'un panier."""
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    
    saved_cart = Cart.query.filter_by(user_id=test_user.id).first()
    assert saved_cart is not None
    assert saved_cart.user_id == test_user.id
    assert len(saved_cart.items) == 0

def test_cart_add_item(db_session, test_user, test_offer):
    """Test l'ajout d'un élément au panier."""
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    
    # Ajouter un élément
    assert cart.add_item(test_offer, 1) is True
    
    # Vérifier que l'élément a été ajouté
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    assert len(cart_items) == 1
    assert cart_items[0].offer_id == test_offer.id
    assert cart_items[0].quantite == 1
    assert cart_items[0].prix_unitaire == test_offer.prix
    
    # Ajouter le même élément à nouveau (doit augmenter la quantité)
    assert cart.add_item(test_offer, 2) is True
    
    # Vérifier que la quantité a été mise à jour
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    assert len(cart_items) == 1
    assert cart_items[0].quantite == 3

def test_cart_update_item(db_session, test_user, test_offer):
    """Test la mise à jour d'un élément du panier."""
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    
    # Ajouter un élément
    cart.add_item(test_offer, 2)
    
    # Récupérer l'élément
    cart_item = CartItem.query.filter_by(cart_id=cart.id, offer_id=test_offer.id).first()
    
    # Mettre à jour la quantité
    assert cart.update_item(cart_item.id, 5) is True
    
    # Vérifier que la quantité a été mise à jour
    cart_item = CartItem.query.filter_by(cart_id=cart.id, offer_id=test_offer.id).first()
    assert cart_item.quantite == 5
    
    # Mettre à 0 (doit supprimer l'élément)
    assert cart.update_item(cart_item.id, 0) is True
    
    # Vérifier que l'élément a été supprimé
    cart_item = CartItem.query.filter_by(cart_id=cart.id, offer_id=test_offer.id).first()
    assert cart_item is None

def test_cart_remove_item(db_session, test_user, test_offer):
    """Test la suppression d'un élément du panier."""
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    
    # Ajouter un élément
    cart.add_item(test_offer, 1)
    
    # Récupérer l'élément
    cart_item = CartItem.query.filter_by(cart_id=cart.id, offer_id=test_offer.id).first()
    
    # Supprimer l'élément
    assert cart.remove_item(cart_item.id) is True
    
    # Vérifier que l'élément a été supprimé
    cart_item = CartItem.query.filter_by(cart_id=cart.id, offer_id=test_offer.id).first()
    assert cart_item is None

def test_cart_clear(db_session, test_user, test_offer):
    """Test la suppression de tous les éléments du panier."""
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    
    # Ajouter quelques éléments (au moins deux offres)
    cart.add_item(test_offer, 1)
    
    # Créer une autre offre
    from app.models.offer import Offer
    from datetime import datetime, timedelta
    
    another_offer = Offer(
        titre='Another Offer',
        description='Another Test Description',
        type='duo',
        nombre_personnes=2,
        prix=80.0,
        date_evenement=datetime.utcnow() + timedelta(days=45),
        disponibilite=20,
        est_publie=True
    )
    db_session.add(another_offer)
    db_session.commit()
    
    cart.add_item(another_offer, 3)
    
    # Vérifier que le panier a 2 éléments
    assert len(cart.items) == 2
    
    # Vider le panier
    assert cart.clear() is True
    
    # Vérifier que le panier est vide
    assert len(cart.items) == 0
    assert CartItem.query.filter_by(cart_id=cart.id).count() == 0

def test_cart_total_and_count(db_session, test_user, test_offer):
    """Test le calcul du total et du nombre d'éléments dans le panier."""
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    
    # Panier vide
    assert cart.total() == 0
    assert cart.count_items() == 0
    
    # Ajouter un élément
    cart.add_item(test_offer, 2)  # 2 * 50.0 = 100.0
    
    # Créer une autre offre
    from app.models.offer import Offer
    from datetime import datetime, timedelta
    
    another_offer = Offer(
        titre='Another Offer',
        description='Another Test Description',
        type='duo',
        nombre_personnes=2,
        prix=80.0,
        date_evenement=datetime.utcnow() + timedelta(days=45),
        disponibilite=20,
        est_publie=True
    )
    db_session.add(another_offer)
    db_session.commit()
    
    cart.add_item(another_offer, 1)  # 1 * 80.0 = 80.0
    
    # Vérifier le total et le nombre d'éléments
    assert cart.total() == 180.0  # 100.0 + 80.0
    assert cart.count_items() == 3  # 2 + 1