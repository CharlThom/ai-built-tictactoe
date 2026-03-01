from flask import Blueprint, jsonify, request
from src.models.game_state import GameState, games_db

game_bp = Blueprint('game', __name__)

@game_bp.route('/game', methods=['POST'])
def create_game():
    game = GameState()
    games_db[game.id] = game
    return jsonify(game.to_dict()), 201

@game_bp.route('/game/<game_id>', methods=['GET'])
def get_game(game_id):
    game = games_db.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify(game.to_dict()), 200

@game_bp.route('/game/<game_id>/restart', methods=['PUT'])
def restart_game(game_id):
    game = games_db.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    game.restart()
    return jsonify(game.to_dict()), 200
