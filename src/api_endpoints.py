from flask import Flask, request, jsonify
from src.api_security import (
    limiter, validate_request, secure_headers,
    check_sql_injection, check_nosql_injection
)

app = Flask(__name__)
limiter.init_app(app)


@app.route('/api/game/create', methods=['POST'])
@limiter.limit("10 per minute")
@secure_headers
@validate_request('player_name')
def create_game():
    """Create a new game with validated input."""
    data = request.validated_data
    
    # Additional injection checks
    if check_sql_injection(data['player_name']):
        return jsonify({'error': 'Invalid input detected'}), 400
    
    # Game creation logic here
    return jsonify({
        'game_id': 'generated-uuid',
        'player_name': data['player_name'],
        'status': 'created'
    }), 201


@app.route('/api/game/<game_id>/move', methods=['POST'])
@limiter.limit("30 per minute")
@secure_headers
@validate_request('game_id', 'position', 'token')
def make_move(game_id):
    """Make a move with validated game_id and position."""
    data = request.validated_data
    
    # Validate game_id from URL matches body
    if data['game_id'] != game_id:
        return jsonify({'error': 'Game ID mismatch'}), 400
    
    # Check for injection attempts
    if check_nosql_injection(data):
        return jsonify({'error': 'Invalid input detected'}), 400
    
    position = int(data['position'])
    
    # Move logic here
    return jsonify({
        'game_id': game_id,
        'position': position,
        'status': 'move_accepted'
    }), 200


@app.route('/api/game/<game_id>/state', methods=['GET'])
@limiter.limit("60 per minute")
@secure_headers
def get_game_state(game_id):
    """Get game state with validated game_id."""
    is_valid, error_msg = validate_input('game_id', game_id)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # State retrieval logic here
    return jsonify({
        'game_id': game_id,
        'board': [None] * 9,
        'current_player': 'X',
        'status': 'in_progress'
    }), 200


@app.route('/api/player/join', methods=['POST'])
@limiter.limit("5 per minute")
@secure_headers
@validate_request('player_name', 'game_id')
def join_game():
    """Join existing game with validation."""
    data = request.validated_data
    
    # Injection prevention
    for field in ['player_name', 'game_id']:
        if check_sql_injection(data[field]):
            return jsonify({'error': 'Invalid input detected'}), 400
    
    # Join logic here
    return jsonify({
        'game_id': data['game_id'],
        'player_name': data['player_name'],
        'status': 'joined'
    }), 200


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded errors."""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429


@app.errorhandler(400)
def bad_request_handler(e):
    """Handle bad request errors."""
    return jsonify({
        'error': 'Bad request',
        'message': str(e)
    }), 400