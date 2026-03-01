import React, { useState } from 'react';
import styles from './TicTacToe.module.css';

type Player = 'X' | 'O' | null;

const TicTacToe: React.FC = () => {
  const [board, setBoard] = useState<Player[]>(Array(9).fill(null));
  const [isXNext, setIsXNext] = useState(true);
  const [winner, setWinner] = useState<Player>(null);
  const [winningLine, setWinningLine] = useState<number[]>([]);

  const calculateWinner = (squares: Player[]): { winner: Player; line: number[] } => {
    const lines = [
      [0, 1, 2],
      [3, 4, 5],
      [6, 7, 8],
      [0, 3, 6],
      [1, 4, 7],
      [2, 5, 8],
      [0, 4, 8],
      [2, 4, 6],
    ];

    for (const [a, b, c] of lines) {
      if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
        return { winner: squares[a], line: [a, b, c] };
      }
    }
    return { winner: null, line: [] };
  };

  const handleClick = (index: number) => {
    if (board[index] || winner) return;

    const newBoard = [...board];
    newBoard[index] = isXNext ? 'X' : 'O';
    setBoard(newBoard);

    const result = calculateWinner(newBoard);
    if (result.winner) {
      setWinner(result.winner);
      setWinningLine(result.line);
    } else {
      setIsXNext(!isXNext);
    }
  };

  const resetGame = () => {
    setBoard(Array(9).fill(null));
    setIsXNext(true);
    setWinner(null);
    setWinningLine([]);
  };

  const getStatus = () => {
    if (winner) {
      return `Winner: ${winner}`;
    }
    if (board.every((cell) => cell !== null)) {
      return "It's a Draw!";
    }
    return `Next Player: ${isXNext ? 'X' : 'O'}`;
  };

  return (
    <div className={styles.container}>
      <div className={styles.statusArea}>
        <div className={styles.status}>{getStatus()}</div>
        <button className={styles.resetButton} onClick={resetGame}>
          Reset Game
        </button>
      </div>
      <div className={styles.gameBoard}>
        {board.map((cell, index) => (
          <button
            key={index}
            className={`${styles.cell} ${winningLine.includes(index) ? styles.winner : ''}`}
            onClick={() => handleClick(index)}
            disabled={!!cell || !!winner}
          >
            {cell && (
              <span className={cell === 'X' ? styles.symbolX : styles.symbolO}>
                {cell}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};

export default TicTacToe;