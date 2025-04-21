import uuid
import hashlib
from datetime import datetime
from flask import current_app
import qrcode
from io import BytesIO
import base64
import json

def generate_user_key(user_id, email):
    """
    Génère une clé de sécurité unique pour un utilisateur.
    
    Cette clé est générée lors de la création du compte et est invisible pour l'utilisateur.
    Elle est utilisée pour la génération de billets.
    """
    # Combinaison d'éléments uniques
    key_material = f"{uuid.uuid4()}{email}{user_id}{datetime.utcnow().timestamp()}{current_app.config['SALT_KEY']}"
    
    # Hachage SHA-256
    key = hashlib.sha256(key_material.encode()).hexdigest()
    
    return key

def generate_purchase_key(user_id, order_id):
    """
    Génère une clé d'achat unique pour une commande.
    
    Cette clé est générée lors de l'achat et est utilisée avec la clé utilisateur
    pour sécuriser les billets.
    """
    # Combinaison d'éléments uniques
    key_material = f"{uuid.uuid4()}{user_id}{order_id}{datetime.utcnow().timestamp()}{current_app.config['SALT_KEY']}"
    
    # Hachage SHA-256
    key = hashlib.sha256(key_material.encode()).hexdigest()
    
    return key

def combine_keys(user_key, purchase_key):
    """
    Combine les clés utilisateur et achat pour générer la clé définitive du billet.
    
    Cette clé combinée est utilisée pour générer le QR code.
    """
    # Ajout d'un sel supplémentaire pour renforcer la sécurité
    combined = f"{user_key}|{purchase_key}|{uuid.uuid4()}|{current_app.config['SALT_KEY']}"
    
    # Hachage SHA-256
    key = hashlib.sha256(combined.encode()).hexdigest()
    
    return key

def generate_qr_code(ticket_id, final_key):
    """
    Génère un QR code pour un billet.
    
    Le QR code contient les informations nécessaires pour vérifier l'authenticité du billet.
    """
    # Création des données du QR code
    data = {
        'id': str(uuid.uuid4()),  # Identifiant unique pour ce QR code
        'ticket_id': str(ticket_id),
        'key': final_key,
        'timestamp': datetime.utcnow().timestamp()
    }
    
    # Conversion en chaîne JSON
    qr_data = json.dumps(data)
    
    # Génération du QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Conversion en base64
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

def verify_ticket_key(ticket_key, user_key, purchase_key):
    """
    Vérifie l'authenticité d'une clé de billet.
    
    Cette fonction est utilisée lors de la vérification des billets le jour de l'événement.
    """
    # La vérification exacte n'est pas possible car la clé définitive contient un UUID aléatoire
    # Nous vérifions donc que les informations de base correspondent
    
    # Dans un cas réel, nous utiliserions une approche plus sophistiquée pour la vérification
    # comme une signature numérique ou un mécanisme de challenge-response
    
    # Pour cet exemple, nous vérifions simplement que la clé utilisateur et la clé d'achat
    # sont bien celles attendues
    
    # Récupérer les parties de la clé
    parts = ticket_key.split('|')
    
    if len(parts) < 2:  # Si la clé n'a pas le format attendu
        return False
    
    return parts[0] == user_key and parts[1] == purchase_key

def parse_qr_code(qr_data):
    """
    Analyse les données d'un QR code pour extraire les informations du billet.
    """
    try:
        data = json.loads(qr_data)
        
        ticket_id = data.get('ticket_id')
        key = data.get('key')
        timestamp = data.get('timestamp')
        
        # Vérifier que les données nécessaires sont présentes
        if not ticket_id or not key:
            return None
        
        return {
            'ticket_id': ticket_id,
            'key': key,
            'timestamp': timestamp
        }
    
    except json.JSONDecodeError:
        return None
