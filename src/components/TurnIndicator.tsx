import React from 'react';
import './TurnIndicator.css';

interface TurnIndicatorProps {
  currentPlayer: 'X' | 'O';
  winner: 'X' | 'O' | 'draw' | null;
  onReset?: () => void;
}

const TurnIndicator: React.FC<TurnIndicatorProps> = ({ currentPlayer, winner, onReset }) => {
  const getStatusMessage = () => {
    if (winner === 'draw') {
      return "It's a Draw!";
    }
    if (winner) {
      return `Player ${winner} Wins!`;
    }
    return `Current Turn: Player ${currentPlayer}`;
  };

  const getStatusClass = () => {
    if (winner) return 'game-over';
    return currentPlayer === 'X' ? 'player-x' : 'player-o';
  };

  return (
    <div className="turn-indicator">
      <div className={`status-message ${getStatusClass()}`}>
        <span className="status-text">{getStatusMessage()}</span>
        {currentPlayer && !winner && (
          <span className={`player-symbol symbol-${currentPlayer.toLowerCase()}`}>
            {currentPlayer}
          </span>
        )}
      </div>
      {winner && onReset && (
        <button className="reset-button" onClick={onReset}>
          Play Again
        </button>
      )}
    </div>
  );
};

export default TurnIndicator;