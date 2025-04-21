from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User
from app.services.auth_service import validate_password

class RegistrationForm(FlaskForm):
    """
    Formulaire d'inscription.
    """
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(),
        Length(min=3, max=20)
    ])
    
    email = StringField('Adresse email', validators=[
        DataRequired(),
        Email()
    ])
    
    nom = StringField('Nom', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    
    prenom = StringField('Prénom', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    
    password = PasswordField('Mot de passe', validators=[
        DataRequired()
    ])
    
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    
    submit = SubmitField('S\'inscrire')
    
    def validate_username(self, username):
        """Vérifie que le nom d'utilisateur n'est pas déjà utilisé."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà utilisé. Veuillez en choisir un autre.')
    
    def validate_email(self, email):
        """Vérifie que l'email n'est pas déjà utilisé."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cette adresse email est déjà utilisée. Veuillez en choisir une autre.')
    
    def validate_password(self, password):
        """Vérifie que le mot de passe respecte la politique de sécurité."""
        is_valid, message = validate_password(password.data)
        if not is_valid:
            raise ValidationError(message)

class LoginForm(FlaskForm):
    """
    Formulaire de connexion.
    """
    email = StringField('Adresse email', validators=[
        DataRequired(),
        Email()
    ])
    
    password = PasswordField('Mot de passe', validators=[
        DataRequired()
    ])
    
    remember = BooleanField('Se souvenir de moi')
    
    submit = SubmitField('Se connecter')

class TwoFactorForm(FlaskForm):
    """
    Formulaire d'authentification à deux facteurs.
    """
    code = StringField('Code d\'authentification', validators=[
        DataRequired(),
        Length(min=6, max=6)
    ])
    
    submit = SubmitField('Vérifier')

class ChangePasswordForm(FlaskForm):
    """
    Formulaire de changement de mot de passe.
    """
    current_password = PasswordField('Mot de passe actuel', validators=[
        DataRequired()
    ])
    
    new_password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired()
    ])
    
    confirm_new_password = PasswordField('Confirmer le nouveau mot de passe', validators=[
        DataRequired(),
        EqualTo('new_password')
    ])
    
    submit = SubmitField('Changer le mot de passe')
    
    def validate_new_password(self, new_password):
        """Vérifie que le nouveau mot de passe respecte la politique de sécurité."""
        is_valid, message = validate_password(new_password.data)
        if not is_valid:
            raise ValidationError(message)

class RequestResetForm(FlaskForm):
    """
    Formulaire de demande de réinitialisation de mot de passe.
    """
    email = StringField('Adresse email', validators=[
        DataRequired(),
        Email()
    ])
    
    submit = SubmitField('Demander une réinitialisation')

class ResetPasswordForm(FlaskForm):
    """
    Formulaire de réinitialisation de mot de passe.
    """
    password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired()
    ])
    
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    
    submit = SubmitField('Réinitialiser le mot de passe')
    
    def validate_password(self, password):
        """Vérifie que le mot de passe respecte la politique de sécurité."""
        is_valid, message = validate_password(password.data)
        if not is_valid:
            raise ValidationError(message)
