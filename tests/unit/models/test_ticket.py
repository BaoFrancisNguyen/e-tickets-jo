#------------------------------------------------------
# tests/unit/models/test_ticket.py - Tests du modèle Ticket
#------------------------------------------------------

import pytest
from app.models.ticket import Ticket
from datetime import datetime

def test_ticket_creation(db_session, test_user, test_offer, test_order):
    """Test basic ticket creation."""
    ticket = Ticket(
        order_id=test_order.id,
        offer_id=test_offer.id,
        user_id=test_user.id,
        cle_utilisateur=test_user.cle_securite,
        cle_achat=test_order.cle_achat
    )
    
    db_session.add(ticket)
    db_session.commit()
    
    # Verify ticket was created and has proper attributes
    saved_ticket = Ticket.query.filter_by(order_id=test_order.id).first()
    assert saved_ticket is not None
    assert saved_ticket.est_valide is True
    assert saved_ticket.cle_billet is not None
    assert saved_ticket.qr_code is not None

def test_ticket_validation(db_session, test_user, test_offer, test_order):
    """Test ticket validation process."""
    ticket = Ticket(
        order_id=test_order.id,
        offer_id=test_offer.id,
        user_id=test_user.id,
        cle_utilisateur=test_user.cle_securite,
        cle_achat=test_order.cle_achat
    )
    
    db_session.add(ticket)
    db_session.commit()
    
    # Ticket should be valid initially
    assert ticket.est_valide is True
    assert ticket.date_utilisation is None
    
    # Validate the ticket
    result = ticket.validate()
    assert result is True
    
    # Check ticket state after validation
    assert ticket.est_valide is False
    assert ticket.date_utilisation is not None
    
    # Attempting to validate again should fail
    result = ticket.validate()
    assert result is False