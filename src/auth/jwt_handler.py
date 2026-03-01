import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from functools import wraps
from flask import request, jsonify


class JWTHandler:
    """Handles JWT token generation and validation"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
        self.refresh_token_expire_days = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    
    def generate_access_token(self, user_id: str, email: str, additional_claims: Optional[Dict] = None) -> str:
        """Generate JWT access token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            'iat': datetime.utcnow()
        }
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate JWT refresh token"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return {'valid': True, 'payload': payload, 'error': None}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'payload': None, 'error': 'Token has expired'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'payload': None, 'error': f'Invalid token: {str(e)}'}
    
    def verify_access_token(self, token: str) -> Optional[Dict]:
        """Verify access token and return payload if valid"""
        result = self.decode_token(token)
        if result['valid'] and result['payload'].get('type') == 'access':
            return result['payload']
        return None
    
    def verify_refresh_token(self, token: str) -> Optional[Dict]:
        """Verify refresh token and return payload if valid"""
        result = self.decode_token(token)
        if result['valid'] and result['payload'].get('type') == 'refresh':
            return result['payload']
        return None


jwt_handler = JWTHandler()


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        payload = jwt_handler.verify_access_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated


def optional_token(f):
    """Decorator for routes where authentication is optional"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = jwt_handler.verify_access_token(token)
            request.current_user = payload if payload else None
        else:
            request.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated