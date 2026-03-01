from flask import Blueprint, jsonify, request
from functools import wraps
import jwt
from src.models.user import User
from src.config import Config

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = User.get_by_id(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Retrieve authenticated user profile data"""
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat() if hasattr(current_user.created_at, 'isoformat') else str(current_user.created_at),
            'games_played': current_user.games_played,
            'games_won': current_user.games_won,
            'games_lost': current_user.games_lost,
            'games_drawn': current_user.games_drawn
        }
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update authenticated user profile data"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    allowed_fields = ['username', 'email']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    # Check if username already exists
    if 'username' in update_data and update_data['username'] != current_user.username:
        if User.get_by_username(update_data['username']):
            return jsonify({'error': 'Username already exists'}), 409
    
    # Check if email already exists
    if 'email' in update_data and update_data['email'] != current_user.email:
        if User.get_by_email(update_data['email']):
            return jsonify({'error': 'Email already exists'}), 409
    
    try:
        current_user.update(**update_data)
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update profile'}), 500