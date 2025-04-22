from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash, request
from app import bcrypt
from app.models.user import User
from wtforms import PasswordField, StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length

class AdminBaseView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'administrateur'
    
    def inaccessible_callback(self, name, **kwargs):
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('auth.login', next=request.url))

class UserAdminView(AdminBaseView):
    # Définir les colonnes à afficher dans la liste
    column_list = ('id', 'username', 'email', 'nom', 'prenom', 'role', 'est_verifie')
    
    # Définir les colonnes qui peuvent être triées
    column_sortable_list = ('id', 'username', 'email', 'nom', 'prenom', 'role')
    
    # Définir les colonnes qui peuvent être filtrées
    column_filters = ('username', 'email', 'role', 'est_verifie')
    
    # Définir les colonnes qui peuvent être recherchées
    column_searchable_list = ('username', 'email', 'nom', 'prenom')
    
    # Masquer les colonnes sensibles
    column_exclude_list = ('password', 'cle_securite', 'code_verification', 'code_2fa_secret')
    
    # Ajout de champs personnalisés
    form_args = {
        'username': {
            'label': 'Nom d\'utilisateur',
            'validators': [DataRequired(), Length(min=3, max=20)]
        },
        'email': {
            'label': 'Adresse email',
            'validators': [DataRequired(), Email()]
        },
        'nom': {
            'label': 'Nom',
            'validators': [DataRequired(), Length(min=2, max=50)]
        },
        'prenom': {
            'label': 'Prénom',
            'validators': [DataRequired(), Length(min=2, max=50)]
        },
        'role': {
            'label': 'Rôle'
        },
        'est_verifie': {
            'label': 'Compte vérifié'
        }
    }
    
    # Définir les champs supplémentaires pour le formulaire
    form_extra_fields = {
        'password': PasswordField('Mot de passe')
    }
    
    # Désactiver les modaux pour éviter les problèmes
    create_modal = False
    edit_modal = False
    
    def on_model_change(self, form, model, is_created):
        """Appelé lorsqu'un modèle est créé ou modifié."""
        # Si un mot de passe est fourni, le hacher
        if form.password and form.password.data:
            model.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Si c'est une création, générer la clé de sécurité
        if is_created:
            model.cle_securite = model._generate_security_key()

class OfferAdminView(AdminBaseView):
    # Configurer les colonnes et les options pour les offres
    column_list = ('id', 'titre', 'type', 'prix', 'disponibilite', 'date_evenement', 'est_publie')
    column_sortable_list = ('id', 'titre', 'type', 'prix', 'disponibilite', 'date_evenement')
    column_filters = ('type', 'est_publie')
    column_searchable_list = ('titre', 'description')
    
    # Désactiver les modaux pour éviter les problèmes
    create_modal = False
    edit_modal = False

class OrderAdminView(AdminBaseView):
    # Configurer les colonnes et les options pour les commandes
    column_list = ('id', 'reference', 'user.username', 'total', 'statut', 'date_commande')
    column_sortable_list = ('id', 'reference', 'total', 'date_commande')
    column_filters = ('statut',)
    column_searchable_list = ('reference',)
    
    # Les commandes ne peuvent pas être créées manuellement
    can_create = False
    
    # Désactiver les modaux pour éviter les problèmes
    create_modal = False
    edit_modal = False

class TicketAdminView(AdminBaseView):
    # Configurer les colonnes et les options pour les billets
    column_list = ('id', 'order.reference', 'offer.titre', 'est_valide', 'date_generation')
    column_sortable_list = ('id', 'date_generation')
    column_filters = ('est_valide',)
    
    # Les billets ne peuvent pas être créés manuellement
    can_create = False
    
    # Désactiver les modaux pour éviter les problèmes
    create_modal = False
    edit_modal = False

def init_admin(admin):
    """Initialise l'interface d'administration Flask-Admin"""
    # Importer les modèles
    from app.models.user import User
    from app.models.offer import Offer
    from app.models.order import Order
    from app.models.ticket import Ticket
    from app import db
    
    # Ajouter les vues à l'admin
    admin.add_view(UserAdminView(User, db.session, name="Utilisateurs"))
    admin.add_view(OfferAdminView(Offer, db.session, name="Offres"))
    admin.add_view(OrderAdminView(Order, db.session, name="Commandes"))
    admin.add_view(TicketAdminView(Ticket, db.session, name="Billets"))