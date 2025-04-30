#------------------------------------------------------
# tests/integration/test_ticket_validation.py - Tests de validation des billets
#------------------------------------------------------

import json
from datetime import datetime

def test_ticket_generation_and_validation_workflow(app, db_session, test_user, test_offer):
    """Test the complete workflow from ticket generation to validation."""
    with app.app_context():
        from app.models.order import Order
        from app.models.ticket import Ticket
        from app.services.qrcode_service import verify_qrcode, scan_ticket

        # Create an order
        order = Order(
            user_id=test_user.id,
            total=test_offer.prix,
            adresse_email=test_user.email
        )
        db_session.add(order)
        db_session.commit()

        # Add item to order
        order.add_item(test_offer, 1, test_offer.prix)

        # Set as paid
        order.set_paid()

        # Generate tickets
        tickets = order.generate_tickets(test_user)
        assert len(tickets) == 1

        ticket = tickets[0]
        assert ticket.est_valide is True
        assert ticket.qr_code is not None

        # Extract QR code data
        # In a real application, this would be scanned from the QR code image
        # Here we simulate by creating the QR data manually
        qr_data = json.dumps({
            'ticket_id': str(ticket.id),
            'key': ticket.cle_billet,
            'timestamp': datetime.utcnow().timestamp()
        })

        # Verify the QR code
        success, result = verify_qrcode(qr_data)
        assert success is True
        assert result.id == ticket.id

        # Scan and validate the ticket
        success, scan_result = scan_ticket(qr_data)
        assert success is True
        assert 'ticket_id' in scan_result
        
        # Verify ticket is now used
        db_session.refresh(ticket)
        assert ticket.est_valide is False
        assert ticket.date_utilisation is not None