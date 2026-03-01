# Database Schema Design Decisions

## Relationship Design Rationale

### 1. Game ↔ Board (1:1 Relationship)

**Decision**: Separate Board entity from Game entity

**Rationale**:
- **Separation of Concerns**: Game manages lifecycle/metadata, Board manages state
- **Query Optimization**: Can fetch game metadata without loading board state
- **Extensibility**: Future support for different board types or sizes

**Implementation**:
- Board.game_id has UNIQUE constraint enforcing 1:1
- Cascading deletes maintain referential integrity

**Alternative Considered**: Embedding board state in Game table
- Rejected: Violates single responsibility principle, harder to extend

---

### 2. Game ↔ Player (1:2 Relationship)

**Decision**: Exactly two Player records per Game

**Rationale**:
- **Data Normalization**: Player attributes (symbol, number) stored separately
- **Flexibility**: Easy to add player statistics, history, or user associations
- **Validation**: Database-level constraint ensures exactly 2 players

**Implementation**:
- UNIQUE(game_id, player_number) constraint
- CHECK constraint: player_number IN (1, 2)
- Application layer validates 2 players before game starts

**Alternative Considered**: Storing player1_symbol, player2_symbol in Game table
- Rejected: Less flexible for future features (player profiles, AI vs human)

---

### 3. Game ↔ Move (1:N Relationship)

**Decision**: Separate Move entity for game history

**Rationale**:
- **Audit Trail**: Complete history of all moves for replay/analysis
- **Undo Functionality**: Can implement move rollback
- **Analytics**: Query patterns, game duration, player behavior
- **Debugging**: Trace game state evolution

**Implementation**:
- Move.game_id foreign key (non-unique, allows multiple moves)
- move_number field for ordering (1-9)
- UNIQUE(game_id, position) prevents duplicate moves on same cell

**Alternative Considered**: Only storing final board state
- Rejected: Loses valuable historical data, can't replay games

---

## Key Constraints

### Referential Integrity
- All foreign keys use CASCADE DELETE to prevent orphaned records
- ON UPDATE CASCADE for id changes (if using natural keys)

### Data Validation
- CHECK constraints enforce business rules at database level
- ENUM types for status, winner, symbol ensure valid values
- NOT NULL constraints on required fields

### Performance Considerations
- Indexes on foreign keys for join performance
- Composite index on (game_id, move_number) for move ordering
- Index on game.status for filtering active games

---

## Schema Evolution Strategy

### Future Enhancements Supported
1. **User Accounts**: Add user_id to Player table
2. **Game Variants**: Add game_type to Game table (3x3, 4x4, etc.)
3. **Tournaments**: Add tournament_id to Game table
4. **AI Players**: Add player_type (human/ai) to Player table
5. **Time Controls**: Add time_limit, time_remaining to Game/Player

### Migration Path
- Schema supports backward-compatible additions
- Core relationships remain stable
- New features added via new columns or tables
