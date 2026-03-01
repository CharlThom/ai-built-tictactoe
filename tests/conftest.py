import pytest
import os
from datetime import datetime, timedelta
import jwt
from src.config import SECRET_KEY, ALGORITHM


@pytest.fixture
def test_user_data():
    """Fixture providing test user data"""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPassword123!"
    }


@pytest.fixture
def valid_access_token():
    """Fixture providing a valid access token"""
    payload = {
        "user_id": "test_user_123",
        "type": "access",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def valid_refresh_token():
    """Fixture providing a valid refresh token"""
    payload = {
        "user_id": "test_user_123",
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def expired_token():
    """Fixture providing an expired token"""
    payload = {
        "user_id": "test_user_123",
        "type": "access",
        "exp": datetime.utcnow() - timedelta(hours=1),
        "iat": datetime.utcnow() - timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def mock_db_user():
    """Fixture providing mock database user object"""
    import bcrypt
    return {
        "_id": "user_123",
        "username": "testuser",
        "email": "testuser@example.com",
        "password": bcrypt.hashpw("TestPassword123!".encode(), bcrypt.gensalt()),
        "created_at": datetime.utcnow(),
        "is_active": True
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "test_secret_key_12345")
    
    yield
    
    # Cleanup after test
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture
def auth_headers(valid_access_token):
    """Fixture providing authentication headers"""
    return {
        "Authorization": f"Bearer {valid_access_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def invalid_token():
    """Fixture providing an invalid token"""
    return "invalid.jwt.token.format"


@pytest.fixture
def token_with_wrong_signature():
    """Fixture providing a token with wrong signature"""
    payload = {
        "user_id": "test_user_123",
        "type": "access",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, "wrong_secret_key", algorithm=ALGORITHM)
