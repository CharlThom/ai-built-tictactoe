# TicTacToe Entity Relationship Diagram

## Entity Relationships


┌─────────────────────────────────────────────────────────────────┐
│                            GAME                                 │
├─────────────────────────────────────────────────────────────────┤
│ PK: id (UUID/INT)                                               │
│     status (ENUM: in_progress, completed)                       │
│     winner (ENUM: player1, player2, draw, NULL)                 │
│     created_at (TIMESTAMP)                                      │
│     updated_at (TIMESTAMP)                                      │
└──────────────┬──────────────────────┬───────────────────────────┘
               │                      │
               │ 1:1                  │ 1:2
               │                      │
               ▼                      ▼
┌──────────────────────────┐  ┌─────────────────────────────┐
│         BOARD            │  │          PLAYER             │
├──────────────────────────┤  ├─────────────────────────────┤
│ PK: id (UUID/INT)        │  │ PK: id (UUID/INT)           │
│ FK: game_id (UNIQUE)     │  │ FK: game_id                 │
│     cell_states (JSON)   │  │     player_number (1 or 2)  │
│     current_turn (ENUM)  │  │     symbol (X or O)         │
└──────────────────────────┘  └─────────────────────────────┘
               ▲
               │
               │ N:1
               │
┌──────────────┴───────────┐
│          MOVE            │
├──────────────────────────┤
│ PK: id (UUID/INT)        │
│ FK: game_id              │
│     player_id            │
│     position (0-8)       │
│     move_number (INT)    │
│     created_at           │
└──────────────────────────┘


## Relationship Details

### Game ↔ Board (1:1)
- **Cardinality**: One Game has exactly one Board
- **Foreign Key**: Board.game_id → Game.id (UNIQUE constraint)
- **Cascade**: DELETE Game → DELETE Board
- **Rationale**: Board state is intrinsic to a game instance

### Game ↔ Player (1:2)
- **Cardinality**: One Game has exactly two Players
- **Foreign Key**: Player.game_id → Game.id
- **Constraint**: UNIQUE(game_id, player_number) ensures exactly 2 players per game
- **Cascade**: DELETE Game → DELETE Players
- **Rationale**: TicTacToe requires exactly two players per game

### Game ↔ Move (1:N)
- **Cardinality**: One Game has zero to many Moves (max 9)
- **Foreign Key**: Move.game_id → Game.id
- **Cascade**: DELETE Game → DELETE Moves
- **Rationale**: Maintains complete game history for replay and audit

## Indexes

sql
-- Game table
CREATE INDEX idx_game_status ON Game(status);
CREATE INDEX idx_game_created_at ON Game(created_at);

-- Board table
CREATE UNIQUE INDEX idx_board_game_id ON Board(game_id);

-- Player table
CREATE INDEX idx_player_game_id ON Player(game_id);
CREATE UNIQUE INDEX idx_player_game_player_num ON Player(game_id, player_number);

-- Move table
CREATE INDEX idx_move_game_id ON Move(game_id);
CREATE INDEX idx_move_player_id ON Move(player_id);
CREATE INDEX idx_move_game_move_num ON Move(game_id, move_number);


## Constraints Summary

| Entity | Constraint | Purpose |
|--------|------------|----------|
| Board  | UNIQUE(game_id) | Enforce 1:1 with Game |
| Player | UNIQUE(game_id, player_number) | Enforce exactly 2 players |
| Player | CHECK(player_number IN (1,2)) | Valid player numbers |
| Player | CHECK(symbol IN ('X','O')) | Valid symbols |
| Move   | CHECK(position BETWEEN 0 AND 8) | Valid board positions |
| Move   | UNIQUE(game_id, position) | No duplicate moves on same cell |
