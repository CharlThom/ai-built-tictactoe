# Error Handling Documentation

## Overview
This document describes error handling for invalid moves, edge cases, and exceptional scenarios in the TicTacToe API.

## HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Game not found |
| 409 | Conflict - Invalid game state |
| 422 | Unprocessable Entity - Invalid move |
| 500 | Internal Server Error |

## Error Response Schema

All errors return a consistent JSON structure:


{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {},
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


## Invalid Move Errors

### 1. Cell Already Occupied
**Error Code:** `CELL_OCCUPIED`  
**HTTP Status:** 422  
**Trigger:** Player attempts to place mark in an already occupied cell

**Request:**

POST /game/move
{
  "game_id": "abc123",
  "player": "X",
  "position": {"row": 0, "col": 0}
}


**Response:**

{
  "error": {
    "code": "CELL_OCCUPIED",
    "message": "Cell at position (0,0) is already occupied",
    "details": {
      "position": {"row": 0, "col": 0},
      "occupied_by": "O"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


### 2. Out of Bounds Position
**Error Code:** `INVALID_POSITION`  
**HTTP Status:** 400  
**Trigger:** Position coordinates outside valid range (0-2)

**Request:**

POST /game/move
{
  "game_id": "abc123",
  "player": "X",
  "position": {"row": 5, "col": 2}
}


**Response:**

{
  "error": {
    "code": "INVALID_POSITION",
    "message": "Position must be within bounds (0-2 for row and col)",
    "details": {
      "provided": {"row": 5, "col": 2},
      "valid_range": {"min": 0, "max": 2}
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


### 3. Wrong Player Turn
**Error Code:** `WRONG_TURN`  
**HTTP Status:** 409  
**Trigger:** Player attempts move when it's not their turn

**Response:**

{
  "error": {
    "code": "WRONG_TURN",
    "message": "It is not player X's turn",
    "details": {
      "attempted_player": "X",
      "current_turn": "O"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


### 4. Game Already Finished
**Error Code:** `GAME_FINISHED`  
**HTTP Status:** 409  
**Trigger:** Move attempted after game has ended

**Response:**

{
  "error": {
    "code": "GAME_FINISHED",
    "message": "Cannot make move - game has already finished",
    "details": {
      "game_status": "won",
      "winner": "X"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


## Edge Cases

### 5. Game Not Found
**Error Code:** `GAME_NOT_FOUND`  
**HTTP Status:** 404  
**Trigger:** Invalid or expired game_id

**Response:**

{
  "error": {
    "code": "GAME_NOT_FOUND",
    "message": "Game with ID 'invalid123' does not exist",
    "details": {
      "game_id": "invalid123"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


### 6. Invalid Player Identifier
**Error Code:** `INVALID_PLAYER`  
**HTTP Status:** 400  
**Trigger:** Player value is not 'X' or 'O'

**Response:**

{
  "error": {
    "code": "INVALID_PLAYER",
    "message": "Player must be 'X' or 'O'",
    "details": {
      "provided": "Z",
      "valid_values": ["X", "O"]
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


### 7. Missing Required Fields
**Error Code:** `MISSING_FIELD`  
**HTTP Status:** 400  
**Trigger:** Required field missing from request

**Response:**

{
  "error": {
    "code": "MISSING_FIELD",
    "message": "Required field 'position' is missing",
    "details": {
      "missing_fields": ["position"],
      "required_fields": ["game_id", "player", "position"]
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


### 8. Invalid JSON Format
**Error Code:** `INVALID_JSON`  
**HTTP Status:** 400  
**Trigger:** Malformed JSON in request body

**Response:**

{
  "error": {
    "code": "INVALID_JSON",
    "message": "Request body contains invalid JSON",
    "details": {
      "parse_error": "Unexpected token at position 15"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


### 9. Rate Limit Exceeded
**Error Code:** `RATE_LIMIT_EXCEEDED`  
**HTTP Status:** 429  
**Trigger:** Too many requests from same client

**Response:**

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later",
    "details": {
      "limit": 100,
      "window": "60s",
      "retry_after": 45
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}


## Error Handling Best Practices

### Client Implementation

javascript
async function makeMove(gameId, player, position) {
  try {
    const response = await fetch('/game/move', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({game_id: gameId, player, position})
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      switch(error.error.code) {
        case 'CELL_OCCUPIED':
          alert('That cell is already taken!');
          break;
        case 'WRONG_TURN':
          alert(`Wait for player ${error.error.details.current_turn}'s turn`);
          break;
        case 'GAME_FINISHED':
          alert('Game is over. Start a new game!');
          break;
        case 'INVALID_POSITION':
          alert('Invalid position selected');
          break;
        default:
          alert('An error occurred: ' + error.error.message);
      }
      return null;
    }
    
    return await response.json();
  } catch (err) {
    console.error('Network error:', err);
    alert('Connection failed. Please check your network.');
    return null;
  }
}


## Validation Order

The API validates requests in the following order:

1. **JSON Format** - Validate request body is valid JSON
2. **Required Fields** - Check all required fields present
3. **Field Types** - Validate data types (string, number, object)
4. **Game Existence** - Verify game_id exists
5. **Player Validity** - Check player is 'X' or 'O'
6. **Position Bounds** - Validate row/col within 0-2
7. **Game Status** - Ensure game not finished
8. **Turn Order** - Verify correct player's turn
9. **Cell Availability** - Check cell not occupied

## Logging and Monitoring

All errors are logged with:
- Request ID for tracing
- Client IP (anonymized)
- Error code and message
- Request payload (sanitized)
- Timestamp

**Example Log Entry:**

{
  "level": "warn",
  "request_id": "req_xyz789",
  "error_code": "CELL_OCCUPIED",
  "game_id": "abc123",
  "position": {"row": 0, "col": 0},
  "timestamp": "2024-01-15T10:30:00Z"
}
