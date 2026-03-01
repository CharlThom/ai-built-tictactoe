# TicTacToe API Interactive Playground Guide

## Quick Start

### Option 1: Import Postman Collection (Recommended)

1. **Install Postman**
   - Download from [postman.com](https://www.postman.com/downloads/)
   - Or use the web version at [web.postman.co](https://web.postman.co)

2. **Import the Collection**
   bash
   # In Postman:
   # 1. Click "Import" button (top-left)
   # 2. Select "postman/TicTacToe_API_Collection.json"
   # 3. Click "Import"
   

3. **Configure Environment**
   - The collection uses `{{base_url}}` variable
   - Default: `http://localhost:8000`
   - To change: Edit collection variables or create an environment

4. **Start Testing**
   - Expand "Game Management" folder
   - Click "Create New Game"
   - Click "Send" button
   - The `game_id` is automatically saved for subsequent requests

### Option 2: Use cURL Commands

bash
# 1. Create a new game
curl -X POST http://localhost:8000/api/v1/game \
  -H "Content-Type: application/json" \
  -d '{"player_x": "Alice", "player_o": "Bob"}'

# Response: {"game_id": "abc123", "status": "in_progress", ...}

# 2. Make a move (replace {game_id} with actual ID)
curl -X POST http://localhost:8000/api/v1/game/{game_id}/move \
  -H "Content-Type: application/json" \
  -d '{"position": 4}'

# 3. Get game state
curl http://localhost:8000/api/v1/game/{game_id}/state

# 4. Restart game
curl -X POST http://localhost:8000/api/v1/game/{game_id}/restart


## Postman Collection Features

### Automated Testing
Each request includes automated tests that verify:
- ✅ Correct HTTP status codes
- ✅ Response schema validation
- ✅ Game state consistency
- ✅ Move validation logic
- ✅ Win/draw detection

### Pre-configured Scenarios

#### 1. **Game Management**
- Create New Game
- Get Game State
- Restart Game

#### 2. **Game Moves**
- Make Move - Position 0 (Top-Left)
- Make Move - Position 4 (Center)
- Invalid Move - Out of Bounds (tests error handling)

#### 3. **Test Scenarios**
- **Complete Game - X Wins (Top Row)**
  - Automated 6-move sequence
  - Demonstrates full game flow
  - Validates win detection

### Variables & Auto-population

**Collection Variables:**
- `base_url`: API server URL (default: `http://localhost:8000`)
- `game_id`: Automatically captured from "Create New Game" response

**How it works:**
javascript
// After creating a game, this script runs automatically:
var jsonData = pm.response.json();
pm.collectionVariables.set('game_id', jsonData.game_id);

// All subsequent requests use {{game_id}} automatically


## Testing Workflows

### Workflow 1: Quick Game Test

1. **Create New Game** → Captures `game_id`
2. **Make Move - Position 0** → X plays top-left
3. **Make Move - Position 4** → O plays center
4. **Get Game State** → Verify board state
5. **Restart Game** → Reset for new round

### Workflow 2: Complete Game Scenario

1. Navigate to **Test Scenarios → Complete Game - X Wins**
2. Right-click folder → **Run folder**
3. Watch automated sequence:
   - Creates game
   - Plays 6 moves
   - X wins with top row (positions 0, 1, 2)
   - All tests validate each step

### Workflow 3: Error Handling Test

1. **Create New Game**
2. **Make Move - Position 0** (X plays)
3. **Make Move - Position 0** (try same position) → Expect 400 error
4. **Invalid Move - Out of Bounds** → Expect 400 error
5. Verify error messages are descriptive

## Board Position Reference


Board positions (0-8):

 0 | 1 | 2
-----------
 3 | 4 | 5
-----------
 6 | 7 | 8


## Response Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | OK | Successful move, state retrieval, restart |
| 201 | Created | New game created |
| 400 | Bad Request | Invalid position, position occupied, wrong turn |
| 404 | Not Found | Game ID doesn't exist |
| 409 | Conflict | Game already finished |

## Example Responses

### Successful Move

{
  "game_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "current_player": "O",
  "board": ["X", null, null, null, null, null, null, null, null],
  "move_number": 1
}


### Game Won

{
  "game_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "won",
  "winner": "X",
  "winning_line": [0, 1, 2],
  "board": ["X", "X", "X", "O", "O", null, null, null, null],
  "move_number": 5
}


### Error Response

{
  "error": "Invalid move",
  "message": "Position 4 is already occupied",
  "code": "POSITION_OCCUPIED"
}


## Advanced Usage

### Running All Tests

**Via Postman UI:**
1. Click collection name (TicTacToe API Collection)
2. Click "Run" button
3. Select requests to run
4. Click "Run TicTacToe API Collection"
5. View test results summary

**Via Newman (CLI):**
bash
# Install Newman
npm install -g newman

# Run collection
newman run postman/TicTacToe_API_Collection.json \
  --environment your-environment.json

# With detailed output
newman run postman/TicTacToe_API_Collection.json \
  --reporters cli,json \
  --reporter-json-export results.json


### Custom Environment Setup

**Create environment file** (`environments/production.json`):

{
  "name": "Production",
  "values": [
    {
      "key": "base_url",
      "value": "https://api.tictactoe.example.com",
      "enabled": true
    }
  ]
}


### Extending the Collection

**Add custom test:**
javascript
// In Postman Tests tab:
pm.test("Custom validation", function () {
    var jsonData = pm.response.json();
    // Your custom assertions
    pm.expect(jsonData.board.filter(x => x !== null).length).to.be.below(10);
});


## Troubleshooting

### Issue: "Could not get response"
**Solution:** Ensure backend server is running on `{{base_url}}`
bash
# Start the server
python src/main.py
# or
npm start


### Issue: "game_id variable not set"
**Solution:** Run "Create New Game" request first to populate the variable

### Issue: Tests failing
**Solution:** Check that:
1. Server is running and accessible
2. Database is initialized
3. No games are in corrupted state
4. Run "Restart Game" to reset state

## Best Practices

1. **Always start with "Create New Game"** to get a fresh `game_id`
2. **Use test scenarios** to validate complete workflows
3. **Check test results** after each request to catch issues early
4. **Use "Restart Game"** instead of creating new games for quick testing
5. **Export results** when reporting bugs (Collection Runner → Export Results)

## Integration with CI/CD

yaml
# .github/workflows/api-tests.yml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start API Server
        run: |
          python src/main.py &
          sleep 5
      - name: Install Newman
        run: npm install -g newman
      - name: Run API Tests
        run: newman run postman/TicTacToe_API_Collection.json


## Support

For issues or questions:
- Check API documentation: `/docs/API_REFERENCE.md`
- Review test results in Postman Console
- Enable verbose logging in server configuration
- Contact: api-support@tictactoe.example.com
