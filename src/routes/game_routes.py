from flask import Blueprint, request, jsonify, session
from src.middleware.csrf_protection import csrf, get_csrf_token
from src.models.game import Game
from src.utils.validators import validate_move_input
import logging

game_bp = Blueprint('game', __name__, url_prefix='/api/game')
logger = logging.getLogger(__name__)

# In-memory game storage (use database in production)
games = {}

@game_bp.route('/csrf-token', methods=['GET'])
def get_token():
    """Endpoint to retrieve CSRF token for the session"""
    try:
        token = get_csrf_token()
        return jsonify({
            'csrf_token': token,
            'session_id': session.get('session_id')
        }), 200
    except Exception as e:
        logger.error(f"Error generating CSRF token: {e}")
        return jsonify({'error': 'Failed to generate token'}), 500

@game_bp.route('/move', methods=['POST'])
@csrf.csrf_protect
def make_move():
    """Protected endpoint for making a game move"""
    try:
        data = request.get_json()
        
        # Validate input
        if not validate_move_input(data):
            return jsonify({'error': 'Invalid move data'}), 400
        
        game_id = data.get('game_id')
        position = data.get('position')
        player_id = session.get('player_id')
        
        if not player_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        game = games.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        # Server-side validation of move
        if not game.is_valid_move(position, player_id):
            return jsonify({'error': 'Invalid move'}), 400
        
        game.make_move(position, player_id)
        
        logger.info(f"Player {player_id} made move at position {position} in game {game_id}")
        
        return jsonify({
            'success': True,
            'game_state': game.get_state(),
            'csrf_token': get_csrf_token()  # Rotate token after action
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing move: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@game_bp.route('/restart', methods=['POST'])
@csrf.csrf_protect
def restart_game():
    """Protected endpoint for restarting a game"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        player_id = session.get('player_id')
        
        if not player_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        game = games.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        # Verify player is authorized to restart
        if not game.is_player(player_id):
            return jsonify({'error': 'Not authorized to restart this game'}), 403
        
        game.restart()
        
        logger.info(f"Player {player_id} restarted game {game_id}")
        
        return jsonify({
            'success': True,
            'game_state': game.get_state(),
            'csrf_token': get_csrf_token()  # Rotate token after action
        }), 200
        
    except Exception as e:
        logger.error(f"Error restarting game: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@game_bp.route('/surrender', methods=['POST'])
@csrf.csrf_protect
def surrender_game():
    """Protected endpoint for surrendering a game"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        player_id = session.get('player_id')
        
        if not player_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        game = games.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        if not game.is_player(player_id):
            return jsonify({'error': 'Not authorized'}), 403
        
        game.surrender(player_id)
        
        logger.info(f"Player {player_id} surrendered game {game_id}")
        
        return jsonify({
            'success': True,
            'game_state': game.get_state(),
            'csrf_token': get_csrf_token()
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing surrender: {e}")
        return jsonify({'error': 'Internal server error'}), 500