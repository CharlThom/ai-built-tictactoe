import { useState, useEffect } from 'react';
import './TicTacToe.css';

const TicTacToe = () => {
  const [board, setBoard] = useState(Array(9).fill(null));
  const [isXNext, setIsXNext] = useState(true);
  const [gameStatus, setGameStatus] = useState('Next player: X');
  const [gameOver, setGameOver] = useState(false);

  const checkWinner = (squares) => {
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

  const checkDraw = (squares) => {
    return squares.every(cell => cell !== null);
  };

  useEffect(() => {
    const winner = checkWinner(board);
    if (winner) {
      setGameStatus(`Winner: ${winner}`);
      setGameOver(true);
    } else if (checkDraw(board)) {
      setGameStatus('Game Draw!');
      setGameOver(true);
    } else {
      setGameStatus(`Next player: ${isXNext ? 'X' : 'O'}`);
    }
  }, [board, isXNext]);

  const handleClick = (index) => {
    if (board[index] || gameOver) return;

    const newBoard = [...board];
    newBoard[index] = isXNext ? 'X' : 'O';
    setBoard(newBoard);
    setIsXNext(!isXNext);
  };

  const resetGame = () => {
    setBoard(Array(9).fill(null));
    setIsXNext(true);
    setGameOver(false);
    setGameStatus('Next player: X');
  };

  return (
    <div className="game-container">
      <h1>Tic Tac Toe</h1>
      <div className="status-display">
        <p className={gameOver ? 'game-over' : ''}>{gameStatus}</p>
      </div>
      <div className="board">
        {board.map((cell, index) => (
          <div
            key={index}
            className={`cell ${cell ? 'filled' : ''}`}
            onClick={() => handleClick(index)}
          >
            {cell && <span className={`symbol ${cell.toLowerCase()}`}>{cell}</span>}
          </div>
        ))}
      </div>
      <button className="reset-button" onClick={resetGame}>
        New Game
      </button>
    </div>
  );
};

export default TicTacToe;