from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GameStatus(str, Enum):
    """Enumeration for game status"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class GameWinner(str, Enum):
    """Enumeration for game winner"""
    PLAYER1 = "player1"
    PLAYER2 = "player2"
    DRAW = "draw"


class Game(Base):
    """Game entity representing a TicTacToe game session"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(
        SQLEnum(GameStatus),
        nullable=False,
        default=GameStatus.IN_PROGRESS,
        index=True
    )
    winner = Column(
        SQLEnum(GameWinner),
        nullable=True,
        default=None
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Game(id={self.id}, status={self.status}, winner={self.winner})>"

    def to_dict(self):
        """Convert game entity to dictionary"""
        return {
            "id": self.id,
            "status": self.status.value if self.status else None,
            "winner": self.winner.value if self.winner else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }