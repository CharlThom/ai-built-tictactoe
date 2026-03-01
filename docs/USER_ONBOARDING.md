# TicTacToe API - User Onboarding Guide

## Quick Start (5 Minutes)

### Step 1: Create a New Game

bash
curl -X POST https://api.tictactoe.example.com/game/new \
  -H "Content-Type: application/json" \
  -d '{"player_x": "Alice", "player_o": "Bob"}'


**Response:**

{
  "game_id": "abc123",
  "status": "in_progress",
  "current_player": "X",
  "board": [null, null, null, null, null, null, null, null, null]
}


**Save the `game_id`** - you'll need it for all subsequent requests!

### Step 2: Make Your First Move

Board positions are numbered 0-8:

0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8


Player X moves to center (position 4):

bash
curl -X POST https://api.tictactoe.example.com/game/move \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "abc123",
    "player": "X",
    "position": 4
  }'


**Response:**

{
  "status": "in_progress",
  "current_player": "O",
  "board": [null, null, null, null, "X", null, null, null, null],
  "move_count": 1
}


### Step 3: Continue Playing

Player O makes a move:

bash
curl -X POST https://api.tictactoe.example.com/game/move \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "abc123",
    "player": "O",
    "position": 0
  }'


### Step 4: Check Game State Anytime

bash
curl https://api.tictactoe.example.com/game/state/abc123


### Step 5: Winning the Game

When a player wins:


{
  "status": "finished",
  "result": "win",
  "winner": "X",
  "winning_combination": [0, 1, 2],
  "board": ["X", "X", "X", "O", "O", null, null, null, null]
}


### Step 6: Restart or New Game

**Restart same game:**
bash
curl -X POST https://api.tictactoe.example.com/game/restart \
  -H "Content-Type: application/json" \
  -d '{"game_id": "abc123"}'


**Start new game:**
Repeat Step 1

---

## Understanding Game Status & Results

### Game Status Flow

1. **in_progress**: Game is active, players can make moves
2. **finished**: Game ended (someone won or draw)

### Result Types

- **null**: Game still in progress
- **win**: A player won (check `winner` field for "X" or "O")
- **draw**: Board full, no winner

### Reading the Board

The board is an array of 9 elements:
- `null` = empty cell
- `"X"` = X player's mark
- `"O"` = O player's mark


["X", "O", "X",
 "O", "X", null,
 null, null, "O"]


Visually:

X | O | X
---------
O | X | .
---------
. | . | O


---

## Common Error Scenarios

### Error 1: Position Already Occupied

**Request:**

{"game_id": "abc123", "player": "O", "position": 4}


**Response (400):**

{
  "error": "POSITION_OCCUPIED",
  "message": "Position 4 is already occupied by X"
}


**Solution:** Choose a different position (one with `null` value)

### Error 2: Not Your Turn

**Response (400):**

{
  "error": "NOT_YOUR_TURN",
  "message": "It is currently X's turn"
}


**Solution:** Check `current_player` field before making move

### Error 3: Game Already Finished

**Response (409):**

{
  "error": "GAME_FINISHED",
  "message": "Cannot make move on finished game"
}


**Solution:** Restart the game or create a new one

### Error 4: Invalid Position

**Response (400):**

{
  "error": "INVALID_POSITION",
  "message": "Position must be between 0 and 8"
}


**Solution:** Use positions 0-8 only

---

## Complete API Reference

### Endpoint Summary

| Method | Endpoint | Purpose |
|--------|----------|----------|
| POST | `/game/new` | Create new game |
| GET | `/game/state/{game_id}` | Get current game state |
| POST | `/game/move` | Make a move |
| POST | `/game/restart` | Restart existing game |

### Detailed Endpoints

#### POST /game/new

Create a new game session.

**Request Body:**

{
  "player_x": "Alice",  // optional
  "player_o": "Bob"     // optional
}


**Response (201):**

{
  "game_id": "abc123",
  "status": "in_progress",
  "current_player": "X",
  "board": [null, null, null, null, null, null, null, null, null],
  "player_x": "Alice",
  "player_o": "Bob"
}


#### GET /game/state/{game_id}

