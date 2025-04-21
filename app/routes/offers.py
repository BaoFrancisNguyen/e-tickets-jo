from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.offer import Offer
from app.models.cart import Cart

offers_bp = Blueprint('offers', __name__, url_prefix='/offers')

@offers_bp.route('/')
def index():
    """
    Affiche toutes les offres disponibles.
    """
    # Récupérer le type d'offre sélectionné (filtre)
    offer_type = request.args.get('type')
    
    # Récupérer les offres en fonction du type sélectionné
    if offer_type and offer_type in ['solo', 'duo', 'familiale']:
        offers = Offer.query.filter_by(est_publie=True, type=offer_type).all()
    else:
        offers = Offer.query.filter_by(est_publie=True).all()
    
    return render_template('offers/index.html', offers=offers, selected_type=offer_type)

@offers_bp.route('/<int:offer_id>')
def detail(offer_id):
    """
    Affiche les détails d'une offre spécifique.
    """
    offer = Offer.query.get_or_404(offer_id)
    
    # Vérifier si l'offre est publiée
    if not offer.est_publie:
        flash('Cette offre n\'est pas disponible.', 'warning')
        return redirect(url_for('offers.index'))
    
    return render_template('offers/detail.html', offer=offer)

@offers_bp.route('/add-to-cart/<int:offer_id>', methods=['POST'])
@login_required
def add_to_cart(offer_id):
    """
    Ajoute une offre au panier de l'utilisateur.
    """
    offer = Offer.query.get_or_404(offer_id)
    
    # Vérifier si l'offre est publiée et disponible
    if not offer.est_publie or not offer.is_available():
        flash('Cette offre n\'est pas disponible.', 'warning')
        return redirect(url_for('offers.detail', offer_id=offer_id))
    
    # Récupérer la quantité souhaitée
    quantity = int(request.form.get('quantity', 1))
    
    # Vérifier que la quantité est valide
    if quantity <= 0:
        flash('La quantité doit être positive.', 'danger')
        return redirect(url_for('offers.detail', offer_id=offer_id))
    
    # Vérifier la disponibilité
    if offer.disponibilite < quantity:
        flash(f'Il ne reste que {offer.disponibilite} billets disponibles pour cette offre.', 'warning')
        return redirect(url_for('offers.detail', offer_id=offer_id))
    
    # Récupérer le panier de l'utilisateur ou en créer un
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    # Ajouter l'offre au panier
    if cart.add_item(offer, quantity):
        flash(f'{quantity} billet(s) ajouté(s) au panier.', 'success')
    else:
        flash('Erreur lors de l\'ajout au panier.', 'danger')
    
    return redirect(url_for('cart.index'))

@offers_bp.route('/api/offers')
def api_offers():
    """
    API pour récupérer les offres (utilisé pour le filtrage dynamique).
    """
    # Récupérer le type d'offre sélectionné (filtre)
    offer_type = request.args.get('type')
    
    # Récupérer les offres en fonction du type sélectionné
    if offer_type and offer_type in ['solo', 'duo', 'familiale']:
        offers = Offer.query.filter_by(est_publie=True, type=offer_type).all()
    else:
        offers = Offer.query.filter_by(est_publie=True).all()
    
    # Convertir les offres en dictionnaires
    offers_data = [offer.to_dict() for offer in offers]
    
    return jsonify(offers_data)
