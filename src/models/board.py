from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base


class PlayerTurn(enum.Enum):
    """Enum for tracking whose turn it is"""
    PLAYER1 = "player1"
    PLAYER2 = "player2"


class Board(Base):
    """Board entity representing the game board state"""
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, unique=True)
    cell_states = Column(JSON, nullable=False, default=lambda: [None] * 9)
    current_turn = Column(Enum(PlayerTurn), nullable=False, default=PlayerTurn.PLAYER1)

    # Relationship to Game entity
    game = relationship("Game", back_populates="board")

    def __repr__(self):
        return f"<Board(id={self.id}, game_id={self.game_id}, current_turn={self.current_turn.value})>"

    def to_dict(self):
        """Convert board to dictionary representation"""
        return {
            "id": self.id,
            "game_id": self.game_id,
            "cell_states": self.cell_states,
            "current_turn": self.current_turn.value
        }

    def get_cell(self, position: int) -> str:
        """Get cell value at position (0-8)"""
        if 0 <= position < 9:
            return self.cell_states[position]
        raise ValueError("Position must be between 0 and 8")

    def set_cell(self, position: int, value: str):
        """Set cell value at position (0-8)"""
        if 0 <= position < 9:
            states = self.cell_states.copy()
            states[position] = value
            self.cell_states = states
        else:
            raise ValueError("Position must be between 0 and 8")

    def switch_turn(self):
        """Switch current turn to the other player"""
        self.current_turn = PlayerTurn.PLAYER2 if self.current_turn == PlayerTurn.PLAYER1 else PlayerTurn.PLAYER1