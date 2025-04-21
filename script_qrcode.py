# Script à exécuter une fois pour mettre à jour les QR codes existants
from app import create_app, db
from app.models.ticket import Ticket
from app.services.qrcode_service import generate_ticket_qrcode
from app.config import Config

app = create_app(Config)

with app.app_context():
    tickets = Ticket.query.all()
    for ticket in tickets:
        new_qr_code = generate_ticket_qrcode(ticket.id)
        print(f"QR code régénéré pour le billet #{ticket.id}")
    
    db.session.commit()
    print("Tous les QR codes ont été mis à jour")