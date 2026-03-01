# Component Hierarchy - TicTacToe

## Overview
This document defines the component structure for the TicTacToe application following a component-based SPA architecture.

## Component Tree


App (Root Component)
├── StatusDisplay
├── Board
│   └── Cell (9 instances)
└── RestartButton


## Component Specifications

### App Component
**Responsibility**: Root container, manages global game state and orchestrates child components

**State**:
- `board`: Array[9] - Current board state (null, 'X', or 'O')
- `currentPlayer`: String - Current player ('X' or 'O')
- `winner`: String|null - Winner identifier or null
- `gameOver`: Boolean - Game completion status

**Methods**:
- `handleCellClick(index)`: Process cell selection
- `checkWinner()`: Evaluate win conditions
- `restartGame()`: Reset game state

**Props Passed Down**:
- To Board: `board`, `onCellClick`, `gameOver`
- To StatusDisplay: `currentPlayer`, `winner`, `gameOver`
- To RestartButton: `onRestart`

---

### Board Component
**Responsibility**: Render 3x3 grid and manage cell layout

**Props Received**:
- `board`: Array[9] - Cell values
- `onCellClick`: Function - Cell click handler
- `gameOver`: Boolean - Disable interaction when true

**Rendering**:
- Maps over board array to render 9 Cell components
- Applies grid layout (CSS Grid or Flexbox)

**No Internal State**: Pure presentational component

---

### Cell Component
**Responsibility**: Render individual cell and handle click events

**Props Received**:
- `value`: String|null - Cell content ('X', 'O', or null)
- `onClick`: Function - Click handler
- `disabled`: Boolean - Interaction state
- `index`: Number - Cell position (0-8)

**Behavior**:
- Display value if present
- Trigger onClick when clicked (if not disabled and empty)
- Apply hover states when interactive

**Styling States**:
- Empty, filled, disabled, hover

---

### StatusDisplay Component
**Responsibility**: Show current game status to users

**Props Received**:
- `currentPlayer`: String - Active player
- `winner`: String|null - Winner if game ended
- `gameOver`: Boolean - Game state

**Display Logic**:
- If `winner`: "Player {winner} wins!"
- If `gameOver && !winner`: "It's a draw!"
- Else: "Current Player: {currentPlayer}"

**No Internal State**: Pure presentational component

---

### RestartButton Component
**Responsibility**: Provide game reset functionality

**Props Received**:
- `onRestart`: Function - Reset handler

**Behavior**:
- Trigger onRestart when clicked
- Always visible and enabled

**No Internal State**: Pure presentational component

---

## Data Flow

### Unidirectional Data Flow
1. **State Management**: All game state lives in App component
2. **Props Down**: Data flows down via props
3. **Events Up**: User interactions bubble up via callbacks

### Event Flow Example

User clicks Cell → Cell.onClick() → Board.onCellClick() → App.handleCellClick()
→ App updates state → Re-render cascade → UI updates


## State Management Strategy

**Approach**: Lift state up pattern (React) / Centralized state (Vue)
- App component owns all state
- Child components are stateless/presentational
- No prop drilling beyond 2 levels

**Future Considerations**:
- For multiplayer: Introduce Context API (React) or Provide/Inject (Vue)
- For complex features: Consider Zustand/Redux (React) or Pinia (Vue)

## Component Reusability

**Highly Reusable**:
- Cell: Generic grid cell, reusable in other board games
- RestartButton: Generic action button

**Game-Specific**:
- Board: TicTacToe-specific 3x3 layout
- StatusDisplay: Game-specific messaging
- App: Game orchestration logic

## File Structure


src/
├── components/
│   ├── App/
│   │   ├── App.jsx|vue|js
│   │   ├── App.module.css
│   │   └── index.js
│   ├── Board/
│   │   ├── Board.jsx|vue|js
│   │   ├── Board.module.css
│   │   └── index.js
│   ├── Cell/
│   │   ├── Cell.jsx|vue|js
│   │   ├── Cell.module.css
│   │   └── index.js
│   ├── StatusDisplay/
│   │   ├── StatusDisplay.jsx|vue|js
│   │   ├── StatusDisplay.module.css
│   │   └── index.js
│   └── RestartButton/
│       ├── RestartButton.jsx|vue|js
│       ├── RestartButton.module.css
│       └── index.js
├── utils/
│   └── gameLogic.js
└── main.js


## Testing Strategy

**Unit Tests**:
- Cell: Render states, click handling
- Board: Grid rendering, event delegation
- StatusDisplay: Conditional rendering
- RestartButton: Click behavior

**Integration Tests**:
- App: Full game flow, win conditions, draw scenarios

## Performance Considerations

- **Memoization**: Cell components should be memoized (React.memo/Vue computed)
- **Event Handlers**: Use stable references (useCallback/methods)
- **Minimal Re-renders**: Only affected cells re-render on state change

## Accessibility

- Cell: `role="button"`, `aria-label="Cell {index}"`
- Board: `role="grid"`, keyboard navigation support
- StatusDisplay: `role="status"`, `aria-live="polite"`
- RestartButton: Semantic `<button>` element

## Design Decisions

1. **Single Source of Truth**: App component owns all state to prevent synchronization issues
2. **Presentational Components**: Board, Cell, StatusDisplay, RestartButton are pure for testability
3. **Prop Drilling Acceptable**: Shallow hierarchy (max 2 levels) makes prop drilling manageable
4. **Component Colocation**: Each component in own directory with styles for maintainability
5. **Index Exports**: Simplify imports and allow implementation swapping