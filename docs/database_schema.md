# Database Schema - TicTacToe

## Game Entity

### Table: `games`

| Field       | Type     | Constraints           | Description                                    |
|-------------|----------|-----------------------|------------------------------------------------|
| id          | INTEGER  | PRIMARY KEY, AUTO_INC | Unique identifier for each game                |
| status      | ENUM     | NOT NULL, INDEXED     | Game status: 'in_progress' or 'completed'      |
| winner      | ENUM     | NULLABLE              | Winner: 'player1', 'player2', 'draw', or NULL  |
| created_at  | DATETIME | NOT NULL              | Timestamp when game was created (UTC)          |
| updated_at  | DATETIME | NOT NULL              | Timestamp when game was last updated (UTC)     |

### Enumerations

**GameStatus:**
- `in_progress`: Game is currently being played
- `completed`: Game has finished

**GameWinner:**
- `player1`: Player 1 won the game
- `player2`: Player 2 won the game
- `draw`: Game ended in a draw
- `null`: No winner yet (game in progress)

### Indexes
- Primary key on `id`
- Index on `status` for efficient querying of active/completed games

### Business Rules
1. `winner` must be NULL when `status` is 'in_progress'
2. `winner` must be set when `status` is 'completed'
3. `updated_at` automatically updates on any record modification
4. All timestamps stored in UTC

### Design Decisions
- Using SQLAlchemy ORM for database abstraction and portability
- Enums enforce data integrity at application and database level
- Automatic timestamp management reduces manual errors
- Simple schema supports core game functionality without over-engineering