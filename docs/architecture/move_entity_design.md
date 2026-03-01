# Move Entity Design

## Overview
The Move entity tracks individual player moves within a TicTacToe game, maintaining a complete history of all actions taken during gameplay.

## Schema Definition

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique identifier for each move |
| game_id | Integer | Foreign Key (games.id), NOT NULL, Indexed | Reference to the game this move belongs to |
| player_id | Integer | Foreign Key (players.id), NOT NULL, Indexed | Reference to the player who made this move |
| position | Integer | NOT NULL, CHECK (0-8) | Board position where move was made (0-8 representing 3x3 grid) |
| timestamp | DateTime | NOT NULL, Default: UTC now | When the move was made |

### Relationships
- **game**: Many-to-One relationship with Game entity (CASCADE delete)
- **player**: Many-to-One relationship with Player entity (CASCADE delete)

### Constraints
- Position must be between 0 and 8 (inclusive) representing valid board positions
- Position must be an integer value
- Foreign key cascades ensure moves are deleted when parent game/player is deleted

## Design Decisions

### Position Representation
- **Decision**: Use integer 0-8 for position instead of row/column pairs
- **Rationale**: Simpler indexing, matches array-based board representation, easier validation
- **Mapping**: Position maps to board as: [0,1,2] (top row), [3,4,5] (middle), [6,7,8] (bottom)

### Timestamp Storage
- **Decision**: Store UTC timestamps with default value
- **Rationale**: Enables move history replay, game analytics, and dispute resolution

### Cascade Deletion
- **Decision**: CASCADE delete on both game_id and player_id foreign keys
- **Rationale**: Moves have no meaning without their parent game/player context

### Indexing Strategy
- **Decision**: Index both game_id and player_id
- **Rationale**: Common query patterns include fetching all moves for a game and all moves by a player

## Usage Examples

python
# Create a new move
move = Move(
    game_id=1,
    player_id=1,
    position=4  # Center position
)

# Query moves for a game (chronological order)
moves = session.query(Move).filter_by(game_id=1).order_by(Move.timestamp).all()

# Validate move uniqueness (business logic layer)
existing_move = session.query(Move).filter_by(game_id=1, position=4).first()
if existing_move:
    raise ValueError("Position already taken")


## Integration Notes
- Move validation (position not already taken) should be handled at business logic layer
- Moves should be created atomically with Board state updates
- Consider adding unique constraint on (game_id, position) to prevent duplicate moves at DB level