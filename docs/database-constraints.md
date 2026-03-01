# Database Schema Constraints

## Overview
This document defines the data integrity constraints for the TicTacToe database schema.

## Entity Constraints

### Game Entity
- `id`: Primary key, auto-increment, NOT NULL
- `status`: ENUM('in_progress', 'completed'), NOT NULL, DEFAULT 'in_progress'
- `winner`: ENUM('player1', 'player2', 'draw', NULL), DEFAULT NULL
- `created_at`: TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP
- `updated_at`: TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

**Business Rules:**
- `winner` can only be set when `status` = 'completed'
- `winner` must be NULL when `status` = 'in_progress'

### Board Entity
- `id`: Primary key, auto-increment, NOT NULL
- `game_id`: Foreign key references Game(id), NOT NULL, UNIQUE, ON DELETE CASCADE
- `cell_states`: JSON array of exactly 9 elements, NOT NULL
- `current_turn`: ENUM('player1', 'player2'), NOT NULL, DEFAULT 'player1'

**Cell States Constraints:**
- Array length must be exactly 9 elements
- Each element must be one of: 'empty', 'X', 'O'
- Valid positions: indices 0-8 (representing board positions)
- Position mapping:
  
  0 | 1 | 2
  ---------
  3 | 4 | 5
  ---------
  6 | 7 | 8
  

**Validation Rules:**
- CHECK constraint: `JSON_LENGTH(cell_states) = 9`
- Each cell value must match regex: `^(empty|X|O)$`

### Player Entity
- `id`: Primary key, auto-increment, NOT NULL
- `player_number`: INTEGER, NOT NULL, CHECK(player_number IN (1, 2))
- `symbol`: ENUM('X', 'O'), NOT NULL
- `game_id`: Foreign key references Game(id), NOT NULL, ON DELETE CASCADE

**Unique Constraints:**
- UNIQUE(game_id, player_number) - ensures only one player per number per game
- UNIQUE(game_id, symbol) - ensures only one player per symbol per game

**Business Rules:**
- Exactly 2 players per game
- Player 1 must have symbol 'X'
- Player 2 must have symbol 'O'

### Move Entity (Optional - for move history)
- `id`: Primary key, auto-increment, NOT NULL
- `game_id`: Foreign key references Game(id), NOT NULL, ON DELETE CASCADE
- `player_id`: Foreign key references Player(id), NOT NULL, ON DELETE CASCADE
- `position`: INTEGER, NOT NULL, CHECK(position >= 0 AND position <= 8)
- `symbol`: ENUM('X', 'O'), NOT NULL
- `move_number`: INTEGER, NOT NULL, CHECK(move_number > 0)
- `created_at`: TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP

**Unique Constraints:**
- UNIQUE(game_id, position) - ensures each position is played only once per game
- UNIQUE(game_id, move_number) - ensures sequential move ordering

**Validation Rules:**
- Position range: 0-8 (inclusive)
- Position must correspond to a valid board cell
- Symbol must match the player's assigned symbol

## Index Recommendations

sql
-- Performance indexes
CREATE INDEX idx_game_status ON Game(status);
CREATE INDEX idx_board_game_id ON Board(game_id);
CREATE INDEX idx_player_game_id ON Player(game_id);
CREATE INDEX idx_move_game_id ON Move(game_id);
CREATE INDEX idx_move_position ON Move(game_id, position);


## Constraint Summary Table

| Constraint Type | Entity | Field(s) | Rule |
|----------------|--------|----------|------|
| CHECK | Board | cell_states | Length = 9 |
| CHECK | Board | cell_states[i] | Value IN ('empty', 'X', 'O') |
| CHECK | Player | player_number | Value IN (1, 2) |
| CHECK | Move | position | Value >= 0 AND <= 8 |
| UNIQUE | Board | game_id | One board per game |
| UNIQUE | Player | (game_id, player_number) | One player per number per game |
| UNIQUE | Player | (game_id, symbol) | One player per symbol per game |
| UNIQUE | Move | (game_id, position) | One move per position per game |
| UNIQUE | Move | (game_id, move_number) | Sequential move ordering |
| FOREIGN KEY | Board | game_id | References Game(id) CASCADE |
| FOREIGN KEY | Player | game_id | References Game(id) CASCADE |
| FOREIGN KEY | Move | game_id | References Game(id) CASCADE |
| FOREIGN KEY | Move | player_id | References Player(id) CASCADE |

## Data Validation Examples

### Valid Cell States

["empty", "X", "O", "empty", "X", "empty", "O", "empty", "empty"]


### Invalid Cell States

// Too few elements
["empty", "X", "O"]

// Invalid value
["empty", "X", "Y", "empty", "X", "empty", "O", "empty", "empty"]

// Wrong type
[0, 1, 2, 0, 1, 0, 2, 0, 0]


### Valid Move Positions
- 0, 1, 2, 3, 4, 5, 6, 7, 8

### Invalid Move Positions
- -1, 9, 10, null, "5"
