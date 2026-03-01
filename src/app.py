from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# In-memory storage for game sessions
games = {}

class GameState:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.board = [None, None, None, None, None, None, None, None, None]
        self.current_player = 'X'
        self.status = 'in_progress'
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
    """Initialize a new game session"""
    game = GameState()
    games[game.id] = game
    
    return jsonify({
        'success': True,
        'game': game.to_dict()
    }), 201

@app.route('/game/<game_id>', methods=['GET'])
def get_game(game_id):
    """Retrieve game state by ID"""
    game = games.get(game_id)
    
    if not game:
        return jsonify({
            'success': False,
            'error': 'Game not found'
        }), 404
    
    return jsonify({
        'success': True,
        'game': game.to_dict()
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)