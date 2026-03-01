from flask import Flask, request, jsonify
from functools import wraps
import os
from game_state_validator import GameStateValidator

app = Flask(__name__)
validator = GameStateValidator(os.environ.get('GAME_SECRET_KEY', 'change-me-in-production'))

# In-memory game storage (use Redis/DB in production)
games = {}

def require_auth(f):
    """Decorator to require valid session token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token or not validate_session_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def validate_session_token(token: str) -> bool:
    """Validate session token (placeholder - implement with actual auth)"""
    # This should validate against your session store
    return len(token) > 0

def get_player_id_from_token(token: str) -> str:
    """Extract player ID from token (placeholder)"""
    # Implement actual token decoding
    return token.split(':')[0] if ':' in token else token

@app.route('/api/game/<game_id>/move', methods=['POST'])
@require_auth
def make_move(game_id: str):
    """Make a move with server-side validation"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    player_id = get_player_id_from_token(token)
    
    # Get game state
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    
    # Verify state hash to prevent tampering
    client_hash = request.json.get('state_hash')
    if client_hash and not validator.verify_state_hash(game, client_hash):
        return jsonify({'error': 'Game state tampered'}), 400
    
    # Determine player symbol
    if player_id == game['player_x_id']:
        player_symbol = 'X'
    elif player_id == game['player_o_id']:
        player_symbol = 'O'
    else:
        return jsonify({'error': 'Not a player in this game'}), 403
    
    # Get move coordinates
    row = request.json.get('row')
    col = request.json.get('col')
    
    if row is None or col is None:
        return jsonify({'error': 'Missing row or col'}), 400
    
    # Validate move
    valid, error = validator.validate_move(
        game['board'], row, col, player_symbol, game['current_player']
    )
    if not valid:
        return jsonify({'error': error}), 400
    
    # Apply move
    game['board'][row][col] = player_symbol
    game['move_count'] += 1
    
    # Validate board state after move
    valid, error = validator.validate_board_state(game['board'], game['move_count'])
    if not valid:
        # Rollback move
        game['board'][row][col] = ''
        game['move_count'] -= 1
        return jsonify({'error': f'Invalid state: {error}'}), 400
    
    # Check for winner or draw
    winner = validator.check_winner(game['board'])
    is_draw = validator.is_draw(game['board'])
    
    if winner:
        game['status'] = 'finished'
        game['winner'] = winner
    elif is_draw:
        game['status'] = 'draw'
    else:
        # Switch player
        game['current_player'] = 'O' if game['current_player'] == 'X' else 'X'
    
    # Create secure state response
    secure_state = validator.create_secure_game_state(
        game_id, game['board'], game['current_player'],
        game['move_count'], game['player_x_id'], game['player_o_id']
    )
    secure_state['status'] = game.get('status', 'active')
    secure_state['winner'] = game.get('winner')
    
    return jsonify(secure_state), 200

@app.route('/api/game/<game_id>/state', methods=['GET'])
@require_auth
def get_game_state(game_id: str):
    """Get current game state with integrity hash"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    secure_state = validator.create_secure_game_state(
        game_id, game['board'], game['current_player'],
        game['move_count'], game['player_x_id'], game['player_o_id']
    )
    secure_state['status'] = game.get('status', 'active')
    secure_state['winner'] = game.get('winner')
    
    return jsonify(secure_state), 200

if __name__ == '__main__':
    app.run(debug=False)