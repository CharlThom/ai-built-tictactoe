import { useState, useCallback } from 'react';

type Player = 'X' | 'O';
type CellValue = Player | null;
type Board = CellValue[];

interface GameState {
  board: Board;
  currentPlayer: Player;
  winner: Player | null;
  isDraw: boolean;
  isGameOver: boolean;
}

const WINNING_COMBINATIONS = [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8],
  [2, 4, 6],
];

const checkWinner = (board: Board): Player | null => {
  for (const [a, b, c] of WINNING_COMBINATIONS) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return board[a] as Player;
    }
  }
  return null;
};

const checkDraw = (board: Board): boolean => {
  return board.every(cell => cell !== null);
};

export const useGameState = () => {
  const [gameState, setGameState] = useState<GameState>({
    board: Array(9).fill(null),
    currentPlayer: 'X',
    winner: null,
    isDraw: false,
    isGameOver: false,
  });

  const makeMove = useCallback((index: number) => {
    if (gameState.board[index] || gameState.isGameOver) {
      return false;
    }

    const newBoard = [...gameState.board];
    newBoard[index] = gameState.currentPlayer;

    const winner = checkWinner(newBoard);
    const isDraw = !winner && checkDraw(newBoard);
    const isGameOver = !!(winner || isDraw);

    setGameState({
      board: newBoard,
      currentPlayer: gameState.currentPlayer === 'X' ? 'O' : 'X',
      winner,
      isDraw,
      isGameOver,
    });

    return true;
  }, [gameState]);

  const resetGame = useCallback(() => {
    setGameState({
      board: Array(9).fill(null),
      currentPlayer: 'X',
      winner: null,
      isDraw: false,
      isGameOver: false,
    });
  }, []);

  return {
    ...gameState,
    makeMove,
    resetGame,
  };
};

export type { Player, CellValue, Board, GameState };