import os
import tempfile

def test_config():
    """Test la configuration par défaut."""
    from app import create_app
    
    app = create_app()
    assert app.config['SECRET_KEY'] is not None
    assert app.config['SQLALCHEMY_DATABASE_URI'] is not None
    assert app.config['SALT_KEY'] is not None

def test_testing_config():
    """Test la configuration de test."""
    from app import create_app
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-key',
        'SALT_KEY': 'test-salt'
    })
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert app.config['SECRET_KEY'] == 'test-key'

def test_upload_folder_exists():
    """Test que le dossier d'upload existe."""
    from app import create_app
    from app.admin_config import _initialized
    
    # Réinitialiser le flag pour éviter les erreurs de blueprint déjà enregistré
    _initialized = False
    
    # Configuration de test
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'UPLOAD_FOLDER': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app', 'static', 'uploads'),
        'SECRET_KEY': 'test-key',
        'SALT_KEY': 'test-salt'
    })
    
    # Vérifier que le dossier d'upload existe
    upload_folder = app.config['UPLOAD_FOLDER']
    assert os.path.exists(upload_folder) or os.makedirs(upload_folder, exist_ok=True)