Retrieve current game state.

**Response (200):**

{
  "game_id": "abc123",
  "status": "in_progress",
  "result": null,
  "winner": null,
  "current_player": "X",
  "board": ["X", "O", null, null, null, null, null, null, null],
  "move_count": 2
}


#### POST /game/move

Make a move in the game.

**Request Body:**

{
  "game_id": "abc123",
  "player": "X",
  "position": 4
}


**Response (200):**

{
  "status": "in_progress",
  "current_player": "O",
  "board": [null, null, null, null, "X", null, null, null, null],
  "move_count": 1
}


#### POST /game/restart

Restart an existing game (clears board, resets to X's turn).

**Request Body:**

{
  "game_id": "abc123"
}


**Response (200):**

{
  "game_id": "abc123",
  "status": "in_progress",
  "current_player": "X",
  "board": [null, null, null, null, null, null, null, null, null],
  "move_count": 0
}


---

## Best Practices

### 1. Always Validate Current Player
javascript
if (gameState.current_player === myPlayer) {
  // Allow move
} else {
  // Disable move input
}


### 2. Check Game Status Before Moves
javascript
if (gameState.status === 'finished') {
  // Show restart option
  // Disable move input
}


### 3. Handle All Error Codes
javascript
try {
  const response = await makeMove(gameId, player, position);
} catch (error) {
  switch (error.code) {
    case 'POSITION_OCCUPIED':
      alert('That spot is taken!');
      break;
    case 'NOT_YOUR_TURN':
      alert('Wait for your turn!');
      break;
    // ... handle other errors
  }
}


### 4. Display Winning Combination
javascript
if (gameState.result === 'win') {
  highlightCells(gameState.winning_combination);
  showMessage(`${gameState.winner} wins!`);
}


### 5. Poll for Multiplayer Updates
javascript
// Poll every 2 seconds for opponent's move
setInterval(async () => {
  const state = await getGameState(gameId);
  updateBoard(state.board);
}, 2000);


---

## Example: Complete Game Flow

javascript
// 1. Create game
const game = await fetch('/game/new', {
  method: 'POST',
  body: JSON.stringify({player_x: 'Alice', player_o: 'Bob'})
}).then(r => r.json());

const gameId = game.game_id;

// 2. Make moves
await fetch('/game/move', {
  method: 'POST',
  body: JSON.stringify({game_id: gameId, player: 'X', position: 4})
});

await fetch('/game/move', {
  method: 'POST',
  body: JSON.stringify({game_id: gameId, player: 'O', position: 0})
});

// 3. Check state
const state = await fetch(`/game/state/${gameId}`).then(r => r.json());

if (state.status === 'finished') {
  console.log(`Game over! Winner: ${state.winner || 'Draw'}`);
}

// 4. Restart
await fetch('/game/restart', {
  method: 'POST',
  body: JSON.stringify({game_id: gameId})
});


---

## Troubleshooting

**Q: My move returns "NOT_YOUR_TURN" but I'm sure it's my turn**

A: Always fetch the latest game state before making a move. The `current_player` field tells you whose turn it is.

**Q: How do I know if someone won?**

A: Check if `status === 'finished'` and `result === 'win'`. The `winner` field will be "X" or "O".

**Q: Can I undo a move?**

A: No, moves are final. Use `/game/restart` to start over.

**Q: What happens if I try to move on a finished game?**

A: You'll receive a 409 error with code "GAME_FINISHED". Restart or create a new game.

**Q: How long do game sessions last?**

A: Game sessions persist until explicitly deleted or after 24 hours of inactivity (implementation dependent).

---

## Next Steps

1. ✅ Read this onboarding guide
2. ✅ Try the Quick Start example
3. 📖 Review [GAME_LOGIC_ALGORITHM.md](./GAME_LOGIC_ALGORITHM.md) for detailed algorithm documentation
4. 🔧 Integrate the API into your application
5. 🎮 Build your UI with proper error handling
6. 🚀 Deploy and play!

## Support

For issues or questions:
- API Documentation: `/docs/api`
- GitHub Issues: `github.com/yourorg/tictactoe/issues`
- Email: support@tictactoe.example.com
