# TicTacToe API - Quick Start Guide

Welcome to the TicTacToe API! This guide will help you get started with integrating the game into your application.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Creating Your First Game](#creating-your-first-game)
3. [Making Moves](#making-moves)
4. [Checking Game State](#checking-game-state)
5. [Restarting a Game](#restarting-a-game)
6. [Complete Game Flow Example](#complete-game-flow-example)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- API Base URL: `https://api.tictactoe.example.com/v1`
- Content-Type: `application/json`
- Basic understanding of REST APIs
- HTTP client (curl, Postman, or your preferred programming language)

---

## Creating Your First Game

Before you can play, you need to create a game. The game will be assigned a unique `game_id`.

**Note:** Game creation endpoint is assumed to be `POST /game/create` (implement separately)

bash
curl -X POST https://api.tictactoe.example.com/v1/game/create \
  -H "Content-Type: application/json" \
  -d '{}'


**Response:**

{
  "game_id": "550e8400-e29b-41d4-a716-446655440000",
  "board": [null, null, null, null, null, null, null, null, null],
  "current_player": "X",
  "status": "in_progress"
}


**Save the `game_id`** - you'll need it for all subsequent requests!

---

## Making Moves

To make a move, use the `POST /game/move` endpoint.

### Understanding the Board

The board has 9 positions numbered 0-8:


 0 | 1 | 2
-----------
 3 | 4 | 5
-----------
 6 | 7 | 8


### Example: Player X moves to center (position 4)

bash
curl -X POST https://api.tictactoe.example.com/v1/game/move \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "550e8400-e29b-41d4-a716-446655440000",
    "position": 4,
    "player": "X"
  }'


**Response:**

{
  "success": true,
  "game_state": {
    "game_id": "550e8400-e29b-41d4-a716-446655440000",
    "board": [null, null, null, null, "X", null, null, null, null],
    "current_player": "O",
    "status": "in_progress",
    "winner": null,
    "move_count": 1
  }
}


### Example: Player O moves to top-left (position 0)

bash
curl -X POST https://api.tictactoe.example.com/v1/game/move \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "550e8400-e29b-41d4-a716-446655440000",
    "position": 0,
    "player": "O"
  }'


---

## Checking Game State

At any time, you can check the current state of the game:

bash
curl -X GET "https://api.tictactoe.example.com/v1/game/state?game_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json"


**Response:**

{
  "game_id": "550e8400-e29b-41d4-a716-446655440000",
  "board": ["O", null, null, null, "X", null, null, null, null],
  "current_player": "X",
  "status": "in_progress",
  "winner": null,
  "winning_line": null,
  "move_count": 2
}


---

## Restarting a Game

When a game ends, you can restart it with the same `game_id`:

bash
curl -X POST https://api.tictactoe.example.com/v1/game/restart \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "550e8400-e29b-41d4-a716-446655440000",
    "starting_player": "X"
  }'


**Response:**

{
  "success": true,
  "game_state": {
    "game_id": "550e8400-e29b-41d4-a716-446655440000",
    "board": [null, null, null, null, null, null, null, null, null],
    "current_player": "X",
    "status": "in_progress",
    "winner": null,
    "move_count": 0
  }
}


---

## Complete Game Flow Example

Here's a complete game from start to finish using Python:

python
import requests
import json

BASE_URL = "https://api.tictactoe.example.com/v1"

# 1. Create a new game
response = requests.post(f"{BASE_URL}/game/create")
game_data = response.json()
game_id = game_data["game_id"]
print(f"Game created: {game_id}")

# 2. Make moves
moves = [
    {"player": "X", "position": 0},  # X: top-left
    {"player": "O", "position": 4},  # O: center
    {"player": "X", "position": 1},  # X: top-middle
    {"player": "O", "position": 3},  # O: middle-left
    {"player": "X", "position": 2},  # X: top-right (wins!)
]

for move in moves:
    response = requests.post(
        f"{BASE_URL}/game/move",
        json={
            "game_id": game_id,
            "position": move["position"],
            "player": move["player"]
        }
    )
    result = response.json()
    
    if result["game_state"]["status"] == "won":
        print(f"Player {result['game_state']['winner']} wins!")
        print(f"Winning line: {result['game_state']['winning_line']}")
        break
    elif result["game_state"]["status"] == "draw":
        print("Game ended in a draw!")
        break

# 3. Restart the game
response = requests.post(
    f"{BASE_URL}/game/restart",
    json={"game_id": game_id, "starting_player": "O"}
)
print("Game restarted!")


---

## Best Practices

### 1. Always Check Current Player
Before making a move, verify it's the correct player's turn:

python
state = requests.get(f"{BASE_URL}/game/state?game_id={game_id}").json()
if state["current_player"] == player:
    # Make move
    pass


### 2. Handle Errors Gracefully

python
response = requests.post(f"{BASE_URL}/game/move", json=move_data)

if response.status_code == 400:
    error = response.json()
    if error["error"] == "invalid_move":
        print("Position already occupied!")
    elif error["error"] == "wrong_turn":
        print("Not your turn!")
else:
    # Process successful move
    pass


### 3. Check Game Status After Each Move

python
result = requests.post(f"{BASE_URL}/game/move", json=move_data).json()

if result["game_state"]["status"] == "won":
    winner = result["game_state"]["winner"]
    print(f"Game over! {winner} wins!")
elif result["game_state"]["status"] == "draw":
    print("Game over! It's a draw!")


### 4. Store game_id Persistently
If your application needs to resume games later, store the `game_id` in a database or local storage.

---

## Troubleshooting

### Error: "Position already occupied"
**Cause:** Trying to place a mark on a position that already has X or O.
**Solution:** Check the board state before making a move.

### Error: "It is player X's turn"
**Cause:** Wrong player attempting to move.
**Solution:** Always check `current_player` from the game state.

### Error: "Game has already ended"
**Cause:** Attempting to make a move after the game is won or drawn.
**Solution:** Use `POST /game/restart` to start a new game.

### Error: "Game not found"
**Cause:** Invalid or expired `game_id`.
**Solution:** Create a new game using the create endpoint.

---

## Next Steps

1. **Explore Advanced Features:** Check the full API documentation for additional endpoints
2. **Implement AI Opponent:** Use the API to build a computer player
3. **Add Multiplayer:** Build real-time multiplayer using WebSockets (if available)
4. **Track Statistics:** Implement win/loss tracking for players

---

## Support

For additional help:
- Full API Documentation: `/docs/api/game-endpoints.md`
- Report Issues: [GitHub Issues](https://github.com/example/tictactoe-api/issues)
- Email Support: support@tictactoe.example.com

Happy coding! 🎮