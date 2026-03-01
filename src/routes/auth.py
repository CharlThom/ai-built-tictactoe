from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta
from src.models.user import User
from src.database import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token using a valid refresh token.
    Expected JSON: {"refresh_token": "<token>"}
    Returns: {"access_token": "<new_token>", "expires_in": <seconds>}
    """
    try:
        data = request.get_json()
        
        if not data or 'refresh_token' not in data:
            return jsonify({
                'error': 'Refresh token is required',
                'message': 'Please provide refresh_token in request body'
            }), 400
        
        refresh_token = data['refresh_token']
        
        # Decode and validate refresh token
        try:
            payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Refresh token has expired',
                'message': 'Please login again to get new tokens'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'error': 'Invalid refresh token',
                'message': 'Token is malformed or invalid'
            }), 401
        
        # Verify token type is refresh
        if payload.get('type') != 'refresh':
            return jsonify({
                'error': 'Invalid token type',
                'message': 'Provided token is not a refresh token'
            }), 401
        
        # Get user from database
        user_id = payload.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'User associated with this token does not exist'
            }), 401
        
        # Check if user is active (optional security check)
        if hasattr(user, 'is_active') and not user.is_active:
            return jsonify({
                'error': 'Account disabled',
                'message': 'This account has been deactivated'
            }), 401
        
        # Generate new access token
        access_token_payload = {
            'user_id': user.id,
            'username': user.username,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow()
        }
        
        new_access_token = jwt.encode(
            access_token_payload,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        return jsonify({
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            'user': {
                'id': user.id,
                'username': user.username
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Token refresh failed',
            'message': str(e)
        }), 500

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """
    Verify if the current access token is valid.
    Requires Authorization header with Bearer token.
    """
    return jsonify({
        'valid': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Logout endpoint (client should discard tokens).
    For production, implement token blacklisting.
    """
    # In production, add refresh token to blacklist/revocation list
    # For now, client-side token removal is sufficient
    return jsonify({
        'message': 'Successfully logged out',
        'note': 'Please discard your tokens on the client side'
    }), 200