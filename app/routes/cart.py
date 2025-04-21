from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.cart import Cart, CartItem

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def index():
    """
    Affiche le contenu du panier de l'utilisateur.
    """
    # Récupérer le panier de l'utilisateur
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    return render_template('cart/index.html', cart=cart)

@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_item(item_id):
    """
    Met à jour la quantité d'un article dans le panier.
    """
    # Récupérer le panier de l'utilisateur
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('cart.index'))
    
    # Récupérer la nouvelle quantité
    quantity = int(request.form.get('quantity', 0))
    
    # Mettre à jour l'article
    if cart.update_item(item_id, quantity):
        flash('Panier mis à jour.', 'success')
    else:
        flash('Erreur lors de la mise à jour du panier.', 'danger')
    
    return redirect(url_for('cart.index'))

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id):
    """
    Supprime un article du panier.
    """
    # Récupérer le panier de l'utilisateur
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('cart.index'))
    
    # Supprimer l'article
    if cart.remove_item(item_id):
        flash('Article supprimé du panier.', 'success')
    else:
        flash('Erreur lors de la suppression de l\'article.', 'danger')
    
    return redirect(url_for('cart.index'))

@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear():
    """
    Vide le panier de l'utilisateur.
    """
    # Récupérer le panier de l'utilisateur
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart:
        flash('Votre panier est déjà vide.', 'info')
        return redirect(url_for('cart.index'))
    
    # Vider le panier
    if cart.clear():
        flash('Votre panier a été vidé.', 'success')
    else:
        flash('Erreur lors de la suppression des articles.', 'danger')
    
    return redirect(url_for('cart.index'))

@cart_bp.route('/checkout')
@login_required
def checkout():
    """
    Affiche la page de paiement.
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
    
    return render_template('cart/checkout.html', cart=cart)

@cart_bp.route('/api/count')
@login_required
def api_count():
    """
    API pour récupérer le nombre d'articles dans le panier (utilisé pour l'affichage dynamique).
    """
    # Récupérer le panier de l'utilisateur
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    count = 0
    if cart:
        count = cart.count_items()
    
    return jsonify({'count': count})
