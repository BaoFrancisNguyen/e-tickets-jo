import qrcode
import json
import uuid
from io import BytesIO
import base64
from datetime import datetime
from app.models.ticket import Ticket
from app import db

def generate_qrcode_data(ticket):
    """
    Génère les données à encoder dans le QR code.
    
    Ces données incluent l'identifiant du billet, sa clé unique, et d'autres informations
    nécessaires pour vérifier l'authenticité du billet.
    """
    data = {
        'qr_id': str(uuid.uuid4()),  # Identifiant unique pour ce QR code
        'ticket_id': str(ticket.id),
        'key': ticket.cle_billet,
        'offer_id': ticket.offer_id,
        'user_id': ticket.user_id,
        'generated_at': datetime.utcnow().isoformat()
    }
    
    return json.dumps(data)

def create_qrcode_image(data, box_size=10, border=4):
    """
    Crée une image QR code à partir des données fournies.
    
    Retourne l'image en format base64 pour l'affichage dans un navigateur.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Haute correction d'erreur
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Conversion en base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # Assurez-vous d'ajouter le préfixe data:image/png;base64,
    return f"data:image/png;base64,{img_str}"

def generate_ticket_qrcode(ticket_id):
    """
    Génère un QR code pour un billet spécifique.
    
    Cette fonction est appelée après la création du billet pour générer et stocker
    le QR code associé.
    """
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return None
    
    # Générer les données pour le QR code
    qr_data = generate_qrcode_data(ticket)
    
    # Créer l'image QR code
    qr_image = create_qrcode_image(qr_data)
    
    # Mettre à jour le billet avec le QR code
    ticket.qr_code = qr_image
    db.session.commit()
    
    return qr_image

def verify_qrcode(qr_data):
    """
    Vérifie l'authenticité d'un QR code.
    
    Cette fonction est utilisée lors de la vérification des billets le jour de l'événement.
    """
    try:
        # Décoder les données JSON
        data = json.loads(qr_data)
        
        # Extraire les informations du billet
        ticket_id = data.get('ticket_id')
        key = data.get('key')
        
        if not ticket_id or not key:
            return False, "QR code invalide"
        
        # Récupérer le billet
        ticket = Ticket.query.get(int(ticket_id))
        
        if not ticket:
            return False, "Billet introuvable"
        
        # Vérifier que le billet est valide
        if not ticket.est_valide:
            return False, "Billet déjà utilisé ou annulé"
        
        # Vérifier que la clé correspond
        if ticket.cle_billet != key:
            return False, "Clé de billet invalide"
        
        return True, ticket
    
    except json.JSONDecodeError:
        return False, "Format de QR code invalide"
    except Exception as e:
        return False, f"Erreur lors de la vérification: {str(e)}"

def scan_ticket(qr_data):
    """
    Scanne un billet à partir des données d'un QR code.
    
    Cette fonction est utilisée pour valider un billet lors de l'entrée à l'événement.
    """
    success, result = verify_qrcode(qr_data)
    
    if not success:
        return False, result
    
    ticket = result
    
    # Valider le billet
    if ticket.validate():
        return True, {
            'ticket_id': ticket.id,
            'offer': ticket.offer.titre,
            'user': f"{ticket.user.prenom} {ticket.user.nom}",
            'validated_at': datetime.utcnow().isoformat()
        }
    else:
        return False, "Échec de la validation du billet"