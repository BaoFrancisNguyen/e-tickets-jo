from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.offer import Offer
from app.models.order import Order
from app.models.ticket import Ticket
from app.forms.admin_forms import OfferForm, UserForm
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
from flask import current_app

# Utiliser un préfixe d'URL différent pour éviter les conflits avec Flask-Admin
admin_bp = Blueprint('admin_custom', __name__, url_prefix='/admin-custom')

# Routes pour l'administration
@admin_bp.route('/')
@login_required
def index():
    """
    Tableau de bord administrateur.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    # Statistiques générales
    total_users = User.query.count()
    total_offers = Offer.query.count()
    total_orders = Order.query.count()
    total_tickets = Ticket.query.count()
    
    # Statistiques des offres
    offers_stats = db.session.query(
        Offer.type,
        db.func.count(Ticket.id).label('tickets_count')
    ).outerjoin(Ticket).group_by(Offer.type).all()
    
    offers_stats_dict = {
        'solo': 0,
        'duo': 0,
        'familiale': 0
    }
    
    for offer_type, count in offers_stats:
        offers_stats_dict[offer_type] = count
    
    # Commandes récentes
    recent_orders = Order.query.filter_by(statut='payée').order_by(Order.date_commande.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_offers=total_offers,
        total_orders=total_orders,
        total_tickets=total_tickets,
        offers_stats=offers_stats_dict,
        recent_orders=recent_orders
    )

@admin_bp.route('/offers')
@login_required
def offers():
    """
    Gestion des offres.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    offers = Offer.query.all()
    return render_template('admin/offers.html', offers=offers)

