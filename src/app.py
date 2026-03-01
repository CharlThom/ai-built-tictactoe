from flask import Flask, request, jsonify
import uuid
from datetime import datetime

app = Flask(__name__)

# In-memory storage for game states
games = {}

class GameState:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.board = [None] * 9  # 3x3 board as flat array
        self.current_player = 'X'
        self.status = 'in_progress'  # in_progress, completed, draw
        self.winner = None
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'board': self.board,
            'current_player': self.current_player,
            'status': self.status,
            'winner': self.winner,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

@app.route('/game', methods=['POST'])
def create_game():
    game = GameState()
    games[game.id] = game
    return jsonify(game.to_dict()), 201

@app.route('/game/<game_id>', methods=['GET'])
def get_game(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify(game.to_dict()), 200

@app.route('/game/<game_id>/move', methods=['POST'])
def make_move(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    if game.status != 'in_progress':
        return jsonify({'error': 'Game is already finished'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    # Validate position
    position = data.get('position')
    if position is None:
        return jsonify({'error': 'Position is required'}), 400
    
    if not isinstance(position, int) or position < 0 or position > 8:
        return jsonify({'error': 'Position must be an integer between 0 and 8'}), 400
    
    # Validate player
    player = data.get('player')
    if not player:
        return jsonify({'error': 'Player is required'}), 400
    
    if player not in ['X', 'O']:
        return jsonify({'error': 'Player must be X or O'}), 400
    
    if player != game.current_player:
        return jsonify({'error': f'Not your turn. Current player is {game.current_player}'}), 400
    
    # Check if position is already occupied
    if game.board[position] is not None:
        return jsonify({'error': 'Position is already occupied'}), 400
    
    # Make the move
    game.board[position] = player
    game.updated_at = datetime.utcnow().isoformat()
    
    # Check for winner
    winner = check_winner(game.board)
    if winner:
        game.status = 'completed'
        game.winner = winner
    elif None not in game.board:
        game.status = 'draw'
    else:
        # Switch player
        game.current_player = 'O' if player == 'X' else 'X'
    
    return jsonify(game.to_dict()), 200

def check_winner(board):
    # Winning combinations
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    
    for combo in winning_combinations:
        if (board[combo[0]] is not None and
            board[combo[0]] == board[combo[1]] == board[combo[2]]):
            return board[combo[0]]
    
    return None

if __name__ == '__main__':
    app.run(debug=True, port=5000)