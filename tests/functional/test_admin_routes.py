#------------------------------------------------------
# tests/functional/test_admin_routes.py - Tests des routes d'administration
#------------------------------------------------------

import pytest

def test_admin_login_required(client):
    """Test that admin routes require login."""
    # Try to access admin dashboard without login
    response = client.get('/admin-custom/', follow_redirects=True)
    assert response.status_code == 200
    assert b'connecter' in response.data.lower()  # Should redirect to login page

def test_admin_role_required(client, auth, test_user, app):
    """Test that admin routes require admin role."""
    # First login with a non-admin user
    auth.login()
    
    # Try to access admin dashboard
    response = client.get('/admin-custom/', follow_redirects=True)
    assert response.status_code == 200
    assert b'acc\xc3\xa8s refus\xc3\xa9' in response.data.lower()  # "accès refusé" in UTF-8

def test_admin_dashboard_access(client, app, db_session, test_user):
    """Test that admin can access dashboard."""
    # Upgrade test user to admin
    with app.app_context():
        test_user.role = 'administrateur'
        db_session.commit()
    
    # Login
    client.post(
        '/auth/login',
        data={'email': 'test@example.com', 'password': 'password123'}
    )
    
    # Access admin dashboard
    response = client.get('/admin-custom/')
    assert response.status_code == 200
    assert b'Tableau de bord' in response.data

def test_admin_offer_management(client, app, db_session, test_user, test_offer):
    """Test admin offer management."""
    # Upgrade test user to admin
    with app.app_context():
        test_user.role = 'administrateur'
        db_session.commit()
    
    # Login
    client.post(
        '/auth/login',
        data={'email': 'test@example.com', 'password': 'password123'}
    )
    
    # Access offer management page
    response = client.get('/admin-custom/offers')
    assert response.status_code == 200
    assert b'Gestion des offres' in response.data
    assert bytes(f'>{test_offer.titre}<', 'utf-8') in response.data
    
    # Test offer editing page
    response = client.get(f'/admin-custom/offers/{test_offer.id}/edit')
    assert response.status_code == 200
    assert bytes(f'value="{test_offer.titre}"', 'utf-8') in response.data