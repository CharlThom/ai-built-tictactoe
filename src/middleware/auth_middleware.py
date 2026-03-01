from functools import wraps
from flask import request, jsonify, g
import jwt
from src.config import Config
from src.models.user import User


def token_required(f):
    """Middleware decorator to protect endpoints with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format. Use: Bearer <token>'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            # Decode and verify token
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            
            # Get user from database
            user = User.query.filter_by(id=payload['user_id']).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            # Store user in Flask's g object for access in route handlers
            g.current_user = user
            g.user_id = user.id
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def optional_token(f):
    """Middleware decorator that allows but doesn't require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        g.current_user = None
        g.user_id = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
                user = User.query.filter_by(id=payload['user_id']).first()
                if user:
                    g.current_user = user
                    g.user_id = user.id
            except:
                pass  # Continue without authentication
        
        return f(*args, **kwargs)
    
    return decorated