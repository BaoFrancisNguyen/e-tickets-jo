import uuid
import random
from datetime import datetime
from flask import current_app
from app import db
from app.models.order import Order

class PaymentResult:
    """Classe pour représenter le résultat d'un paiement."""
    
    def __init__(self, success, transaction_id=None, message=None, error_code=None):
        self.success = success
        self.transaction_id = transaction_id
        self.message = message
        self.error_code = error_code
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            'success': self.success,
            'transaction_id': self.transaction_id,
            'message': self.message,
            'error_code': self.error_code,
            'timestamp': self.timestamp.isoformat()
        }

def process_payment(order_id, card_number, expiry_month, expiry_year, cvv, amount):
    """
    Traite un paiement (simulation).
    
    Cette fonction simule le traitement d'un paiement par carte de crédit.
    Dans un environnement de production, cette fonction ferait appel à un service de paiement réel.
    """
    # Récupérer la commande
    order = Order.query.get(order_id)
    
    if not order:
        return PaymentResult(False, message="Commande introuvable", error_code="ORDER_NOT_FOUND")
    
    # Vérifier le montant
    if order.total != amount:
        return PaymentResult(False, message="Montant incorrect", error_code="INVALID_AMOUNT")
    
    # Vérifications basiques des informations de carte
    if not _validate_card(card_number, expiry_month, expiry_year, cvv):
        return PaymentResult(False, message="Informations de carte invalides", error_code="INVALID_CARD")
    
    # Simuler un taux de réussite de 90%
    if random.random() < 0.9:
        # Paiement réussi
        transaction_id = str(uuid.uuid4())
        
        # Mettre à jour le statut de la commande
        order.set_paid()
        
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            message="Paiement traité avec succès"
        )
    else:
        # Paiement échoué
        error_codes = ["INSUFFICIENT_FUNDS", "CARD_DECLINED", "NETWORK_ERROR"]
        error_code = random.choice(error_codes)
        
        error_messages = {
            "INSUFFICIENT_FUNDS": "Fonds insuffisants",
            "CARD_DECLINED": "Carte refusée par l'émetteur",
            "NETWORK_ERROR": "Erreur réseau lors du traitement du paiement"
        }
        
        return PaymentResult(
            success=False,
            message=error_messages[error_code],
            error_code=error_code
        )

def _validate_card(card_number, expiry_month, expiry_year, cvv):
    """
    Valide les informations de carte de crédit (vérifications basiques).
    
    Cette fonction effectue des vérifications basiques sur les informations de carte.
    Dans un environnement de production, cette validation serait plus robuste.
    """
    # Vérifier que le numéro de carte contient entre 13 et 19 chiffres
    if not card_number or not card_number.isdigit() or not (13 <= len(card_number) <= 19):
        return False
    
    # Vérifier que le mois d'expiration est entre 1 et 12
    try:
        month = int(expiry_month)
        if not (1 <= month <= 12):
            return False
    except ValueError:
        return False
    
    # Vérifier que l'année d'expiration est valide
    try:
        year = int(expiry_year)
        current_year = datetime.utcnow().year
        if year < current_year or year > current_year + 20:
            return False
    except ValueError:
        return False
    
    # Vérifier que la date d'expiration n'est pas passée
    current_month = datetime.utcnow().month
    if year == current_year and month < current_month:
        return False
    
    # Vérifier que le CVV contient 3 ou 4 chiffres
    if not cvv or not cvv.isdigit() or not (3 <= len(cvv) <= 4):
        return False
    
    # Algorithme de Luhn pour valider le numéro de carte (détection des erreurs de saisie)
    digits = [int(d) for d in card_number]
    checksum = 0
    
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:  # Positions paires (en partant de la droite)
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    
    return checksum % 10 == 0

def refund_payment(transaction_id, amount=None):
    """
    Rembourse un paiement (simulation).
    
    Cette fonction simule le remboursement d'un paiement.
    Dans un environnement de production, cette fonction ferait appel à un service de paiement réel.
    """
    # Simuler un taux de réussite de 95%
    if random.random() < 0.95:
        # Remboursement réussi
        refund_id = str(uuid.uuid4())
        
        return PaymentResult(
            success=True,
            transaction_id=refund_id,
            message="Remboursement traité avec succès"
        )
    else:
        # Remboursement échoué
        error_codes = ["REFUND_FAILED", "TRANSACTION_NOT_FOUND", "NETWORK_ERROR"]
        error_code = random.choice(error_codes)
        
        error_messages = {
            "REFUND_FAILED": "Échec du remboursement",
            "TRANSACTION_NOT_FOUND": "Transaction introuvable",
            "NETWORK_ERROR": "Erreur réseau lors du traitement du remboursement"
        }
        
        return PaymentResult(
            success=False,
            message=error_messages[error_code],
            error_code=error_code
        )
