import { useState } from 'react';
import './TicTacToe.css';

const TicTacToe = () => {
  const [board, setBoard] = useState(Array(9).fill(null));
  const [isXNext, setIsXNext] = useState(true);
  const [gameOver, setGameOver] = useState(false);
  const [winner, setWinner] = useState(null);

  const calculateWinner = (squares) => {
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
    for (let i = 0; i < lines.length; i++) {
      const [a, b, c] = lines[i];
      if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
        return squares[a];
      }
    }
    return null;
  };

  const handleCellClick = (index) => {
    // Validation: Check if cell is already filled
    if (board[index]) {
      return;
    }

    // Validation: Check if game is over
    if (gameOver) {
      return;
    }

    // Create new board with player's move
    const newBoard = [...board];
    newBoard[index] = isXNext ? 'X' : 'O';
    setBoard(newBoard);

    // Check for winner
    const winnerPlayer = calculateWinner(newBoard);
    if (winnerPlayer) {
      setWinner(winnerPlayer);
      setGameOver(true);
      return;
    }

    // Check for draw
    if (newBoard.every(cell => cell !== null)) {
      setGameOver(true);
      return;
    }

    // Switch player turn
    setIsXNext(!isXNext);
  };

  const resetGame = () => {
    setBoard(Array(9).fill(null));
    setIsXNext(true);
    setGameOver(false);
    setWinner(null);
  };

  const getStatus = () => {
    if (winner) {
      return `Winner: ${winner}`;
    }
    if (gameOver) {
      return "It's a Draw!";
    }
    return `Current Player: ${isXNext ? 'X' : 'O'}`;
  };

  return (
    <div className="game-container">
      <h1>Tic Tac Toe</h1>
      <div className="status">{getStatus()}</div>
      <div className="board">
        {board.map((cell, index) => (
          <div
            key={index}
            className={`cell ${cell ? 'filled' : ''} ${cell === 'X' ? 'x' : ''} ${cell === 'O' ? 'o' : ''}`}
            onClick={() => handleCellClick(index)}
          >
            {cell}
          </div>
        ))}
      </div>
      <button className="reset-button" onClick={resetGame}>
        Reset Game
      </button>
    </div>
  );
};

export default TicTacToe;