from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from app import db
from app.models.order import Order, OrderItem
from app.models.cart import Cart
from app.models.ticket import Ticket
from app.services.payment_service import process_payment
from datetime import datetime

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/')
@login_required
def index():
    """
    Affiche les commandes de l'utilisateur.
    """
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_commande.desc()).all()
    return render_template('orders/index.html', orders=orders)

@orders_bp.route('/<int:order_id>')
@login_required
def detail(order_id):
    """
    Affiche les détails d'une commande spécifique.
    """
    order = Order.query.get_or_404(order_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire de la commande
    if order.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à accéder à cette commande.', 'danger')
        return redirect(url_for('orders.index'))
    
    return render_template('orders/detail.html', order=order)

@orders_bp.route('/create', methods=['POST'])
@login_required
def create():
    """
    Crée une nouvelle commande à partir du panier de l'utilisateur.
    """
    # Récupérer le panier de l'utilisateur
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart or not cart.items:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('cart.index'))
    
    # Vérifier la disponibilité des articles
    for item in cart.items:
        if not item.offer.is_available() or item.offer.disponibilite < item.quantite:
            flash(f'L\'offre "{item.offer.titre}" n\'est plus disponible en quantité suffisante.', 'danger')
            return redirect(url_for('cart.index'))
    
    # Créer la commande
    order = Order(
        user_id=current_user.id,
        total=cart.total(),
        adresse_email=current_user.email
    )
    
    db.session.add(order)
    db.session.commit()
    
    # Ajouter les articles à la commande
    for item in cart.items:
        order.add_item(item.offer, item.quantite, item.prix_unitaire)
        
        # Réduire la disponibilité de l'offre
        item.offer.decrease_availability(item.quantite)
    
    # Vider le panier
    cart.clear()
    
    # Rediriger vers le paiement direct au lieu de la page de paiement problématique
    return redirect(url_for('orders.direct_payment', order_id=order.id))

@orders_bp.route('/direct_payment/<int:order_id>')
@login_required
def direct_payment(order_id):
    """
    Traite directement le paiement sans passer par le formulaire.
    """
    order = Order.query.get_or_404(order_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire de la commande
    if order.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à accéder à cette commande.', 'danger')
        return redirect(url_for('orders.index'))
    
    # Vérifier que la commande n'est pas déjà payée
    if order.statut == 'payée':
        flash('Cette commande a déjà été payée.', 'info')
        return redirect(url_for('orders.confirmation', order_id=order.id))
    
    # Vérifier que la commande n'est pas annulée
    if order.statut == 'annulée':
        flash('Cette commande a été annulée.', 'warning')
        return redirect(url_for('orders.index'))
    
    # Simuler un paiement réussi
    order.set_paid()
    tickets = order.generate_tickets(current_user)
    
    flash('Paiement effectué avec succès (mode de test).', 'success')
    return redirect(url_for('orders.confirmation', order_id=order.id))

@orders_bp.route('/<int:order_id>/payment', methods=['GET', 'POST'])
@login_required
def payment(order_id):
    """
    Affiche et traite la page de paiement pour une commande.
    """
    order = Order.query.get_or_404(order_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire de la commande
    if order.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à accéder à cette commande.', 'danger')
        return redirect(url_for('orders.index'))
    
    # Vérifier que la commande n'est pas déjà payée
    if order.statut == 'payée':
        flash('Cette commande a déjà été payée.', 'info')
        return redirect(url_for('orders.confirmation', order_id=order.id))
    
    # Vérifier que la commande n'est pas annulée
    if order.statut == 'annulée':
        flash('Cette commande a été annulée.', 'warning')
        return redirect(url_for('orders.index'))
    
    if request.method == 'POST':
        # Récupérer les informations de paiement
        card_number = request.form.get('card_number')
        expiry_month = request.form.get('expiry_month')
        expiry_year = request.form.get('expiry_year')
        cvv = request.form.get('cvv')
        
        # Traiter le paiement
        payment_result = process_payment(
            order_id=order.id,
            card_number=card_number,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            cvv=cvv,
            amount=order.total
        )
        
        if payment_result.success:
            # Mettre à jour le statut de la commande
            order.set_paid()
            
            # Générer les billets
            tickets = order.generate_tickets(current_user)
            
            flash('Paiement effectué avec succès.', 'success')
            return redirect(url_for('orders.confirmation', order_id=order.id))
        else:
            flash(f'Erreur lors du paiement : {payment_result.message}', 'danger')
    
    # Pour GET request ou après un échec de paiement
    return render_template('orders/payment.html', order=order)

@orders_bp.route('/<int:order_id>/confirmation')
@login_required
def confirmation(order_id):
    """
    Affiche la page de confirmation après un paiement réussi.
    """
    order = Order.query.get_or_404(order_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire de la commande
    if order.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à accéder à cette commande.', 'danger')
        return redirect(url_for('orders.index'))
    
    # Vérifier que la commande est bien payée
    if order.statut != 'payée':
        flash('Cette commande n\'a pas encore été payée.', 'warning')
        return redirect(url_for('orders.payment', order_id=order.id))
    
    return render_template('orders/confirmation.html', order=order)

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel(order_id):
    """
    Annule une commande.
    """
    order = Order.query.get_or_404(order_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire de la commande
    if order.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à accéder à cette commande.', 'danger')
        return redirect(url_for('orders.index'))
    
    # Vérifier que la commande peut être annulée
    if order.statut == 'annulée':
        flash('Cette commande a déjà été annulée.', 'info')
        return redirect(url_for('orders.index'))
    
    # Annuler la commande
    if order.cancel():
        flash('Commande annulée avec succès.', 'success')
    else:
        flash('Erreur lors de l\'annulation de la commande.', 'danger')
    
    return redirect(url_for('orders.index'))