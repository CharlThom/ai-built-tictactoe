# TicTacToe Game Logic Algorithm Documentation

## Win/Draw Detection Algorithm

### Overview
The game engine evaluates win conditions after each move by checking all possible winning combinations and determines draw conditions when the board is full with no winner.

### Win Detection Algorithm

#### Winning Combinations
There are 8 possible winning combinations in a 3x3 TicTacToe grid:
- 3 horizontal rows: [0,1,2], [3,4,5], [6,7,8]
- 3 vertical columns: [0,3,6], [1,4,7], [2,5,8]
- 2 diagonals: [0,4,8], [2,4,6]

#### Algorithm Steps

1. After each move, iterate through all 8 winning combinations
2. For each combination, check if all three positions contain the same non-empty symbol
3. If match found:
   - Set game status to 'finished'
   - Set winner to the matching symbol ('X' or 'O')
   - Return win result with winning combination indices
4. If no match found, proceed to draw detection


#### Pseudocode
python
WINNING_COMBINATIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
    [0, 4, 8], [2, 4, 6]              # diagonals
]

def check_winner(board):
    for combination in WINNING_COMBINATIONS:
        [a, b, c] = combination
        if board[a] and board[a] == board[b] == board[c]:
            return {
                'winner': board[a],
                'winning_combination': combination
            }
    return None


### Draw Detection Algorithm

#### Algorithm Steps

1. Check if all 9 board positions are filled (no null/empty values)
2. Verify no winner exists (win detection returned None)
3. If both conditions met:
   - Set game status to 'finished'
   - Set winner to null
   - Set result to 'draw'


#### Pseudocode
python
def check_draw(board):
    return all(cell is not None for cell in board)

def evaluate_game_state(board):
    win_result = check_winner(board)
    if win_result:
        return {'status': 'finished', 'result': 'win', **win_result}
    
    if check_draw(board):
        return {'status': 'finished', 'result': 'draw', 'winner': None}
    
    return {'status': 'in_progress', 'result': None, 'winner': None}


### Time Complexity
- Win Detection: O(1) - Always checks exactly 8 combinations
- Draw Detection: O(1) - Always checks exactly 9 positions
- Overall: O(1) constant time

### Space Complexity
- O(1) - Fixed size arrays and variables

---

## Game Status Response Codes

### HTTP Status Codes

| Status Code | Scenario | Description |
|-------------|----------|-------------|
| `200 OK` | Successful move | Move was valid and processed successfully |
| `200 OK` | Game state retrieved | Successfully retrieved current game state |
| `201 Created` | New game created | New game session created successfully |
| `400 Bad Request` | Invalid move | Move validation failed (see error codes below) |
| `404 Not Found` | Game not found | Requested game ID does not exist |
| `409 Conflict` | Game already finished | Attempted move on completed game |
| `422 Unprocessable Entity` | Invalid input format | Request body schema validation failed |
| `500 Internal Server Error` | Server error | Unexpected server-side error |

### Game Status Values

| Status | Description | Possible Next Actions |
|--------|-------------|----------------------|
| `in_progress` | Game is active and awaiting next move | POST /game/move |
| `finished` | Game has ended (win or draw) | POST /game/restart, POST /game/new |
| `waiting` | Waiting for second player (multiplayer) | N/A - wait for player join |

### Game Result Values

| Result | Description | Winner Field |
|--------|-------------|-------------|
| `win` | A player has won | `"X"` or `"O"` |
| `draw` | Board full, no winner | `null` |
| `null` | Game still in progress | `null` |

### Move Validation Error Codes

Returned in response body with 400 status:


{
  "error": "ERROR_CODE",
  "message": "Human readable description",
  "details": {}
}


| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_POSITION` | 400 | Position must be 0-8 |
| `POSITION_OCCUPIED` | 400 | Cell already contains X or O |
| `NOT_YOUR_TURN` | 400 | Wrong player attempting move |
| `GAME_FINISHED` | 409 | Game already ended |
| `INVALID_PLAYER` | 400 | Player symbol must be X or O |
| `GAME_NOT_FOUND` | 404 | Game ID does not exist |
| `INVALID_GAME_STATE` | 500 | Corrupted game state detected |

### Example Response Payloads

#### Successful Move (Win)

{
  "status": "finished",
  "result": "win",
  "winner": "X",
  "winning_combination": [0, 1, 2],
  "board": ["X", "X", "X", "O", "O", null, null, null, null],
  "current_player": null,
  "move_count": 5
}


#### Successful Move (Draw)

{
  "status": "finished",
  "result": "draw",
  "winner": null,
  "winning_combination": null,
  "board": ["X", "O", "X", "X", "O", "O", "O", "X", "X"],
  "current_player": null,
  "move_count": 9
}


#### Successful Move (In Progress)

{
  "status": "in_progress",
  "result": null,
  "winner": null,
  "winning_combination": null,
  "board": ["X", "O", null, null, null, null, null, null, null],
  "current_player": "X",
  "move_count": 2
}


#### Error Response (Position Occupied)

{
  "error": "POSITION_OCCUPIED",
  "message": "Position 4 is already occupied by O",
  "details": {
    "position": 4,
    "occupied_by": "O"
  }
}


#### Error Response (Game Finished)

{
  "error": "GAME_FINISHED",
  "message": "Cannot make move on finished game",
  "details": {
    "game_status": "finished",
    "winner": "X",
    "result": "win"
  }
}


### State Transition Diagram


[New Game]
    |
    v
[in_progress] --move--> [in_progress] (continue)
    |                         |
    |--win detected-->   [finished: win]
    |                         |
    |--draw detected-->  [finished: draw]
    |
    v
[restart] --> [in_progress]


### Integration Notes

1. **Always check game status** before allowing moves
2. **Validate winner field** matches result type (win = X/O, draw = null)
3. **winning_combination** is only populated when result is 'win'
4. **current_player** is null when game is finished
5. **move_count** increments with each valid move (max 9)
6. Client should disable move input when status is 'finished'
7. Poll GET /game/state for multiplayer synchronization
