/**
 * Core game logic utilities for TicTacToe
 */

import type { Board, Player, WinCondition, GameState } from '../types/game.types';
import { WIN_CONDITIONS, INITIAL_GAME_STATE } from '../types/game.types';

/**
 * Check if a player has won the game
 * @param board - Current board state
 * @param player - Player to check for win
 * @returns Winning line if player won, null otherwise
 */
export function checkWinner(board: Board, player: Player): WinCondition | null {
  for (const condition of WIN_CONDITIONS) {
    const [a, b, c] = condition;
    if (board[a] === player && board[b] === player && board[c] === player) {
      return condition;
    }
  }
  return null;
}

/**
 * Check if the board is full (draw condition)
 * @param board - Current board state
 * @returns True if board is full, false otherwise
 */
export function isBoardFull(board: Board): boolean {
  return board.every(cell => cell !== null);
}

/**
 * Make a move on the board
 * @param state - Current game state
 * @param cellIndex - Index of cell to mark (0-8)
 * @returns New game state after move
 */
export function makeMove(state: GameState, cellIndex: number): GameState {
  // Validate move
  if (state.status !== 'playing' || state.board[cellIndex] !== null) {
    return state;
  }

  // Create new board with move
  const newBoard = [...state.board] as Board;
  newBoard[cellIndex] = state.currentPlayer;

  // Check for winner
  const winningLine = checkWinner(newBoard, state.currentPlayer);
  
  if (winningLine) {
    return {
      ...state,
      board: newBoard,
      status: 'won',
      winner: state.currentPlayer,
      winningLine,
      moveCount: state.moveCount + 1
    };
  }

  // Check for draw
  if (isBoardFull(newBoard)) {
    return {
      ...state,
      board: newBoard,
      status: 'draw',
      winner: null,
      winningLine: null,
      moveCount: state.moveCount + 1
    };
  }

  // Continue game with next player
  return {
    ...state,
    board: newBoard,
    currentPlayer: state.currentPlayer === 'X' ? 'O' : 'X',
    status: 'playing',
    moveCount: state.moveCount + 1
  };
}

/**
 * Reset game to initial state
 * @returns Fresh game state
 */
export function resetGame(): GameState {
  return { ...INITIAL_GAME_STATE, board: [...INITIAL_GAME_STATE.board] as Board };
}