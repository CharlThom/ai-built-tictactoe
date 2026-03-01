import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.auth.middleware import validate_token, generate_tokens
from src.auth.routes import register_user, login_user
from src.models.user import User
from src.config import SECRET_KEY, ALGORITHM
import bcrypt


class TestJWTTokenGeneration:
    """Test JWT token generation and validation"""

    def test_generate_access_token(self):
        """Test access token generation with valid payload"""
        user_id = "test_user_123"
        tokens = generate_tokens(user_id)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # Decode and verify access token
        decoded = jwt.decode(tokens["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["user_id"] == user_id
        assert decoded["type"] == "access"
        assert "exp" in decoded

    def test_generate_refresh_token(self):
        """Test refresh token generation with extended expiry"""
        user_id = "test_user_456"
        tokens = generate_tokens(user_id)
        
        decoded = jwt.decode(tokens["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["user_id"] == user_id
        assert decoded["type"] == "refresh"
        
        # Verify refresh token has longer expiry than access token
        access_decoded = jwt.decode(tokens["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["exp"] > access_decoded["exp"]

    def test_token_expiration(self):
        """Test expired token validation fails"""
        expired_token = jwt.encode(
            {"user_id": "test", "type": "access", "exp": datetime.utcnow() - timedelta(hours=1)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_invalid_signature(self):
        """Test token with invalid signature fails validation"""
        invalid_token = jwt.encode(
            {"user_id": "test", "type": "access", "exp": datetime.utcnow() + timedelta(hours=1)},
            "wrong_secret",
            algorithm=ALGORITHM
        )
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(invalid_token, SECRET_KEY, algorithms=[ALGORITHM])


class TestTokenValidationMiddleware:
    """Test token validation middleware"""

    def test_validate_valid_token(self):
        """Test middleware accepts valid token"""
        tokens = generate_tokens("user_123")
        result = validate_token(tokens["access_token"])
        
        assert result["valid"] is True
        assert result["user_id"] == "user_123"

    def test_validate_missing_token(self):
        """Test middleware rejects missing token"""
        result = validate_token(None)
        
        assert result["valid"] is False
        assert "error" in result

    def test_validate_malformed_token(self):
        """Test middleware rejects malformed token"""
        result = validate_token("invalid.token.format")
        
        assert result["valid"] is False
        assert "error" in result

    def test_validate_refresh_token_as_access(self):
        """Test middleware rejects refresh token when access token expected"""
        tokens = generate_tokens("user_123")
        result = validate_token(tokens["refresh_token"], token_type="access")
        
        assert result["valid"] is False
        assert "type" in result.get("error", "").lower()


class TestUserRegistration:
    """Test user registration endpoint"""

    @patch('src.auth.routes.db')
    def test_register_new_user_success(self, mock_db):
        """Test successful user registration"""
        mock_db.users.find_one.return_value = None
        mock_db.users.insert_one.return_value = Mock(inserted_id="new_user_id")
        
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
        
        result = register_user(payload)
        
        assert result["success"] is True
        assert "user_id" in result
        assert mock_db.users.insert_one.called
        
        # Verify password was hashed
        call_args = mock_db.users.insert_one.call_args[0][0]
        assert call_args["password"] != payload["password"]
        assert bcrypt.checkpw(payload["password"].encode(), call_args["password"])

    @patch('src.auth.routes.db')
    def test_register_duplicate_username(self, mock_db):
        """Test registration fails with duplicate username"""
        mock_db.users.find_one.return_value = {"username": "existinguser"}
        
        payload = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "SecurePass123!"
        }
        
        result = register_user(payload)
        
        assert result["success"] is False
        assert "exists" in result["error"].lower()

    def test_register_weak_password(self):
        """Test registration fails with weak password"""
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "123"
        }
        
        result = register_user(payload)
        
        assert result["success"] is False
        assert "password" in result["error"].lower()

    def test_register_invalid_email(self):
        """Test registration fails with invalid email"""
        payload = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "SecurePass123!"
        }
        
        result = register_user(payload)
        
        assert result["success"] is False
        assert "email" in result["error"].lower()


class TestUserLogin:
    """Test user login endpoint"""

    @patch('src.auth.routes.db')
    def test_login_success(self, mock_db):
        """Test successful login returns tokens"""
        password = "SecurePass123!"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        mock_db.users.find_one.return_value = {
            "_id": "user_123",
            "username": "testuser",
            "password": hashed
        }
        
        payload = {
            "username": "testuser",
            "password": password
        }
        
        result = login_user(payload)
        
        assert result["success"] is True
        assert "access_token" in result
        assert "refresh_token" in result
        assert "user_id" in result

    @patch('src.auth.routes.db')
    def test_login_invalid_username(self, mock_db):
        """Test login fails with non-existent username"""
        mock_db.users.find_one.return_value = None
        
        payload = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        result = login_user(payload)
        
        assert result["success"] is False
        assert "invalid" in result["error"].lower()

    @patch('src.auth.routes.db')
    def test_login_wrong_password(self, mock_db):
        """Test login fails with incorrect password"""
        correct_password = "CorrectPass123!"
        hashed = bcrypt.hashpw(correct_password.encode(), bcrypt.gensalt())
        
        mock_db.users.find_one.return_value = {
            "_id": "user_123",
            "username": "testuser",
            "password": hashed
        }
        
        payload = {
            "username": "testuser",
            "password": "WrongPassword"
        }
        
        result = login_user(payload)
        
        assert result["success"] is False
        assert "invalid" in result["error"].lower()

    @patch('src.auth.routes.db')
    def test_login_missing_credentials(self, mock_db):
        """Test login fails with missing credentials"""
        result = login_user({"username": "testuser"})
        assert result["success"] is False
        
        result = login_user({"password": "password"})
        assert result["success"] is False


class TestRefreshTokenFlow:
    """Test refresh token flow"""

    def test_refresh_token_generates_new_access_token(self):
        """Test refresh token can generate new access token"""
        tokens = generate_tokens("user_123")
        refresh_token = tokens["refresh_token"]
        
        # Validate refresh token
        decoded = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["type"] == "refresh"
        
        # Generate new access token
        new_tokens = generate_tokens(decoded["user_id"])
        assert "access_token" in new_tokens
        
        # Verify new access token is different
        assert new_tokens["access_token"] != tokens["access_token"]

    def test_access_token_cannot_refresh(self):
        """Test access token cannot be used for refresh"""
        tokens = generate_tokens("user_123")
        access_token = tokens["access_token"]
        
        decoded = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["type"] == "access"
        
        # Should not allow refresh with access token
        result = validate_token(access_token, token_type="refresh")
        assert result["valid"] is False
