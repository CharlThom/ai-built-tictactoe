# TicTacToe Game State API Documentation

## Overview
This document describes the game state management endpoints for the TicTacToe API.

---

## Endpoints

### 1. Get Game State

**Endpoint:** `GET /game/state`

**Description:** Retrieves the current state of the game.

**Request Parameters:**
- `game_id` (query, required): UUID of the game

**Request Example:**
http
GET /game/state?game_id=550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json


**Response Schema:**

{
  "game_id": "string (UUID)",
  "board": "array[9] (string|null)",
  "current_player": "string (X|O)",
  "status": "string (in_progress|won|draw)",
  "winner": "string|null (X|O|null)",
  "winning_line": "array[3]|null (integers 0-8)",
  "move_count": "integer",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}


**Response Example (200 OK):**

{
  "game_id": "550e8400-e29b-41d4-a716-446655440000",
  "board": ["X", "O", null, "X", null, null, null, null, null],
  "current_player": "O",
  "status": "in_progress",
  "winner": null,
  "winning_line": null,
  "move_count": 2,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:00Z"
}


**Error Responses:**
- `400 Bad Request`: Missing or invalid game_id

{
  "error": "invalid_request",
  "message": "game_id is required and must be a valid UUID"
}


- `404 Not Found`: Game not found

{
  "error": "game_not_found",
  "message": "No game found with the provided game_id"
}


---

### 2. Make a Move

**Endpoint:** `POST /game/move`

**Description:** Makes a move on the game board.

**Request Schema:**

{
  "game_id": "string (UUID, required)",
  "position": "integer (0-8, required)",
  "player": "string (X|O, required)"
}


**Request Example:**
http
POST /game/move
Content-Type: application/json

{
  "game_id": "550e8400-e29b-41d4-a716-446655440000",
  "position": 4,
  "player": "O"
}


**Response Schema:**

{
  "success": "boolean",
  "game_state": {
    "game_id": "string (UUID)",
    "board": "array[9] (string|null)",
    "current_player": "string (X|O)",
    "status": "string (in_progress|won|draw)",
    "winner": "string|null (X|O|null)",
    "winning_line": "array[3]|null",
    "move_count": "integer",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
  }
}


**Response Example (200 OK):**

{
  "success": true,
  "game_state": {
    "game_id": "550e8400-e29b-41d4-a716-446655440000",
    "board": ["X", "O", null, "X", "O", null, null, null, null],
    "current_player": "X",
    "status": "in_progress",
    "winner": null,
    "winning_line": null,
    "move_count": 3,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:32:00Z"
  }
}


**Response Example - Game Won (200 OK):**

{
  "success": true,
  "game_state": {
    "game_id": "550e8400-e29b-41d4-a716-446655440000",
    "board": ["X", "X", "X", "O", "O", null, null, null, null],
    "current_player": "O",
    "status": "won",
    "winner": "X",
    "winning_line": [0, 1, 2],
    "move_count": 5,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}


**Error Responses:**
- `400 Bad Request`: Invalid request data

{
  "error": "invalid_request",
  "message": "position must be an integer between 0 and 8"
}


- `400 Bad Request`: Invalid move

{
  "error": "invalid_move",
  "message": "Position 4 is already occupied"
}


- `400 Bad Request`: Wrong player turn

{
  "error": "wrong_turn",
  "message": "It is player X's turn"
}


- `400 Bad Request`: Game already finished

{
  "error": "game_finished",
  "message": "Game has already ended. Use POST /game/restart to start a new game"
}


- `404 Not Found`: Game not found

{
  "error": "game_not_found",
  "message": "No game found with the provided game_id"
}


---

### 3. Restart Game

**Endpoint:** `POST /game/restart`

**Description:** Resets the game board to start a new game with the same game_id.

**Request Schema:**

{
  "game_id": "string (UUID, required)",
  "starting_player": "string (X|O, optional, default: X)"
}


**Request Example:**
http
POST /game/restart
Content-Type: application/json

{
  "game_id": "550e8400-e29b-41d4-a716-446655440000",
  "starting_player": "X"
}


**Response Schema:**

{
  "success": "boolean",
  "game_state": {
    "game_id": "string (UUID)",
    "board": "array[9] (null)",
    "current_player": "string (X|O)",
    "status": "string (in_progress)",
    "winner": "null",
    "winning_line": "null",
    "move_count": "integer (0)",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
  }
}


**Response Example (200 OK):**

{
  "success": true,
  "game_state": {
    "game_id": "550e8400-e29b-41d4-a716-446655440000",
    "board": [null, null, null, null, null, null, null, null, null],
    "current_player": "X",
    "status": "in_progress",
    "winner": null,
    "winning_line": null,
    "move_count": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:40:00Z"
  }
}


**Error Responses:**
- `400 Bad Request`: Invalid request data

{
  "error": "invalid_request",
  "message": "starting_player must be either X or O"
}


- `404 Not Found`: Game not found

{
  "error": "game_not_found",
  "message": "No game found with the provided game_id"
}


---

## Board Position Reference

The board is represented as a flat array of 9 positions (0-8):


 0 | 1 | 2
-----------
 3 | 4 | 5
-----------
 6 | 7 | 8


## Status Values

- `in_progress`: Game is ongoing
- `won`: Game has been won by a player
- `draw`: Game ended in a draw (all positions filled, no winner)

## Common HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters or game logic violation
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error