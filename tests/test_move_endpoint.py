import pytest
import json
from src.app import app, games

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    games.clear()

def test_make_valid_move(client):
    # Create a game
    response = client.post('/game')
    game_id = response.get_json()['id']
    
    # Make a move
    response = client.post(f'/game/{game_id}/move',
                          data=json.dumps({'position': 0, 'player': 'X'}),
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['board'][0] == 'X'
    assert data['current_player'] == 'O'

def test_invalid_position(client):
    response = client.post('/game')
    game_id = response.get_json()['id']
    
    response = client.post(f'/game/{game_id}/move',
                          data=json.dumps({'position': 10, 'player': 'X'}),
                          content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_occupied_position(client):
    response = client.post('/game')
    game_id = response.get_json()['id']
    
    client.post(f'/game/{game_id}/move',
               data=json.dumps({'position': 0, 'player': 'X'}),
               content_type='application/json')
    
    response = client.post(f'/game/{game_id}/move',
                          data=json.dumps({'position': 0, 'player': 'O'}),
                          content_type='application/json')
    assert response.status_code == 400
    assert 'occupied' in response.get_json()['error']

def test_wrong_turn(client):
    response = client.post('/game')
    game_id = response.get_json()['id']
    
    response = client.post(f'/game/{game_id}/move',
                          data=json.dumps({'position': 0, 'player': 'O'}),
                          content_type='application/json')
    assert response.status_code == 400
    assert 'turn' in response.get_json()['error'].lower()

def test_winning_game(client):
    response = client.post('/game')
    game_id = response.get_json()['id']
    
    # X wins with top row
    moves = [
        {'position': 0, 'player': 'X'},
        {'position': 3, 'player': 'O'},
        {'position': 1, 'player': 'X'},
        {'position': 4, 'player': 'O'},
        {'position': 2, 'player': 'X'}
    ]
    
    for move in moves:
        response = client.post(f'/game/{game_id}/move',
                              data=json.dumps(move),
                              content_type='application/json')
    
    data = response.get_json()
    assert data['status'] == 'completed'
    assert data['winner'] == 'X'

def test_draw_game(client):
    response = client.post('/game')
    game_id = response.get_json()['id']
    
    # Create a draw
    moves = [
        {'position': 0, 'player': 'X'},
        {'position': 1, 'player': 'O'},
        {'position': 2, 'player': 'X'},
        {'position': 4, 'player': 'O'},
        {'position': 3, 'player': 'X'},
        {'position': 5, 'player': 'O'},
        {'position': 7, 'player': 'X'},
        {'position': 6, 'player': 'O'},
        {'position': 8, 'player': 'X'}
    ]
    
    for move in moves:
        response = client.post(f'/game/{game_id}/move',
                              data=json.dumps(move),
                              content_type='application/json')
    
    data = response.get_json()
    assert data['status'] == 'draw'
    assert data['winner'] is None