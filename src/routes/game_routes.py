from flask import Blueprint, request, jsonify, g
from src.middleware.auth_middleware import token_required, optional_token
from src.models.game import Game
from src.models.user import User
from src.extensions import db
from datetime import datetime

game_bp = Blueprint('game', __name__, url_prefix='/api/games')


@game_bp.route('', methods=['POST'])
@token_required
def create_game():
    """Create a new TicTacToe game (protected endpoint)"""
    try:
        data = request.get_json() or {}
        
        # Create new game with current user as player1
        game = Game(
            player1_id=g.user_id,
            board_state='         ',  # 9 empty spaces
            current_turn='X',
            status='waiting',
            created_at=datetime.utcnow()
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'message': 'Game created successfully',
            'game': {
                'id': game.id,
                'player1_id': game.player1_id,
                'player2_id': game.player2_id,
                'board_state': game.board_state,
                'current_turn': game.current_turn,
                'status': game.status,
                'created_at': game.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@game_bp.route('/<int:game_id>/join', methods=['POST'])
@token_required
def join_game(game_id):
    """Join an existing game as player2 (protected endpoint)"""
    try:
        game = Game.query.get(game_id)
        
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        if game.status != 'waiting':
            return jsonify({'error': 'Game is not available to join'}), 400
        
        if game.player1_id == g.user_id:
            return jsonify({'error': 'Cannot join your own game'}), 400
        
        if game.player2_id:
            return jsonify({'error': 'Game is already full'}), 400
        
        game.player2_id = g.user_id
        game.status = 'in_progress'
        game.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Joined game successfully',
            'game': {
                'id': game.id,
                'player1_id': game.player1_id,
                'player2_id': game.player2_id,
                'board_state': game.board_state,
                'current_turn': game.current_turn,
                'status': game.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@game_bp.route('/<int:game_id>', methods=['GET'])
@token_required
def get_game(game_id):
    """Get game details (protected endpoint)"""
    try:
        game = Game.query.get(game_id)
        
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        # Check if user is part of the game
        if game.player1_id != g.user_id and game.player2_id != g.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'game': {
                'id': game.id,
                'player1_id': game.player1_id,
                'player2_id': game.player2_id,
                'board_state': game.board_state,
                'current_turn': game.current_turn,
                'status': game.status,
                'winner_id': game.winner_id,
                'created_at': game.created_at.isoformat(),
                'updated_at': game.updated_at.isoformat() if game.updated_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/<int:game_id>/move', methods=['POST'])
@token_required
def make_move(game_id):
    """Make a move in the game (protected endpoint)"""
    try:
        data = request.get_json()
        position = data.get('position')
        
        if position is None or not (0 <= position <= 8):
            return jsonify({'error': 'Invalid position. Must be 0-8'}), 400
        
        game = Game.query.get(game_id)
        
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        if game.status != 'in_progress':
            return jsonify({'error': 'Game is not in progress'}), 400
        
        # Verify it's the player's turn
        if (game.current_turn == 'X' and game.player1_id != g.user_id) or \
           (game.current_turn == 'O' and game.player2_id != g.user_id):
            return jsonify({'error': 'Not your turn'}), 403
        
        # Check if position is empty
        board = list(game.board_state)
        if board[position] != ' ':
            return jsonify({'error': 'Position already taken'}), 400
        
        # Make the move
        board[position] = game.current_turn
        game.board_state = ''.join(board)
        game.current_turn = 'O' if game.current_turn == 'X' else 'X'
        game.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Move made successfully',
            'game': {
                'id': game.id,
                'board_state': game.board_state,
                'current_turn': game.current_turn,
                'status': game.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@game_bp.route('/my-games', methods=['GET'])
@token_required
def get_my_games():
    """Get all games for the authenticated user (protected endpoint)"""
    try:
        games = Game.query.filter(
            (Game.player1_id == g.user_id) | (Game.player2_id == g.user_id)
        ).order_by(Game.created_at.desc()).all()
        
        return jsonify({
            'games': [{
                'id': game.id,
                'player1_id': game.player1_id,
                'player2_id': game.player2_id,
                'status': game.status,
                'current_turn': game.current_turn,
                'winner_id': game.winner_id,
                'created_at': game.created_at.isoformat()
            } for game in games]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500