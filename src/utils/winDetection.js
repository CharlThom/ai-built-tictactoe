/**
 * Check if there's a winner on the TicTacToe board
 * @param {Array} board - 1D array of 9 elements representing the 3x3 board
 * @returns {Object} - { winner: 'X' | 'O' | null, winningLine: Array | null }
 */
export const checkWinner = (board) => {
  // Define all winning combinations (indices for 3x3 grid)
  const winningCombinations = [
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
  ];

  // Check each winning combination
  for (const combination of winningCombinations) {
    const [a, b, c] = combination;
    
    if (
      board[a] &&
      board[a] === board[b] &&
      board[a] === board[c]
    ) {
      return {
        winner: board[a],
        winningLine: combination
      };
    }
  }

  // Check for draw (board full with no winner)
  const isDraw = board.every(cell => cell !== null);
  
  if (isDraw) {
    return {
      winner: 'draw',
      winningLine: null
    };
  }

  // Game still in progress
  return {
    winner: null,
    winningLine: null
  };
};

/**
 * Check if a specific player has won
 * @param {Array} board - 1D array of 9 elements
 * @param {string} player - 'X' or 'O'
 * @returns {boolean}
 */
export const hasPlayerWon = (board, player) => {
  const result = checkWinner(board);
  return result.winner === player;
};

/**
 * Check if the game is over (win or draw)
 * @param {Array} board - 1D array of 9 elements
 * @returns {boolean}
 */
export const isGameOver = (board) => {
  const result = checkWinner(board);
  return result.winner !== null;
};