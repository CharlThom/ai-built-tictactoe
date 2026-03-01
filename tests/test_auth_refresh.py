import unittest
import json
from datetime import datetime, timedelta
import jwt
from src.app import create_app
from src.database import db
from src.models.user import User
import os

JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

class TestTokenRefresh(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        from werkzeug.security import generate_password_hash
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('TestPass123!')
        )
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def generate_refresh_token(self, user_id, expired=False):
        """Helper to generate refresh token for testing"""
        exp_time = datetime.utcnow() - timedelta(days=1) if expired else datetime.utcnow() + timedelta(days=7)
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': exp_time,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def test_refresh_token_success(self):
        """Test successful token refresh"""
        refresh_token = self.generate_refresh_token(self.test_user.id)
        
        response = self.client.post(
            '/api/auth/refresh',
            data=json.dumps({'refresh_token': refresh_token}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('expires_in', data)
        self.assertEqual(data['token_type'], 'Bearer')
    
    def test_refresh_token_missing(self):
        """Test refresh endpoint without token"""
        response = self.client.post(
            '/api/auth/refresh',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_refresh_token_expired(self):
        """Test refresh with expired token"""
        expired_token = self.generate_refresh_token(self.test_user.id, expired=True)
        
        response = self.client.post(
            '/api/auth/refresh',
            data=json.dumps({'refresh_token': expired_token}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('expired', data['error'].lower())
    
    def test_refresh_token_invalid(self):
        """Test refresh with invalid token"""
        response = self.client.post(
            '/api/auth/refresh',
            data=json.dumps({'refresh_token': 'invalid.token.here'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_refresh_with_access_token(self):
        """Test that access token cannot be used for refresh"""
        access_payload = {
            'user_id': self.test_user.id,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }
        access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        response = self.client.post(
            '/api/auth/refresh',
            data=json.dumps({'refresh_token': access_token}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('type', data['error'].lower())

if __name__ == '__main__':
    unittest.main()