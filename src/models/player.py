from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from src.models.base import Base


class PlayerNumber(enum.Enum):
    """Enum for player number (1 or 2)"""
    PLAYER_1 = 1
    PLAYER_2 = 2


class PlayerSymbol(enum.Enum):
    """Enum for player symbol (X or O)"""
    X = "X"
    O = "O"


class Player(Base):
    """Player entity representing a player in a TicTacToe game.
    
    Attributes:
        id: Primary key, unique identifier for the player
        player_number: Player number (1 or 2) indicating turn order
        symbol: Player's symbol (X or O) used on the board
        game_id: Foreign key reference to the Game entity
    """
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_number = Column(SQLEnum(PlayerNumber), nullable=False)
    symbol = Column(SQLEnum(PlayerSymbol), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)

    # Relationship to Game entity
    game = relationship("Game", back_populates="players")

    def __repr__(self):
        return f"<Player(id={self.id}, player_number={self.player_number.value}, symbol={self.symbol.value}, game_id={self.game_id})>"

    def to_dict(self):
        """Convert Player entity to dictionary representation."""
        return {
            "id": self.id,
            "player_number": self.player_number.value,
            "symbol": self.symbol.value,
            "game_id": self.game_id
        }