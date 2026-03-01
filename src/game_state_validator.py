from typing import List, Optional, Tuple
import hashlib
import hmac
import json
from datetime import datetime

class GameStateValidator:
    """Server-side game state validation and tamper protection"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def generate_state_hash(self, game_state: dict) -> str:
        """Generate HMAC hash of game state to prevent tampering"""
        state_string = json.dumps(game_state, sort_keys=True)
        return hmac.new(self.secret_key, state_string.encode(), hashlib.sha256).hexdigest()
    
    def verify_state_hash(self, game_state: dict, provided_hash: str) -> bool:
        """Verify game state hasn't been tampered with"""
        expected_hash = self.generate_state_hash(game_state)
        return hmac.compare_digest(expected_hash, provided_hash)
    
    def validate_move(self, board: List[List[str]], row: int, col: int, 
                     player: str, current_player: str) -> Tuple[bool, Optional[str]]:
        """Validate move server-side to prevent cheating"""
        # Check player turn
        if player != current_player:
            return False, "Not your turn"
        
        # Validate coordinates
        if not (0 <= row < 3 and 0 <= col < 3):
            return False, "Invalid coordinates"
        
        # Check if cell is empty
        if board[row][col] != '':
            return False, "Cell already occupied"
        
        # Validate player symbol
        if player not in ['X', 'O']:
            return False, "Invalid player symbol"
        
        return True, None
    
    def validate_board_state(self, board: List[List[str]], move_count: int) -> Tuple[bool, Optional[str]]:
        """Validate entire board state for consistency"""
        # Count X and O
        x_count = sum(row.count('X') for row in board)
        o_count = sum(row.count('O') for row in board)
        
        # X always goes first, so x_count should be equal or one more than o_count
        if x_count < o_count or x_count > o_count + 1:
            return False, "Invalid board state: incorrect piece count"
        
        # Verify move count matches board
        total_moves = x_count + o_count
        if total_moves != move_count:
            return False, "Move count mismatch"
        
        # Check for multiple winners (impossible in valid game)
        if self._has_multiple_winners(board):
            return False, "Invalid board state: multiple winners"
        
        return True, None
    
    def _has_multiple_winners(self, board: List[List[str]]) -> bool:
        """Check if board has multiple winners (invalid state)"""
        winners = set()
        
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] and row[0] != '':
                winners.add(row[0])
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] and board[0][col] != '':
                winners.add(board[0][col])
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != '':
            winners.add(board[0][0])
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != '':
            winners.add(board[0][2])
        
        return len(winners) > 1
    
    def check_winner(self, board: List[List[str]]) -> Optional[str]:
        """Server-side winner determination"""
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] and row[0] != '':
                return row[0]
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] and board[0][col] != '':
                return board[0][col]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != '':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != '':
            return board[0][2]
        
        return None
    
    def is_draw(self, board: List[List[str]]) -> bool:
        """Check if game is a draw"""
        return all(cell != '' for row in board for cell in row) and self.check_winner(board) is None
    
    def create_secure_game_state(self, game_id: str, board: List[List[str]], 
                                current_player: str, move_count: int, 
                                player_x_id: str, player_o_id: str) -> dict:
        """Create tamper-proof game state with hash"""
        state = {
            'game_id': game_id,
            'board': board,
            'current_player': current_player,
            'move_count': move_count,
            'player_x_id': player_x_id,
            'player_o_id': player_o_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        state['hash'] = self.generate_state_hash(state)
        return state