# TicTacToe API Quickstart Guide

## Getting Started

This guide will help you integrate the TicTacToe API into your application in minutes.

## Prerequisites

- API endpoint: `https://api.tictactoe.example.com/v1`
- API key (obtain from developer portal)
- HTTP client library

## Quick Example

### 1. Initialize a New Game Session

**Request:**
bash
curl -X POST https://api.tictactoe.example.com/v1/game/new \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "player1": "Alice",
    "player2": "Bob",
    "firstPlayer": "X"
  }'


**Response:**

{
  "gameId": "game_abc123xyz",
  "status": "in_progress",
  "currentPlayer": "X",
  "board": [
    ["", "", ""],
    ["", "", ""],
    ["", "", ""]
  ],
  "players": {
    "X": "Alice",
    "O": "Bob"
  },
  "createdAt": "2024-01-15T10:30:00Z"
}


### 2. Make a Move

**Request:**
bash
curl -X POST https://api.tictactoe.example.com/v1/game/move \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "gameId": "game_abc123xyz",
    "player": "X",
    "position": {"row": 0, "col": 0}
  }'


**Response:**

{
  "gameId": "game_abc123xyz",
  "status": "in_progress",
  "currentPlayer": "O",
  "board": [
    ["X", "", ""],
    ["", "", ""],
    ["", "", ""]
  ],
  "moveValid": true,
  "message": "Move accepted"
}


### 3. Check Game State

**Request:**
bash
curl -X GET https://api.tictactoe.example.com/v1/game/state/game_abc123xyz \
  -H "Authorization: Bearer YOUR_API_KEY"


**Response:**

{
  "gameId": "game_abc123xyz",
  "status": "in_progress",
  "currentPlayer": "O",
  "board": [
    ["X", "", ""],
    ["", "", ""],
    ["", "", ""]
  ],
  "moveCount": 1,
  "winner": null
}


### 4. Game Completion Example

When a player wins:


{
  "gameId": "game_abc123xyz",
  "status": "completed",
  "winner": "X",
  "winningLine": [
    {"row": 0, "col": 0},
    {"row": 0, "col": 1},
    {"row": 0, "col": 2}
  ],
  "board": [
    ["X", "X", "X"],
    ["O", "O", ""],
    ["", "", ""]
  ]
}


### 5. Restart Game

**Request:**
bash
curl -X POST https://api.tictactoe.example.com/v1/game/restart \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"gameId": "game_abc123xyz"}'


## Code Examples

### Python

python
import requests

API_URL = "https://api.tictactoe.example.com/v1"
API_KEY = "your_api_key_here"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Initialize new game
response = requests.post(
    f"{API_URL}/game/new",
    headers=headers,
    json={
        "player1": "Alice",
        "player2": "Bob",
        "firstPlayer": "X"
    }
)
game = response.json()
game_id = game["gameId"]

# Make a move
response = requests.post(
    f"{API_URL}/game/move",
    headers=headers,
    json={
        "gameId": game_id,
        "player": "X",
        "position": {"row": 1, "col": 1}
    }
)
print(response.json())


### JavaScript (Node.js)

javascript
const axios = require('axios');

const API_URL = 'https://api.tictactoe.example.com/v1';
const API_KEY = 'your_api_key_here';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// Initialize new game
async function startGame() {
  const response = await axios.post(`${API_URL}/game/new`, {
    player1: 'Alice',
    player2: 'Bob',
    firstPlayer: 'X'
  }, { headers });
  
  return response.data.gameId;
}

// Make a move
async function makeMove(gameId, player, row, col) {
  const response = await axios.post(`${API_URL}/game/move`, {
    gameId,
    player,
    position: { row, col }
  }, { headers });
  
  return response.data;
}

// Usage
(async () => {
  const gameId = await startGame();
  const result = await makeMove(gameId, 'X', 0, 0);
  console.log(result);
})();


### Java

java
import java.net.http.*;
import java.net.URI;
import org.json.JSONObject;

public class TicTacToeClient {
    private static final String API_URL = "https://api.tictactoe.example.com/v1";
    private static final String API_KEY = "your_api_key_here";
    
    public static String createGame() throws Exception {
        HttpClient client = HttpClient.newHttpClient();
        
        JSONObject body = new JSONObject()
            .put("player1", "Alice")
            .put("player2", "Bob")
            .put("firstPlayer", "X");
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL + "/game/new"))
            .header("Authorization", "Bearer " + API_KEY)
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(body.toString()))
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        JSONObject json = new JSONObject(response.body());
        return json.getString("gameId");
    }
}


## Error Handling

Common error responses:

- `400 Bad Request`: Invalid move or malformed request
- `401 Unauthorized`: Invalid or missing API key
- `404 Not Found`: Game session not found
- `409 Conflict`: Move not allowed (wrong player turn, position occupied)

Example error response:

{
  "error": "invalid_move",
  "message": "Position already occupied",
  "code": 409
}


## Next Steps

- Review the [full API reference](./API_REFERENCE.md)
- Explore [advanced features](./ADVANCED.md)
- Check [rate limits and best practices](./BEST_PRACTICES.md)
- Join our [developer community](https://community.tictactoe.example.com)