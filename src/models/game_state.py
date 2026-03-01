import uuid

games_db = {}

class GameState:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.board = [None] * 9
        self.current_player = 'X'
        self.status = 'in_progress'
        self.winner = None
    
    def restart(self):
        """Reset the game to initial state while keeping the same game ID"""
        self.board = [None] * 9
        self.current_player = 'X'
        self.status = 'in_progress'
        self.winner = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'board': self.board,
            'current_player': self.current_player,
            'status': self.status,
            'winner': self.winner
        }
