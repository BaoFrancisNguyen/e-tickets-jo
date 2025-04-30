#------------------------------------------------------
# tests/functional/test_auth_routes.py - Tests des routes d'authentification
#------------------------------------------------------

import pytest

def test_register_page(client):
    """Test that the register page loads correctly."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Inscription' in response.data

def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Connexion' in response.data

def test_register_success(client, app):
    """Test successful user registration."""
    response = client.post(
        '/auth/register',
        data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
            'nom': 'New',
            'prenom': 'User'
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b'succ' in response.data  # "créé avec succès" in French
    
    # Verify user was created in database
    with app.app_context():
        from app.models.user import User
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.username == 'newuser'

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        '/auth/login',
        data={
            'email': 'test@example.com',
            'password': 'password123',
            'remember': False
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    # Should redirect to home page after login
    assert b'Bienvenue' in response.data or b'Accueil' in response.data

def test_login_failure(client):
    """Test login with incorrect credentials."""
    response = client.post(
        '/auth/login',
        data={
            'email': 'wrong@example.com',
            'password': 'wrongpassword',
            'remember': False
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b'incorrect' in response.data.lower()