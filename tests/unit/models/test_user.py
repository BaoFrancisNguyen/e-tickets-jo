#------------------------------------------------------
# tests/unit/models/test_user.py - Tests du modèle User
#------------------------------------------------------

import pytest
from app.models.user import User

def test_user_attributes(test_user):
    """Test basic attributes of a user."""
    assert test_user.username == 'testuser'
    assert test_user.email == 'test@example.com'
    assert test_user.nom == 'Test'
    assert test_user.prenom == 'User'
    assert test_user.role == 'utilisateur'
    assert test_user.est_verifie is True

def test_user_check_password(app, db_session):
    """Test password verification."""
    with app.app_context():
        from app import bcrypt
        from app.models.user import User
        
        # Créer un utilisateur avec un mot de passe connu
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(
            username='testpwduser',
            email='testpwd@example.com',
            password=hashed_password,
            nom='Test',
            prenom='User',
            est_verifie=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Vérifier avec le bon mot de passe
        assert user.check_password('password123') is True
        
        # Vérifier avec un mauvais mot de passe
        assert user.check_password('wrongpassword') is False

def test_user_roles(test_user, app, db_session):
    """Test user role functions."""
    with app.app_context():
        # Par défaut, l'utilisateur n'est pas admin
        assert test_user.is_admin() is False
        
        # Changer le rôle
        test_user.role = 'administrateur'
        db_session.commit()
        
        # Maintenant il devrait être admin
        assert test_user.is_admin() is True