# Component Interfaces - TicTacToe

## Type Definitions

### Common Types

typescript
type CellValue = 'X' | 'O' | null;
type Player = 'X' | 'O';
type BoardState = [CellValue, CellValue, CellValue, CellValue, CellValue, CellValue, CellValue, CellValue, CellValue];
type CellIndex = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;


## Component Interfaces

### App Component

**Interface**: Root component (no props)

typescript
interface AppState {
  board: BoardState;
  currentPlayer: Player;
  winner: Player | null;
  gameOver: boolean;
}

interface AppMethods {
  handleCellClick(index: CellIndex): void;
  checkWinner(): Player | null;
  checkDraw(): boolean;
  restartGame(): void;
}


**Initial State**:
javascript
{
  board: [null, null, null, null, null, null, null, null, null],
  currentPlayer: 'X',
  winner: null,
  gameOver: false
}


---

### Board Component

typescript
interface BoardProps {
  board: BoardState;
  onCellClick: (index: CellIndex) => void;
  gameOver: boolean;
}


**Usage Example**:
jsx
<Board 
  board={board} 
  onCellClick={handleCellClick} 
  gameOver={gameOver} 
/>


---

### Cell Component

typescript
interface CellProps {
  value: CellValue;
  onClick: () => void;
  disabled: boolean;
  index: CellIndex;
}


**Computed Disabled State**:
javascript
disabled = gameOver || value !== null


**Usage Example**:
jsx
<Cell 
  value={board[0]} 
  onClick={() => onCellClick(0)} 
  disabled={gameOver || board[0] !== null}
  index={0}
/>


---

### StatusDisplay Component

typescript
interface StatusDisplayProps {
  currentPlayer: Player;
  winner: Player | null;
  gameOver: boolean;
}


**Display Logic**:
javascript
function getStatusMessage(props) {
  if (props.winner) {
    return `Player ${props.winner} wins!`;
  }
  if (props.gameOver) {
    return "It's a draw!";
  }
  return `Current Player: ${props.currentPlayer}`;
}


**Usage Example**:
jsx
<StatusDisplay 
  currentPlayer={currentPlayer} 
  winner={winner} 
  gameOver={gameOver} 
/>


---

### RestartButton Component

typescript
interface RestartButtonProps {
  onRestart: () => void;
}


**Usage Example**:
jsx
<RestartButton onRestart={restartGame} />


---

## Game Logic Utilities

### Win Condition Checker

typescript
function checkWinner(board: BoardState): Player | null


**Win Patterns**:
javascript
const WIN_PATTERNS = [
  [0, 1, 2], // Top row
  [3, 4, 5], // Middle row
  [6, 7, 8], // Bottom row
  [0, 3, 6], // Left column
  [1, 4, 7], // Middle column
  [2, 5, 8], // Right column
  [0, 4, 8], // Diagonal \
  [2, 4, 6]  // Diagonal /
];


### Draw Condition Checker

typescript
function checkDraw(board: BoardState): boolean


**Logic**: All cells filled and no winner
javascript
return board.every(cell => cell !== null) && !checkWinner(board);


---

## Event Handlers

### handleCellClick Implementation

javascript
function handleCellClick(index) {
  // Guard clauses
  if (gameOver) return;
  if (board[index] !== null) return;
  
  // Update board
  const newBoard = [...board];
  newBoard[index] = currentPlayer;
  
  // Check game end conditions
  const winner = checkWinner(newBoard);
  const isDraw = checkDraw(newBoard);
  
  // Update state
  setState({
    board: newBoard,
    currentPlayer: currentPlayer === 'X' ? 'O' : 'X',
    winner: winner,
    gameOver: winner !== null || isDraw
  });
}


### restartGame Implementation

javascript
function restartGame() {
  setState({
    board: [null, null, null, null, null, null, null, null, null],
    currentPlayer: 'X',
    winner: null,
    gameOver: false
  });
}


---

## CSS Class Naming Convention

### BEM Methodology

css
/* App */
.app
.app__container

/* Board */
.board
.board--game-over

/* Cell */
.cell
.cell--filled
.cell--disabled
.cell--x
.cell--o
.cell:hover

/* StatusDisplay */
.status-display
.status-display__message
.status-display--winner
.status-display--draw

/* RestartButton */
.restart-button
.restart-button:hover
.restart-button:active


---

## Component Communication Diagram


┌─────────────────────────────────────┐
│              App                    │
│  State: board, currentPlayer,       │
│         winner, gameOver            │
└──────────┬──────────────────────────┘
           │
           ├─── Props ───► StatusDisplay
           │               (currentPlayer, winner, gameOver)
           │
           ├─── Props ───► Board
           │               (board, onCellClick, gameOver)
           │               │
           │               └─── Props ───► Cell (×9)
           │                               (value, onClick, disabled, index)
           │
           └─── Props ───► RestartButton
                           (onRestart)

           ▲
           │
      Events bubble up


---

## Validation Rules

1. **Cell Click**: Only allowed if cell is empty and game is not over
2. **Player Turn**: Automatically alternates after valid move
3. **Game Over**: Triggered by win or draw, disables all cells
4. **Restart**: Always available, resets to initial state

---

## Error Handling

- Invalid cell index: Ignored (should not occur with proper UI)
- Click on filled cell: No-op
- Click when game over: No-op
- All state transitions are atomic and consistent