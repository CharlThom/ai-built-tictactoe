import uuid
from datetime import datetime

class GameState:
    """Represents the state of a TicTacToe game"""
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.board = [None] * 9  # 3x3 board as flat array
        self.current_player = 'X'  # X always starts
        self.status = 'in_progress'  # in_progress, won, draw
        self.winner = None
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self):
        """Convert game state to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'board': self.board,
            'current_player': self.current_player,
            'status': self.status,
            'winner': self.winner,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
