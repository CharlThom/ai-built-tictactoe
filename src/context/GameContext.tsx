import React, { createContext, useContext, useReducer, useCallback, useMemo } from 'react';

// Types
type Player = 'X' | 'O';
type CellValue = Player | null;
type GameStatus = 'idle' | 'playing' | 'finished';
type Winner = Player | 'draw' | null;

interface GameState {
  board: CellValue[];
  currentPlayer: Player;
  winner: Winner;
  gameStatus: GameStatus;
  moveHistory: number[];
}

type GameAction =
  | { type: 'MAKE_MOVE'; payload: number }
  | { type: 'RESET_GAME' }
  | { type: 'UNDO_MOVE' };

interface GameContextValue {
  state: GameState;
  makeMove: (index: number) => void;
  resetGame: () => void;
  undoMove: () => void;
}

// Winning combinations
const WINNING_COMBINATIONS = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
  [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
  [0, 4, 8], [2, 4, 6]             // Diagonals
];

// Helper: Check winner
const checkWinner = (board: CellValue[]): Winner => {
  for (const [a, b, c] of WINNING_COMBINATIONS) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return board[a] as Player;
    }
  }
  return board.every(cell => cell !== null) ? 'draw' : null;
};

// Initial state
const initialState: GameState = {
  board: Array(9).fill(null),
  currentPlayer: 'X',
  winner: null,
  gameStatus: 'idle',
  moveHistory: []
};

// Reducer
const gameReducer = (state: GameState, action: GameAction): GameState => {
  switch (action.type) {
    case 'MAKE_MOVE': {
      const index = action.payload;
      
      // Validation
      if (state.board[index] !== null || state.gameStatus === 'finished') {
        return state;
      }

      const newBoard = [...state.board];
      newBoard[index] = state.currentPlayer;
      
      const winner = checkWinner(newBoard);
      const gameStatus = winner ? 'finished' : 'playing';
      const nextPlayer = state.currentPlayer === 'X' ? 'O' : 'X';

      return {
        ...state,
        board: newBoard,
        currentPlayer: nextPlayer,
        winner,
        gameStatus,
        moveHistory: [...state.moveHistory, index]
      };
    }

    case 'RESET_GAME':
      return initialState;

    case 'UNDO_MOVE': {
      if (state.moveHistory.length === 0) return state;

      const newHistory = [...state.moveHistory];
      const lastMove = newHistory.pop()!;
      
      const newBoard = [...state.board];
      newBoard[lastMove] = null;
      
      const previousPlayer = state.currentPlayer === 'X' ? 'O' : 'X';
      const winner = checkWinner(newBoard);

      return {
        ...state,
        board: newBoard,
        currentPlayer: previousPlayer,
        winner,
        gameStatus: winner ? 'finished' : newHistory.length === 0 ? 'idle' : 'playing',
        moveHistory: newHistory
      };
    }

    default:
      return state;
  }
};

// Context
const GameContext = createContext<GameContextValue | undefined>(undefined);

// Provider
export const GameProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(gameReducer, initialState);

  const makeMove = useCallback((index: number) => {
    dispatch({ type: 'MAKE_MOVE', payload: index });
  }, []);

  const resetGame = useCallback(() => {
    dispatch({ type: 'RESET_GAME' });
  }, []);

  const undoMove = useCallback(() => {
    dispatch({ type: 'UNDO_MOVE' });
  }, []);

  const value = useMemo(
    () => ({ state, makeMove, resetGame, undoMove }),
    [state, makeMove, resetGame, undoMove]
  );

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};

// Custom hook
export const useGame = (): GameContextValue => {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within GameProvider');
  }
  return context;
};

export type { GameState, Player, CellValue, Winner, GameStatus };