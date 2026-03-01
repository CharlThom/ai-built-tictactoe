import React from 'react';
import { useGameState } from '../hooks/useGameState';

const TicTacToe: React.FC = () => {
  const { board, currentPlayer, winner, isDraw, isGameOver, makeMove, resetGame } = useGameState();

  const handleCellClick = (index: number) => {
    makeMove(index);
  };

  const getStatusMessage = () => {
    if (winner) {
      return `Player ${winner} wins!`;
    }
    if (isDraw) {
      return "It's a draw!";
    }
    return `Current player: ${currentPlayer}`;
  };

  return (
    <div className="game-container">
      <div className="game-status">
        <h2>{getStatusMessage()}</h2>
      </div>
      
      <div className="game-board">
        {board.map((cell, index) => (
          <div
            key={index}
            className={`cell ${cell ? 'filled' : ''}`}
            onClick={() => handleCellClick(index)}
          >
            {cell && <span className={`symbol symbol-${cell.toLowerCase()}`}>{cell}</span>}
          </div>
        ))}
      </div>

      {isGameOver && (
        <div className="game-controls">
          <button className="reset-button" onClick={resetGame}>
            Play Again
          </button>
        </div>
      )}
    </div>
  );
};

export default TicTacToe;