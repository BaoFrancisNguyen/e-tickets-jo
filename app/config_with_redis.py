import os
from datetime import timedelta

class Config:
    """Configuration de base de l'application."""
    
    # Configuration de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE_ME_IN_PRODUCTION'
    SALT_KEY = os.environ.get('SALT_KEY') or 'CHANGE_ME_IN_PRODUCTION'
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///jo_etickets.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration de Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'mailhog'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 1025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@jo-etickets.fr'
    
    # Configuration des téléchargements
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Mo
    
    # Configuration de Flask-Session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Sera configuré dans __init__.py
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Configuration des mots de passe
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True