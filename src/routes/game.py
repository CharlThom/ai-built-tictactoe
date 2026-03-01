from flask import Blueprint, jsonify, request
from src.models.game_state import GameState
from src.storage import game_storage

game_bp = Blueprint('game', __name__)

@game_bp.route('/game', methods=['POST'])
def create_game():
    """Initialize a new game session"""
    game = GameState()
    game_storage[game.id] = game
    return jsonify(game.to_dict()), 201

@game_bp.route('/game/<game_id>', methods=['GET'])
def get_game(game_id):
    """Retrieve current game state by ID"""
    game = game_storage.get(game_id)
    
    if game is None:
        return jsonify({
            'error': 'Game not found',
            'message': f'No game exists with ID: {game_id}'
        }), 404
    
    return jsonify(game.to_dict()), 200
