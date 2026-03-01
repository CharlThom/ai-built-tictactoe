# Player Entity Design

## Overview
The Player entity represents individual players participating in a TicTacToe game. Each game has exactly two players.

## Schema Definition

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique identifier for the player |
| player_number | Enum (1, 2) | NOT NULL | Player turn order (1 or 2) |
| symbol | Enum ('X', 'O') | NOT NULL | Player's symbol on the board |
| game_id | Integer | Foreign Key (games.id), NOT NULL, ON DELETE CASCADE | Reference to the associated game |

## Design Decisions

### 1. Enum Types for player_number and symbol
**Decision**: Use enum types instead of plain integers/strings
**Rationale**: 
- Type safety at database and application level
- Prevents invalid values (e.g., player_number=3 or symbol='Z')
- Self-documenting code
- Better IDE support and autocomplete

### 2. Foreign Key with CASCADE Delete
**Decision**: game_id has ON DELETE CASCADE constraint
**Rationale**:
- When a game is deleted, associated players should be automatically removed
- Maintains referential integrity
- Prevents orphaned player records

### 3. Separate Player Entities vs Embedded
**Decision**: Players are separate entities rather than embedded in Game
**Rationale**:
- Allows for future extensibility (player profiles, statistics, authentication)
- Cleaner separation of concerns
- Easier to query player-specific data
- Supports potential multiplayer or tournament features

### 4. player_number vs player_id naming
**Decision**: Use player_number instead of player_id
**Rationale**:
- Avoids confusion with the entity's primary key 'id'
- Clearly indicates it's a positional/ordinal value (1st or 2nd player)
- More semantically accurate

## Relationships

- **Many-to-One with Game**: Each player belongs to exactly one game; each game has exactly two players
- Bidirectional relationship configured via SQLAlchemy's `relationship()` and `back_populates`

## Constraints & Validation

1. **Game-level constraint** (enforced at application layer): Each game must have exactly 2 players
2. **Uniqueness constraint** (recommended): Consider adding unique constraint on (game_id, player_number) to prevent duplicate player numbers per game
3. **Symbol assignment**: Typically player 1 gets 'X' and player 2 gets 'O', enforced at application layer

## Future Considerations

- Add player name/username field for user identification
- Add player_type field (human/AI) for bot support
- Add statistics fields (games_played, wins, losses)
- Link to User entity for authenticated players