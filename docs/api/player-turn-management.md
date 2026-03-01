# Player Turn Management & Move Validation API Reference

## Overview
This document describes the API endpoints and logic for managing player turns and validating moves in the TicTacToe game.

## Base URL

http://localhost:8000/api/v1


## Endpoints

### Get Current Turn

**GET** `/game/{game_id}/turn`

Retrieve information about whose turn it is.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| game_id | string | Yes | Unique game identifier |

#### Response 200 (OK)

{
  "game_id": "abc123",
  "current_player": "X",
  "turn_number": 5,
  "is_game_over": false,
  "next_player": "O"
}


#### Response 404 (Not Found)

{
  "error": "Game not found",
  "game_id": "abc123"
}


---

### Validate Move

**POST** `/game/{game_id}/validate-move`

Validate a move without executing it.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| game_id | string | Yes | Unique game identifier |

#### Request Body

{
  "player": "X",
  "position": {
    "row": 1,
    "col": 1
  }
}


#### Request Schema
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| player | string | Yes | "X" or "O" | Player making the move |
| position.row | integer | Yes | 0-2 | Row index (0-based) |
| position.col | integer | Yes | 0-2 | Column index (0-based) |

#### Response 200 (Valid Move)

{
  "valid": true,
  "message": "Move is valid",
  "position": {
    "row": 1,
    "col": 1
  }
}


#### Response 200 (Invalid Move)

{
  "valid": false,
  "message": "Position already occupied",
  "error_code": "POSITION_OCCUPIED",
  "position": {
    "row": 1,
    "col": 1
  }
}


#### Response 400 (Bad Request)

{
  "error": "Invalid position coordinates",
  "error_code": "INVALID_COORDINATES",
  "details": "Row and column must be between 0 and 2"
}


---

### Switch Turn

**POST** `/game/{game_id}/switch-turn`

Manually switch turns (admin/testing only).

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| game_id | string | Yes | Unique game identifier |

#### Response 200 (OK)

{
  "game_id": "abc123",
  "previous_player": "X",
  "current_player": "O",
  "turn_number": 6
}


---

## Move Validation Rules

### 1. Position Validation
- **Rule**: Position must be within board boundaries (0-2 for both row and column)
- **Error Code**: `INVALID_COORDINATES`
- **HTTP Status**: 400

### 2. Position Occupancy
- **Rule**: Selected position must be empty
- **Error Code**: `POSITION_OCCUPIED`
- **HTTP Status**: 200 (valid=false)

### 3. Turn Order
- **Rule**: Player must match current turn
- **Error Code**: `NOT_YOUR_TURN`
- **HTTP Status**: 200 (valid=false)

### 4. Game State
- **Rule**: Game must not be finished (no winner or draw)
- **Error Code**: `GAME_ALREADY_FINISHED`
- **HTTP Status**: 200 (valid=false)

### 5. Player Identity
- **Rule**: Player must be either "X" or "O"
- **Error Code**: `INVALID_PLAYER`
- **HTTP Status**: 400

---

## Turn Management Logic

### Turn Sequence
1. Player "X" always starts first
2. Players alternate after each valid move
3. Turn counter increments with each move
4. Game ends when:
   - A player wins (3 in a row)
   - Board is full (draw)
   - Game is manually reset

### Turn State Transitions

Initial State: X's turn (turn_number: 1)
  ↓
Valid Move by X
  ↓
O's turn (turn_number: 2)
  ↓
Valid Move by O
  ↓
X's turn (turn_number: 3)
  ↓
... continues until game ends


---

## Error Codes Reference

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| INVALID_COORDINATES | Position outside 0-2 range | 400 |
| POSITION_OCCUPIED | Cell already has a mark | 200 |
| NOT_YOUR_TURN | Wrong player for current turn | 200 |
| GAME_ALREADY_FINISHED | Game has ended | 200 |
| INVALID_PLAYER | Player is not X or O | 400 |
| GAME_NOT_FOUND | Game ID doesn't exist | 404 |
| INVALID_GAME_STATE | Game state corrupted | 500 |

---

## Examples

### Example 1: Valid Move Sequence

bash
# Check current turn
curl -X GET http://localhost:8000/api/v1/game/abc123/turn

# Response
{
  "current_player": "X",
  "turn_number": 1
}

# Validate move
curl -X POST http://localhost:8000/api/v1/game/abc123/validate-move \
  -H "Content-Type: application/json" \
  -d '{"player": "X", "position": {"row": 0, "col": 0}}'

# Response
{
  "valid": true,
  "message": "Move is valid"
}

# Execute move (using existing POST /game/move endpoint)
curl -X POST http://localhost:8000/api/v1/game/move \
  -H "Content-Type: application/json" \
  -d '{"game_id": "abc123", "player": "X", "position": {"row": 0, "col": 0}}'


### Example 2: Invalid Move - Wrong Turn

bash
curl -X POST http://localhost:8000/api/v1/game/abc123/validate-move \
  -H "Content-Type: application/json" \
  -d '{"player": "O", "position": {"row": 1, "col": 1}}'

# Response (when it's X's turn)
{
  "valid": false,
  "message": "Not your turn",
  "error_code": "NOT_YOUR_TURN",
  "current_player": "X"
}


### Example 3: Invalid Move - Position Occupied

bash
curl -X POST http://localhost:8000/api/v1/game/abc123/validate-move \
  -H "Content-Type: application/json" \
  -d '{"player": "X", "position": {"row": 0, "col": 0}}'

# Response (position already taken)
{
  "valid": false,
  "message": "Position already occupied",
  "error_code": "POSITION_OCCUPIED",
  "occupied_by": "X"
}


---

## Integration Notes

### Client-Side Implementation
1. Always check current turn before allowing move
2. Validate move client-side first for better UX
3. Handle validation errors gracefully
4. Update UI based on turn state

### Server-Side Validation
All moves are validated server-side regardless of client validation:
1. Position bounds check
2. Position occupancy check
3. Turn order verification
4. Game state verification
5. Player identity verification

### Concurrency Handling
- Use optimistic locking for concurrent move attempts
- Return appropriate error if game state changed
- Implement retry logic on client side

---

## Rate Limiting

- **Validate Move**: 100 requests/minute per game
- **Get Turn**: 200 requests/minute per game
- **Switch Turn**: 10 requests/minute (admin only)

---

## Versioning

API Version: 1.0.0
Last Updated: 2024

For breaking changes, a new API version will be released under `/api/v2/`