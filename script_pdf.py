# Script de débogage pour tester la génération de PDF
from app import create_app, db
from app.models.ticket import Ticket
from app.config import Config
import io
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64

app = create_app(Config)

with app.app_context():
    # Récupérer un billet
    ticket_id = 1  # Remplacer par un ID de billet existant
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        print(f"Billet #{ticket_id} non trouvé")
        exit()
    
    print(f"Billet trouvé: #{ticket.id} - {ticket.offer.titre}")
    
    # Vérifier le QR code
    print(f"QR code présent: {'Oui' if ticket.qr_code else 'Non'}")
    if ticket.qr_code:
        print(f"Début du QR code: {ticket.qr_code[:50]}...")
    
    try:
        # Création d'une image pour le billet
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Ajouter les informations du billet
        draw.text((50, 50), f"JO 2024 - Billet #{ticket.id}", fill='black')
        draw.text((50, 100), f"Offre: {ticket.offer.titre}", fill='black')
        draw.text((50, 150), f"Type: {ticket.offer.type}", fill='black')
        draw.text((50, 200), f"Date: {ticket.offer.date_evenement.strftime('%d/%m/%Y %H:%M')}", fill='black')
        
        # Ajouter le QR code si présent
        if ticket.qr_code and ticket.qr_code.startswith('data:image'):
            try:
                # Extraire la partie base64
                qr_data = ticket.qr_code.split(',')[1]
                # Décoder et créer une image
                qr_image = Image.open(io.BytesIO(base64.b64decode(qr_data)))
                # Redimensionner le QR code
                qr_image = qr_image.resize((200, 200))
                # Coller le QR code sur l'image
                image.paste(qr_image, (550, 50))
                print("QR code ajouté avec succès")
            except Exception as e:
                print(f"Erreur lors du traitement du QR code: {str(e)}")
        
        # Convertir l'image en PDF
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        
        # Convertir l'image
        image_buffer = io.BytesIO()
        image.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        
        # Ajouter l'image au PDF
        pdf.drawImage(image_buffer, 50, 400, width=500, height=250)
        
        # Ajouter des informations supplémentaires
        pdf.drawString(50, 350, f"Titulaire: Test User")
        pdf.drawString(50, 330, f"Email: test@example.com")
        pdf.drawString(50, 310, f"Référence: {ticket.order.reference}")
        
        pdf.save()
        buffer.seek(0)
        
        print("PDF généré avec succès")
        
        # Sauvegarder le PDF pour vérification
        with open(f"ticket_{ticket.id}.pdf", "wb") as f:
            f.write(buffer.getvalue())
        
        print(f"PDF sauvegardé dans ticket_{ticket.id}.pdf")
        
    except Exception as e:
        print(f"Erreur lors de la génération du PDF: {str(e)}")