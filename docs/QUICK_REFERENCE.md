# TicTacToe Quick Reference Card

## API Endpoints

### Start/Restart Game

POST /game/restart
→ Returns fresh game state with empty board


### Make a Move

POST /game/move
Body: {"position": 0-8, "player": "X"|"O"}
→ Returns updated game state


### Get Game State

GET /game/state
→ Returns current game state


## Board Layout

 0 | 1 | 2
-----------
 3 | 4 | 5
-----------
 6 | 7 | 8


## Turn Indicators

| Field | Description |
|-------|-------------|
| `current_player` | "X" or "O" - whose turn it is |
| `status` | "in_progress", "won", or "draw" |
| `winner` | "X" or "O" (only when status is "won") |
| `winning_line` | Array of 3 positions forming winning line |

## Game Status Flow


[Start] → in_progress → [Moves] → in_progress → [Win/Draw]
                                                      ↓
                                              won OR draw
                                                      ↓
                                                  [Restart]


## Response Examples

### In Progress

{
  "current_player": "X",
  "status": "in_progress",
  "board": ["", "O", "", "", "X", "", "", "", ""]
}


### Player Wins

{
  "status": "won",
  "winner": "X",
  "winning_line": [0, 1, 2],
  "board": ["X", "X", "X", "O", "O", "", "", "", ""]
}


### Draw

{
  "status": "draw",
  "board": ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
}


## Error Codes

- **400**: Invalid move (position taken, wrong turn)
- **404**: Game not found
- **422**: Invalid input (position out of range)

## Restart Functionality

**When to Restart:**
- Game status is "won" or "draw"
- Want to start a new game

**Effect:**
- Clears all board positions
- Resets to Player X's turn
- Generates new game_id
- Sets status to "in_progress"

## Move Validation Rules

✓ Position must be 0-8
✓ Position must be empty
✓ Must be your turn (match `current_player`)
✓ Game status must be "in_progress"

## Winning Combinations


Rows:     [0,1,2] [3,4,5] [6,7,8]
Columns:  [0,3,6] [1,4,7] [2,5,8]
Diagonals:[0,4,8] [2,4,6]


## Integration Checklist

- [ ] Call `/game/restart` on app start
- [ ] Display `current_player` prominently
- [ ] Validate moves client-side before API call
- [ ] Handle all error responses
- [ ] Check `status` after each move
- [ ] Highlight `winning_line` when game won
- [ ] Show restart button when game ends
- [ ] Disable moves when status ≠ "in_progress"