@admin_bp.route('/offers/new', methods=['GET', 'POST'])
@login_required
def new_offer():
    """
    Création d'une nouvelle offre.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    form = OfferForm()
    
    if form.validate_on_submit():
        offer = Offer(
            titre=form.titre.data,
            description=form.description.data,
            type=form.type.data,
            nombre_personnes=form.nombre_personnes.data,
            prix=form.prix.data,
            date_evenement=form.date_evenement.data,
            disponibilite=form.disponibilite.data,
            est_publie=form.est_publie.data
        )
        
        # Traitement de l'image
        if form.image.data:
            # Code pour sauvegarder l'image
            filename = secure_filename(form.image.data.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(file_path)
            offer.image = filename
        
        db.session.add(offer)
        db.session.commit()
        
        flash(f'Offre "{offer.titre}" créée avec succès.', 'success')
        return redirect(url_for('admin_custom.offers'))
    
    return render_template('admin/offer_form.html', form=form, title='Nouvelle offre')

@admin_bp.route('/offers/<int:offer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_offer(offer_id):
    """
    Modification d'une offre existante.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    offer = Offer.query.get_or_404(offer_id)
    form = OfferForm(obj=offer)
    
    if form.validate_on_submit():
        offer.titre = form.titre.data
        offer.description = form.description.data
        offer.type = form.type.data
        offer.nombre_personnes = form.nombre_personnes.data
        offer.prix = form.prix.data
        offer.date_evenement = form.date_evenement.data
        offer.disponibilite = form.disponibilite.data
        offer.est_publie = form.est_publie.data
        
        # Traitement de l'image
        if form.image.data:
            # Code pour sauvegarder l'image
            filename = secure_filename(form.image.data.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(file_path)
            offer.image = filename
        
        db.session.commit()
        
        flash(f'Offre "{offer.titre}" modifiée avec succès.', 'success')
        return redirect(url_for('admin_custom.offers'))
    
    return render_template('admin/offer_form.html', form=form, offer=offer, title='Modifier l\'offre')

@admin_bp.route('/offers/<int:offer_id>/delete', methods=['POST'])
@login_required
def delete_offer(offer_id):
    """
    Suppression d'une offre.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    offer = Offer.query.get_or_404(offer_id)
    
    # Vérifier si l'offre a des billets associés
    if offer.tickets:
        flash(f'Impossible de supprimer l\'offre "{offer.titre}" car elle a des billets associés.', 'danger')
        return redirect(url_for('admin_custom.offers'))
    
    db.session.delete(offer)
    db.session.commit()
    
    flash(f'Offre "{offer.titre}" supprimée avec succès.', 'success')
    return redirect(url_for('admin_custom.offers'))

@admin_bp.route('/users')
@login_required
def users():
    """
    Gestion des utilisateurs.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    """
    Création d'un nouvel utilisateur.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    from app import bcrypt
    form = UserForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            nom=form.nom.data,
            prenom=form.prenom.data,
            role=form.role.data,
            est_verifie=form.est_verifie.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Utilisateur "{user.username}" créé avec succès.', 'success')
        return redirect(url_for('admin_custom.users'))
    
    return render_template('admin/user_form.html', form=form, title='Nouvel utilisateur')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """
    Modification d'un utilisateur existant.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    from app import bcrypt
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    # Ne pas exiger le mot de passe en édition
    form.password.validators = []
    form.confirm_password.validators = []
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.nom = form.nom.data
        user.prenom = form.prenom.data
        user.role = form.role.data
        user.est_verifie = form.est_verifie.data
        
        # Changer le mot de passe uniquement s'il est fourni
        if form.password.data:
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        db.session.commit()
        
        flash(f'Utilisateur "{user.username}" modifié avec succès.', 'success')
        return redirect(url_for('admin_custom.users'))
    
    # Vider les champs de mot de passe pour l'affichage
    form.password.data = ''
    form.confirm_password.data = ''
    
    return render_template('admin/user_form.html', form=form, user=user, title='Modifier l\'utilisateur')

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """
    Suppression d'un utilisateur.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    # Empêcher la suppression de son propre compte
    if user_id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('admin_custom.users'))
    
    user = User.query.get_or_404(user_id)
    
    # Vérifier si l'utilisateur a des commandes ou des billets associés
    if user.orders or user.tickets:
        flash(f'Impossible de supprimer l\'utilisateur "{user.username}" car il a des commandes ou des billets associés.', 'danger')
        return redirect(url_for('admin_custom.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Utilisateur "{user.username}" supprimé avec succès.', 'success')
    return redirect(url_for('admin_custom.users'))

@admin_bp.route('/orders')
@login_required
def orders():
    """
    Gestion des commandes.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    orders = Order.query.all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/tickets')
@login_required
def tickets():
    """
    Gestion des billets.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    tickets = Ticket.query.all()
    return render_template('admin/tickets.html', tickets=tickets)

@admin_bp.route('/stats')
@login_required
def stats():
    """
    Statistiques des ventes.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    # Statistiques par type d'offre
    offers_stats = db.session.query(
        Offer.type,
        db.func.count(Ticket.id).label('tickets_count')
    ).outerjoin(Ticket).group_by(Offer.type).all()
    
    offers_data = {
        'labels': [offer_type for offer_type, _ in offers_stats],
        'data': [count for _, count in offers_stats]
    }
    
    # Statistiques par date
    date_stats = db.session.query(
        db.func.date(Order.date_commande).label('date'),
        db.func.count(Order.id).label('orders_count'),
        db.func.sum(Order.total).label('total_sales')
    ).filter(Order.statut == 'payée').group_by('date').order_by('date').all()
    
    date_data = {
        'labels': [date.strftime('%d/%m/%Y') for date, _, _ in date_stats],
        'orders': [count for _, count, _ in date_stats],
        'sales': [float(total) if total else 0 for _, _, total in date_stats]
    }
    
    return render_template(
        'admin/stats.html',
        offers_data=json.dumps(offers_data),
        date_data=json.dumps(date_data)
    )

@admin_bp.route('/api/stats/offers')
@login_required
def api_stats_offers():
    """
    API pour les statistiques des offres.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Accès refusé'}), 403
    
    # Statistiques par type d'offre
    offers_stats = db.session.query(
        Offer.type,
        db.func.count(Ticket.id).label('tickets_count')
    ).outerjoin(Ticket).group_by(Offer.type).all()
    
    offers_data = {
        'labels': [offer_type for offer_type, _ in offers_stats],
        'data': [count for _, count in offers_stats]
    }
    
    return jsonify(offers_data)

@admin_bp.route('/api/stats/sales')
@login_required
def api_stats_sales():
    """
    API pour les statistiques des ventes.
    """
    # Vérifier que l'utilisateur est administrateur
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Accès refusé'}), 403
    
    # Statistiques par date
    date_stats = db.session.query(
        db.func.date(Order.date_commande).label('date'),
        db.func.count(Order.id).label('orders_count'),
        db.func.sum(Order.total).label('total_sales')
    ).filter(Order.statut == 'payée').group_by('date').order_by('date').all()
    
    date_data = {
        'labels': [date.strftime('%d/%m/%Y') for date, _, _ in date_stats],
        'orders': [count for _, count, _ in date_stats],
        'sales': [float(total) if total else 0 for _, _, total in date_stats]
    }
    
    return jsonify(date_data)