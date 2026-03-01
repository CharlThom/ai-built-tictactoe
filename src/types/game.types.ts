/**
 * Data structures for TicTacToe game state management
 */

// Cell value type: empty, X, or O
export type CellValue = 'X' | 'O' | null;

// Board is a 3x3 grid
export type Board = [CellValue, CellValue, CellValue, CellValue, CellValue, CellValue, CellValue, CellValue, CellValue];

// Player type
export type Player = 'X' | 'O';

// Game status
export type GameStatus = 'playing' | 'won' | 'draw';

// Win condition: array of winning cell indices
export type WinCondition = [number, number, number];

// All possible winning combinations (rows, columns, diagonals)
export const WIN_CONDITIONS: readonly WinCondition[] = [
  // Rows
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  // Columns
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  // Diagonals
  [0, 4, 8],
  [2, 4, 6]
] as const;

// Complete game state
export interface GameState {
  board: Board;
  currentPlayer: Player;
  status: GameStatus;
  winner: Player | null;
  winningLine: WinCondition | null;
  moveCount: number;
}

// Initial empty board
export const INITIAL_BOARD: Board = [null, null, null, null, null, null, null, null, null];

// Initial game state
export const INITIAL_GAME_STATE: GameState = {
  board: INITIAL_BOARD,
  currentPlayer: 'X',
  status: 'playing',
  winner: null,
  winningLine: null,
  moveCount: 0
};