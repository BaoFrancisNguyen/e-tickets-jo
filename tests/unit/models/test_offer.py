#------------------------------------------------------
# tests/unit/models/test_offer.py - Tests du modèle Offer
#------------------------------------------------------

import pytest
from app.models.offer import Offer
from datetime import datetime, timedelta

def test_offer_creation(db_session):
    """Test la création d'une offre."""
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
    
    saved_offer = Offer.query.filter_by(titre='Test Offer').first()
    assert saved_offer is not None
    assert saved_offer.description == 'Test Description'
    assert saved_offer.prix == 50.0
    assert saved_offer.disponibilite == 100

def test_offer_availability(db_session):
    """Test les méthodes de disponibilité d'une offre."""
    # Offre disponible
    future_offer = Offer(
        titre='Future Offer',
        description='Available offer',
        type='solo',
        nombre_personnes=1,
        prix=50.0,
        date_evenement=datetime.utcnow() + timedelta(days=30),
        disponibilite=10,
        est_publie=True
    )
    
    # Offre dans le passé
    past_offer = Offer(
        titre='Past Offer',
        description='Unavailable offer',
        type='solo',
        nombre_personnes=1,
        prix=50.0,
        date_evenement=datetime.utcnow() - timedelta(days=1),
        disponibilite=10,
        est_publie=True
    )
    
    # Offre non publiée
    unpublished_offer = Offer(
        titre='Unpublished Offer',
        description='Unpublished offer',
        type='solo',
        nombre_personnes=1,
        prix=50.0,
        date_evenement=datetime.utcnow() + timedelta(days=30),
        disponibilite=10,
        est_publie=False
    )
    
    db_session.add_all([future_offer, past_offer, unpublished_offer])
    db_session.commit()
    
    # Vérifier la disponibilité
    assert future_offer.is_available() is True
    assert past_offer.is_available() is False
    assert unpublished_offer.is_available() is False

def test_offer_decrease_availability(db_session):
    """Test la diminution de la disponibilité d'une offre."""
    offer = Offer(
        titre='Decrease Test',
        description='Test',
        type='solo',
        nombre_personnes=1,
        prix=50.0,
        date_evenement=datetime.utcnow() + timedelta(days=30),
        disponibilite=5,
        est_publie=True
    )
    db_session.add(offer)
    db_session.commit()
    
    # Diminuer de 2
    assert offer.decrease_availability(2) is True
    assert offer.disponibilite == 3
    
    # Diminuer de 3
    assert offer.decrease_availability(3) is True
    assert offer.disponibilite == 0
    
    # Diminuer de 1 quand disponibilité = 0
    assert offer.decrease_availability(1) is False
    assert offer.disponibilite == 0

def test_offer_to_dict(db_session):
    """Test la conversion d'une offre en dictionnaire."""
    event_date = datetime.utcnow() + timedelta(days=30)
    offer = Offer(
        titre='Dict Test',
        description='Test Description',
        type='duo',
        nombre_personnes=2,
        prix=100.0,
        date_evenement=event_date,
        disponibilite=50,
        est_publie=True,
        image='test-image.jpg'
    )
    db_session.add(offer)
    db_session.commit()
    
    offer_dict = offer.to_dict()
    
    assert offer_dict['id'] == offer.id
    assert offer_dict['titre'] == 'Dict Test'
    assert offer_dict['type'] == 'duo'
    assert offer_dict['nombre_personnes'] == 2
    assert offer_dict['prix'] == 100.0
    assert offer_dict['disponibilite'] == 50
    assert offer_dict['est_publie'] is True
    assert offer_dict['image'] == 'test-image.jpg'
    # Vérifier que la date est correctement formatée
    assert offer_dict['date_evenement'] == event_date.isoformat()