from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_admin import Admin
from flask_session import Session
from app.config import Config
from app.admin_views import AdminHomeView  # Importer depuis app.admin_views

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()
mail = Mail()
admin = Admin(name='JO E-Tickets Admin', template_mode='bootstrap4', index_view=AdminHomeView())
session = Session()

# Stockage global pour les vues admin
admin_views = {}

def create_app(config=None):
    app = Flask(__name__)
    
    # Charger la configuration par défaut
    app.config.from_object(Config)
    
    # Mettre à jour avec la configuration spécifique passée en paramètre
    if config is not None:
        app.config.update(config)
    
    # Vérifier que SQLALCHEMY_DATABASE_URI est défini
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jo_etickets.db'
    
    # Initialisation des extensions avec l'application
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    session.init_app(app)
    
    # Initialiser seulement si DISABLE_ADMIN n'est pas True (utile pour les tests)
    if not app.config.get('DISABLE_ADMIN', False):
        # Initialisation de Flask-Admin
        admin.init_app(app)
        with app.app_context():
            # Vider le stockage global des vues admin
            global admin_views
            admin_views.clear()
            # Initialiser l'admin
            from app.admin_config import init_admin
            init_admin(admin)

    # Enregistrement des blueprints
    from app.routes.auth import auth_bp
    from app.routes.offers import offers_bp
    from app.routes.cart import cart_bp
    from app.routes.orders import orders_bp
    from app.routes.tickets import tickets_bp
    from app.routes.admin import admin_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(offers_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    # Gestionnaire d'erreurs
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app