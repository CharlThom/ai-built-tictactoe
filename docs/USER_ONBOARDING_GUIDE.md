# TicTacToe User Onboarding Guide

## Welcome to TicTacToe!

This guide will help you get started with playing TicTacToe through our API.

## Quick Start Tutorial

### Step 1: Start a New Game

To begin playing, create a new game session:

bash
curl -X POST http://localhost:8000/game/restart \
  -H "Content-Type: application/json"


**Response:**

{
  "game_id": "abc123",
  "board": ["", "", "", "", "", "", "", "", ""],
  "current_player": "X",
  "status": "in_progress",
  "message": "Game started! Player X's turn"
}


### Step 2: Understanding the Game Board

The board is represented as a 9-element array, indexed 0-8:


 0 | 1 | 2
-----------
 3 | 4 | 5
-----------
 6 | 7 | 8


### Step 3: Making Your First Move

Player X always goes first. Make a move by specifying the position (0-8):

bash
curl -X POST http://localhost:8000/game/move \
  -H "Content-Type: application/json" \
  -d '{"position": 4, "player": "X"}'


**Response:**

{
  "game_id": "abc123",
  "board": ["", "", "", "", "X", "", "", "", ""],
  "current_player": "O",
  "status": "in_progress",
  "message": "Move accepted. Player O's turn"
}


### Step 4: Understanding Turn Indicators

**Current Player Field:**
- The `current_player` field shows whose turn it is
- Always check this before making a move
- Attempting to move out of turn returns a 400 error

**Turn Flow:**
1. X moves → `current_player` becomes "O"
2. O moves → `current_player` becomes "X"
3. Repeat until game ends

### Step 5: Checking Game State

At any time, retrieve the current game state:

bash
curl -X GET http://localhost:8000/game/state


**Response:**

{
  "game_id": "abc123",
  "board": ["", "", "", "", "X", "", "", "O", ""],
  "current_player": "X",
  "status": "in_progress",
  "moves_count": 2
}


### Step 6: Game Status Indicators

The `status` field indicates the game state:

- **`in_progress`**: Game is ongoing, continue playing
- **`won`**: A player has won (check `winner` field)
- **`draw`**: All positions filled, no winner

**Winning Example:**

{
  "board": ["X", "X", "X", "O", "O", "", "", "", ""],
  "status": "won",
  "winner": "X",
  "winning_line": [0, 1, 2],
  "message": "Player X wins!"
}


**Draw Example:**

{
  "board": ["X", "O", "X", "X", "O", "O", "O", "X", "X"],
  "status": "draw",
  "message": "Game ended in a draw"
}


### Step 7: Restarting the Game

When a game ends or you want to start over:

bash
curl -X POST http://localhost:8000/game/restart \
  -H "Content-Type: application/json"


This resets the board and starts a fresh game with Player X.

## UI Controls Reference

### Making Moves
- **Endpoint:** `POST /game/move`
- **Required Fields:** `position` (0-8), `player` ("X" or "O")
- **Validation:** Position must be empty and it must be your turn

### Viewing Game State
- **Endpoint:** `GET /game/state`
- **No Parameters Required**
- **Use Case:** Check board state, current player, and game status

### Restarting Game
- **Endpoint:** `POST /game/restart`
- **No Parameters Required**
- **Effect:** Clears board, resets to Player X's turn

## Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Invalid move (position taken or wrong turn) | Check game state and try valid position |
| 404 | Game not found | Start a new game with `/game/restart` |
| 422 | Invalid position (not 0-8) | Use position between 0 and 8 |

## Complete Game Example

bash
# Start game
curl -X POST http://localhost:8000/game/restart

# X moves to center (position 4)
curl -X POST http://localhost:8000/game/move -d '{"position": 4, "player": "X"}'

# O moves to top-left (position 0)
curl -X POST http://localhost:8000/game/move -d '{"position": 0, "player": "O"}'

# X moves to top-center (position 1)
curl -X POST http://localhost:8000/game/move -d '{"position": 1, "player": "X"}'

# O moves to bottom-left (position 6)
curl -X POST http://localhost:8000/game/move -d '{"position": 6, "player": "O"}'

# X moves to bottom-center (position 7) - WINS!
curl -X POST http://localhost:8000/game/move -d '{"position": 7, "player": "X"}'
# Response: {"status": "won", "winner": "X", "winning_line": [1, 4, 7]}


## Best Practices

1. **Always check `current_player`** before making a move
2. **Handle error responses** gracefully in your client
3. **Check `status` field** after each move to detect game end
4. **Use `winning_line`** to highlight winning positions in UI
5. **Call `/game/restart`** to begin a new game after completion

## Tips for Success

- The API validates all moves automatically
- You cannot overwrite existing moves
- The game detects wins and draws automatically
- Player X always starts first after restart
- Game state persists until explicitly restarted

## Next Steps

Now that you understand the basics:
1. Try playing a complete game using the API
2. Experiment with different move sequences
3. Test error handling by making invalid moves
4. Build a UI client that consumes these endpoints

For detailed API specifications, see the [API Reference Documentation](./API_REFERENCE.md).
