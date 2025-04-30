import json
import pytest
from app.services.qrcode_service import (
    generate_qrcode_data, create_qrcode_image, 
    verify_qrcode, scan_ticket
)
from app.models.ticket import Ticket

def test_generate_qrcode_data(app, db_session, test_user, test_offer, test_order):
    """Test la génération des données QR code pour un billet."""
    # Créer un billet
    ticket = Ticket(
        order_id=test_order.id,
        offer_id=test_offer.id,
        user_id=test_user.id,
        cle_utilisateur=test_user.cle_securite,
        cle_achat=test_order.cle_achat
    )
    db_session.add(ticket)
    db_session.commit()
    
    # Générer les données QR code
    qr_data = generate_qrcode_data(ticket)
    
    # Vérifier que c'est un JSON valide
    data = json.loads(qr_data)
    
    # Vérifier que les informations nécessaires sont présentes
    assert 'qr_id' in data
    assert 'ticket_id' in data
    assert str(ticket.id) == data['ticket_id']
    assert 'key' in data
    assert ticket.cle_billet == data['key']
    assert 'offer_id' in data
    assert ticket.offer_id == data['offer_id']
    assert 'user_id' in data
    assert ticket.user_id == data['user_id']
    assert 'generated_at' in data

def test_create_qrcode_image(app):
    """Test la création d'une image QR code à partir de données."""
    data = {"test": "data"}
    json_data = json.dumps(data)
    
    # Créer une image QR code
    qr_image = create_qrcode_image(json_data)
    
    # Vérifier que l'image est au format base64
    assert qr_image.startswith("data:image/png;base64,")

def test_verify_qrcode(app, db_session, test_user, test_offer, test_order):
    """Test la vérification d'un QR code."""
    # Créer un billet
    ticket = Ticket(
        order_id=test_order.id,
        offer_id=test_offer.id,
        user_id=test_user.id,
        cle_utilisateur=test_user.cle_securite,
        cle_achat=test_order.cle_achat
    )
    db_session.add(ticket)
    db_session.commit()
    
    # Générer les données QR code
    qr_data = generate_qrcode_data(ticket)
    
    # Vérifier le QR code
    success, result = verify_qrcode(qr_data)
    
    # Vérifier le résultat
    assert success is True
    assert isinstance(result, Ticket)
    assert result.id == ticket.id

def test_scan_ticket(app, db_session, test_user, test_offer, test_order):
    """Test le scan d'un billet pour validation."""
    # Créer un billet
    ticket = Ticket(
        order_id=test_order.id,
        offer_id=test_offer.id,
        user_id=test_user.id,
        cle_utilisateur=test_user.cle_securite,
        cle_achat=test_order.cle_achat
    )
    db_session.add(ticket)
    db_session.commit()
    
    # Vérifier que le billet est valide
    assert ticket.est_valide is True
    
    # Générer les données QR code
    qr_data = generate_qrcode_data(ticket)
    
    # Scanner le billet
    success, scan_result = scan_ticket(qr_data)
    
    # Vérifier le résultat
    assert success is True
    assert 'ticket_id' in scan_result
    assert int(scan_result['ticket_id']) == ticket.id
    assert 'validated_at' in scan_result
    
    # Recharger le billet de la base
    db_session.refresh(ticket)
    
    # Vérifier qu'il a été marqué comme utilisé
    assert ticket.est_valide is False
    assert ticket.date_utilisation is not None