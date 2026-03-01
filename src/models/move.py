from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from src.models.base import Base


class Move(Base):
    """Move entity representing a single player move in a TicTacToe game."""
    
    __tablename__ = 'moves'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id', ondelete='CASCADE'), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey('players.id', ondelete='CASCADE'), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    game = relationship('Game', back_populates='moves')
    player = relationship('Player', back_populates='moves')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('position >= 0 AND position <= 8', name='valid_position'),
        CheckConstraint('position = CAST(position AS INTEGER)', name='position_is_integer'),
    )
    
    def __repr__(self):
        return f"<Move(id={self.id}, game_id={self.game_id}, player_id={self.player_id}, position={self.position}, timestamp={self.timestamp})>"
    
    def to_dict(self):
        """Convert Move entity to dictionary representation."""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'player_id': self.player_id,
            'position': self.position,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }