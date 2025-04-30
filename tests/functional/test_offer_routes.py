#------------------------------------------------------
# tests/functional/test_offer_routes.py - Tests des routes d'offres
#------------------------------------------------------

import pytest

def test_offers_index(client):
    """Test that the offers index page loads correctly."""
    response = client.get('/offers/')
    assert response.status_code == 200
    assert b'Nos offres' in response.data

def test_offer_detail(client, test_offer, app):
    """Test that an offer detail page loads correctly."""
    # S'assurer que l'offre a une description
    with app.app_context():
        from app import db
        test_offer.description = 'Test Description'
        db.session.commit()
    
    response = client.get(f'/offers/{test_offer.id}')
    assert response.status_code == 200
    assert b'Test Offer' in response.data
    assert b'Test Description' in response.data

def test_offer_add_to_cart(client, auth, test_user, test_offer):
    """Test adding an offer to cart."""
    # Login first
    auth.login()
    
    # Add offer to cart
    response = client.post(f'/offers/add-to-cart/{test_offer.id}', 
                           data={'quantity': '1'},
                           follow_redirects=True)
    
    assert response.status_code == 200
    assert b'billet(s) ajout' in response.data  # Message confirmation 
    assert b'Votre panier' in response.data  # Redirect to cart page