import pytest
from app.services.auth_service import validate_password, register_user, login_user
from app.models.user import User

def test_password_validation(app):
    """Test the password validation logic."""
    with app.app_context():
        # Valid password
        is_valid, _ = validate_password("StrongPass123!")
        assert is_valid is True

        # Too short
        is_valid, message = validate_password("Short1!")
        assert is_valid is False
        assert "8 caractères" in message  # Vérifier le message sans compter sur "longueur"

        # No uppercase
        is_valid, message = validate_password("lowercase123!")
        assert is_valid is False
        assert "majuscule" in message.lower()
        
        # No lowercase
        is_valid, message = validate_password("UPPERCASE123!")
        assert is_valid is False
        assert "minuscule" in message.lower()
        
        # No digit
        is_valid, message = validate_password("NoDigit!@#")
        assert is_valid is False
        assert "chiffre" in message.lower()
        
        # No special char
        is_valid, message = validate_password("NoSpecial123")
        assert is_valid is False
        assert "spécial" in message.lower() or "special" in message.lower()

def test_user_registration(app, db_session):
    """Test user registration functionality."""
    with app.app_context():
        # Valid registration
        success, user = register_user(
            username="testuser2",
            email="testuser2@example.com",
            password="ValidPass123!",
            nom="Test",
            prenom="User"
        )
        assert success is True
        assert isinstance(user, User)
        
        # Check that the user was saved to the database
        saved_user = User.query.filter_by(email="testuser2@example.com").first()
        assert saved_user is not None
        assert saved_user.username == "testuser2"
        
        # Duplicate email
        success, message = register_user(
            username="testuser3",
            email="testuser2@example.com",  # Same email as above
            password="ValidPass123!",
            nom="Another",
            prenom="User"
        )
        assert success is False
        assert "email" in message.lower()
        
        # Invalid password
        success, message = register_user(
            username="testuser4",
            email="testuser4@example.com",
            password="weak",
            nom="Test",
            prenom="User"
        )
        assert success is False

def test_user_login(app, db_session):
    """Test user login functionality."""
    with app.app_context():
        # Create a test user
        from app import bcrypt
        user = User(
            username="logintest",
            email="logintest@example.com",
            password=bcrypt.generate_password_hash("TestPass123!").decode('utf-8'),
            nom="Login",
            prenom="Test",
            est_verifie=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Successful login
        success, result = login_user(
            email="logintest@example.com",
            password="TestPass123!"
        )
        assert success is True
        assert isinstance(result, User)
        assert result.id == user.id
        
        # Wrong email
        success, message = login_user(
            email="wrong@example.com",
            password="TestPass123!"
        )
        assert success is False
        assert "incorrect" in message.lower()
        
        # Wrong password
        success, message = login_user(
            email="logintest@example.com",
            password="WrongPass123!"
        )
        assert success is False
        assert "incorrect" in message.lower()
        
        # Unverified account
        user.est_verifie = False
        db_session.commit()
        
        success, message = login_user(
            email="logintest@example.com",
            password="TestPass123!"
        )
        assert success is False
        assert "vérifié" in message.lower() or "verifie" in message.lower()