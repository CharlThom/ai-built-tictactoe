from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base


class GameStatus(enum.Enum):
    """Enum for game status"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class GameWinner(enum.Enum):
    """Enum for game winner"""
    PLAYER1 = "player1"
    PLAYER2 = "player2"
    DRAW = "draw"


class Game(Base):
    """Game entity representing a TicTacToe game"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Enum(GameStatus), nullable=False, default=GameStatus.IN_PROGRESS)
    winner = Column(Enum(GameWinner), nullable=True, default=None)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Board entity
    board = relationship("Board", back_populates="game", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game(id={self.id}, status={self.status.value}, winner={self.winner.value if self.winner else None})>"

    def to_dict(self):
        """Convert game to dictionary representation"""
        return {
            "id": self.id,
            "status": self.status.value,
            "winner": self.winner.value if self.winner else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }