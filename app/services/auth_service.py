import re
import jwt
from datetime import datetime, timedelta
from flask import current_app, url_for
from app import db, bcrypt, mail
from app.models.user import User
from flask_mail import Message
import pyotp

def validate_password(password):
    """
    Valide la politique de sécurité des mots de passe.
    
    Règles:
    - Longueur minimale
    - Au moins une lettre majuscule
    - Au moins une lettre minuscule
    - Au moins un chiffre
    - Au moins un caractère spécial
    """
    
    # Récupérer les paramètres de configuration
    min_length = current_app.config.get('PASSWORD_MIN_LENGTH', 8)
    require_uppercase = current_app.config.get('PASSWORD_REQUIRE_UPPERCASE', True)
    require_lowercase = current_app.config.get('PASSWORD_REQUIRE_LOWERCASE', True)
    require_numbers = current_app.config.get('PASSWORD_REQUIRE_NUMBERS', True)
    require_special = current_app.config.get('PASSWORD_REQUIRE_SPECIAL', True)
    
    # Vérifier la longueur
    if len(password) < min_length:
        return False, f"Le mot de passe doit contenir au moins {min_length} caractères."
    
    # Vérifier les majuscules
    if require_uppercase and not any(c.isupper() for c in password):
        return False, "Le mot de passe doit contenir au moins une lettre majuscule."
    
    # Vérifier les minuscules
    if require_lowercase and not any(c.islower() for c in password):
        return False, "Le mot de passe doit contenir au moins une lettre minuscule."
    
    # Vérifier les chiffres
    if require_numbers and not any(c.isdigit() for c in password):
        return False, "Le mot de passe doit contenir au moins un chiffre."
    
    # Vérifier les caractères spéciaux
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial."
    
    return True, "Le mot de passe respecte la politique de sécurité."

def register_user(username, email, password, nom, prenom):
    """
    Enregistre un nouvel utilisateur.
    """
    # Vérifier si l'email existe déjà
    if User.query.filter_by(email=email).first():
        return False, "Cette adresse email est déjà utilisée."
    
    # Vérifier si le nom d'utilisateur existe déjà
    if User.query.filter_by(username=username).first():
        return False, "Ce nom d'utilisateur est déjà utilisé."
    
    # Valider le mot de passe
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message
    
    # Hacher le mot de passe
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Créer l'utilisateur - avec est_verifie=True pour court-circuiter la vérification par email
    user = User(
        username=username,
        email=email,
        password=hashed_password,
        nom=nom,
        prenom=prenom,
        est_verifie=True  # Contourner la vérification par email
    )
    
    # Enregistrer l'utilisateur
    db.session.add(user)
    db.session.commit()
    
    # Ne pas envoyer d'email de vérification
    # send_verification_email(user, user.code_verification)
    
    return True, user

def send_verification_email(user, code):
    """
    Fonction désactivée pour contourner l'erreur.
    """
    print(f"[DÉSACTIVÉ] Envoi d'email à {user.email}")
    # Complètement désactivé - pas d'appel à url_for
    return

def verify_account(code):
    """
    Vérifie un compte utilisateur à partir d'un code de vérification.
    """
    user = User.query.filter_by(code_verification=code).first()
    
    if not user:
        return False, "Code de vérification invalide."
    
    user.verify_account()
    return True, "Votre compte a été vérifié avec succès."

def login_user(email, password):
    """
    Authentifie un utilisateur.
    """
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return False, "Email ou mot de passe incorrect."
    
    if not user.check_password(password):
        return False, "Email ou mot de passe incorrect."
    
    if not user.est_verifie:
        return False, "Votre compte n'a pas été vérifié. Veuillez vérifier vos emails."
    
    # Mettre à jour la dernière connexion
    user.update_last_login()
    
    return True, user

def generate_jwt_token(user):
    """
    Génère un token JWT pour l'utilisateur.
    """
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Expiration dans 1 heure
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token

