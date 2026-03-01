from enum import Enum
from typing import List, Optional


class Player(Enum):
    """Enum representing players in the game."""
    X = "X"
    O = "O"


class GameStatus(Enum):
    """Enum representing the current status of the game."""
    IN_PROGRESS = "in_progress"
    X_WINS = "x_wins"
    O_WINS = "o_wins"
    DRAW = "draw"


class GameState:
    """Core game state model for TicTacToe."""
    
    def __init__(self):
        """Initialize a new game with empty board."""
        self.board: List[Optional[Player]] = [None] * 9
        self.current_player: Player = Player.X
        self.status: GameStatus = GameStatus.IN_PROGRESS
        self.winner: Optional[Player] = None
    
    def make_move(self, position: int) -> bool:
        """Make a move at the specified position (0-8).
        
        Args:
            position: Board position (0-8)
            
        Returns:
            True if move was valid and made, False otherwise
        """
        if not self._is_valid_move(position):
            return False
        
        self.board[position] = self.current_player
        self._update_game_status()
        
        if self.status == GameStatus.IN_PROGRESS:
            self._switch_player()
        
        return True
    
    def _is_valid_move(self, position: int) -> bool:
        """Check if a move is valid."""
        if self.status != GameStatus.IN_PROGRESS:
            return False
        if position < 0 or position > 8:
            return False
        if self.board[position] is not None:
            return False
        return True
    
    def _switch_player(self):
        """Switch to the other player."""
        self.current_player = Player.O if self.current_player == Player.X else Player.X
    
    def _update_game_status(self):
        """Check and update game status based on current board."""
        winner = self._check_winner()
        if winner:
            self.winner = winner
            self.status = GameStatus.X_WINS if winner == Player.X else GameStatus.O_WINS
        elif self._is_board_full():
            self.status = GameStatus.DRAW
    
    def _check_winner(self) -> Optional[Player]:
        """Check if there's a winner.
        
        Returns:
            Winning player or None
        """
        # Winning combinations (rows, columns, diagonals)
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        
        for combo in winning_combinations:
            if (self.board[combo[0]] is not None and
                self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]]):
                return self.board[combo[0]]
        
        return None
    
    def _is_board_full(self) -> bool:
        """Check if the board is full."""
        return all(cell is not None for cell in self.board)
    
    def reset(self):
        """Reset the game to initial state."""
        self.board = [None] * 9
        self.current_player = Player.X
        self.status = GameStatus.IN_PROGRESS
        self.winner = None
    
    def to_dict(self) -> dict:
        """Convert game state to dictionary representation."""
        return {
            "board": [cell.value if cell else None for cell in self.board],
            "current_player": self.current_player.value,
            "status": self.status.value,
            "winner": self.winner.value if self.winner else None
        }