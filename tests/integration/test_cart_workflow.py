#------------------------------------------------------
# tests/integration/test_cart_workflow.py - Tests du workflow de panier
#------------------------------------------------------

import json
from app import db

def test_add_to_cart_workflow(client, test_user, test_offer, auth, app):
    """Test adding an item to cart."""
    # First login
    auth.login()
    
    # Add item to cart
    response = client.post(
        f'/offers/add-to-cart/{test_offer.id}',
        data={'quantity': 1},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b'Votre panier' in response.data
    assert b'Test Offer' in response.data  # The offer title should be in the cart
    
    # Verify the item was added to the database
    with app.app_context():
        from app.models.cart import Cart, CartItem
        
        cart = Cart.query.filter_by(user_id=test_user.id).first()
        
        assert cart is not None
        assert cart.items is not None
        assert len(cart.items) == 1
        
        # Verify item details
        item = cart.items[0]
        assert item.offer_id == test_offer.id
        assert item.quantite == 1

def test_checkout_workflow(client, test_user, test_offer, auth, app, db_session):
    """Test the checkout process."""
    # First login
    auth.login()
    
    # Add item to cart
    with app.app_context():
        from app.models.cart import Cart
        
        # Ensure cart exists and is empty
        cart = Cart.query.filter_by(user_id=test_user.id).first()
        if cart:
            cart.clear()
        else:
            cart = Cart(user_id=test_user.id)
            db.session.add(cart)
            db.session.commit()
        
        # Add item to cart
        cart.add_item(test_offer, 1)
    
    # Go directly to creating an order instead of checkout
    response = client.post(
        '/orders/create',
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify that the order is created and cart is cleared
    with app.app_context():
        from app.models.order import Order
        from app.models.cart import Cart
        
        # Check cart is empty
        cart = Cart.query.filter_by(user_id=test_user.id).first()
        assert len(cart.items) == 0
        
        # Check order was created
        order = Order.query.filter_by(user_id=test_user.id).order_by(Order.id.desc()).first()
        assert order is not None
        assert order.user_id == test_user.id
        assert order.total == test_offer.prix