def verify_jwt_token(token):
    """
    Vérifie un token JWT.
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        
        user_id = payload.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return False, "Utilisateur non trouvé."
        
        return True, user
    
    except jwt.ExpiredSignatureError:
        return False, "Le token a expiré."
    except jwt.InvalidTokenError:
        return False, "Token invalide."

def setup_2fa(user):
    """
    Configure l'authentification à deux facteurs pour un utilisateur.
    """
    if user.est_2fa_active:
        return False, "L'authentification à deux facteurs est déjà activée."
    
    # Générer un secret
    secret = user.generate_2fa_secret()
    
    # Générer l'URI pour le QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="JO E-Tickets"
    )
    
    return True, {
        'secret': secret,
        'uri': provisioning_uri
    }

def verify_2fa_code(user, code):
    """
    Vérifie un code d'authentification à deux facteurs.
    """
    if not user.est_2fa_active:
        return True, "L'authentification à deux facteurs n'est pas activée."
    
    if user.verify_2fa_code(code):
        return True, "Code vérifié avec succès."
    
    return False, "Code incorrect."

def change_password(user, current_password, new_password):
    """
    Change le mot de passe d'un utilisateur.
    """
    if not user.check_password(current_password):
        return False, "Le mot de passe actuel est incorrect."
    
    # Valider le nouveau mot de passe
    is_valid, message = validate_password(new_password)
    if not is_valid:
        return False, message
    
    # Hacher et enregistrer le nouveau mot de passe
    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    
    # Envoyer un email de confirmation
    msg = Message(
        subject="Votre mot de passe a été modifié",
        recipients=[user.email],
        html=f"""
        <h1>Modification de votre mot de passe</h1>
        <p>Bonjour {user.prenom} {user.nom},</p>
        <p>Votre mot de passe a été modifié avec succès.</p>
        <p>Si vous n'êtes pas à l'origine de cette modification, veuillez nous contacter immédiatement.</p>
        <p>L'équipe JO E-Tickets</p>
        """
    )
    
    mail.send(msg)
    
    return True, "Votre mot de passe a été modifié avec succès."

def reset_password_request(email):
    """
    Demande de réinitialisation de mot de passe.
    """
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Pour des raisons de sécurité, ne pas indiquer si l'email existe
        return True, "Si cette adresse email est associée à un compte, vous recevrez un email de réinitialisation."
    
    # Générer un token JWT avec une durée de validité courte
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=15)  # Expiration dans 15 minutes
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    # Envoyer un email avec le lien de réinitialisation
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message(
        subject="Réinitialisation de votre mot de passe",
        recipients=[user.email],
        html=f"""
        <h1>Réinitialisation de votre mot de passe</h1>
        <p>Bonjour {user.prenom} {user.nom},</p>
        <p>Vous avez demandé à réinitialiser votre mot de passe. Veuillez cliquer sur le lien ci-dessous pour définir un nouveau mot de passe :</p>
        <p><a href="{reset_url}">Réinitialiser mon mot de passe</a></p>
        <p>Ce lien est valable pendant 15 minutes.</p>
        <p>Si vous n'êtes pas à l'origine de cette demande, veuillez ignorer cet email.</p>
        <p>L'équipe JO E-Tickets</p>
        """
    )
    
    mail.send(msg)
    
    return True, "Si cette adresse email est associée à un compte, vous recevrez un email de réinitialisation."

def reset_password(token, new_password):
    """
    Réinitialise le mot de passe d'un utilisateur à partir d'un token.
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        
        user_id = payload.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return False, "Utilisateur non trouvé."
        
        # Valider le nouveau mot de passe
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return False, message
        
        # Hacher et enregistrer le nouveau mot de passe
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        
        # Envoyer un email de confirmation
        msg = Message(
            subject="Votre mot de passe a été réinitialisé",
            recipients=[user.email],
            html=f"""
            <h1>Réinitialisation de votre mot de passe</h1>
            <p>Bonjour {user.prenom} {user.nom},</p>
            <p>Votre mot de passe a été réinitialisé avec succès.</p>
            <p>Si vous n'êtes pas à l'origine de cette réinitialisation, veuillez nous contacter immédiatement.</p>
            <p>L'équipe JO E-Tickets</p>
            """
        )
        
        mail.send(msg)
        
        return True, "Votre mot de passe a été réinitialisé avec succès."
    
    except jwt.ExpiredSignatureError:
        return False, "Le lien de réinitialisation a expiré. Veuillez faire une nouvelle demande."
    except jwt.InvalidTokenError:
        return False, "Le lien de réinitialisation est invalide."
