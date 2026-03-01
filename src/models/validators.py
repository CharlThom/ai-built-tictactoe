"""Data model validators for TicTacToe database constraints."""

from typing import List, Any
from enum import Enum


class CellState(Enum):
    """Valid cell states for board positions."""
    EMPTY = "empty"
    X = "X"
    O = "O"


class GameStatus(Enum):
    """Valid game status values."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Winner(Enum):
    """Valid winner values."""
    PLAYER1 = "player1"
    PLAYER2 = "player2"
    DRAW = "draw"


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass


class DataModelValidator:
    """Validates data model constraints for TicTacToe entities."""
    
    BOARD_SIZE = 9
    MIN_POSITION = 0
    MAX_POSITION = 8
    VALID_PLAYER_NUMBERS = {1, 2}
    VALID_CELL_STATES = {state.value for state in CellState}
    
    @staticmethod
    def validate_cell_states(cell_states: List[str]) -> bool:
        """
        Validate board cell_states array.
        
        Constraints:
        - Must be exactly 9 elements
        - Each element must be 'empty', 'X', or 'O'
        
        Args:
            cell_states: List of cell state strings
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(cell_states, list):
            raise ValidationError("cell_states must be a list")
        
        if len(cell_states) != DataModelValidator.BOARD_SIZE:
            raise ValidationError(
                f"cell_states must have exactly {DataModelValidator.BOARD_SIZE} elements, "
                f"got {len(cell_states)}"
            )
        
        for idx, state in enumerate(cell_states):
            if state not in DataModelValidator.VALID_CELL_STATES:
                raise ValidationError(
                    f"Invalid cell state '{state}' at position {idx}. "
                    f"Must be one of: {DataModelValidator.VALID_CELL_STATES}"
                )
        
        return True
    
    @staticmethod
    def validate_position(position: int) -> bool:
        """
        Validate move position.
        
        Constraints:
        - Must be integer in range 0-8 (inclusive)
        
        Args:
            position: Board position
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(position, int):
            raise ValidationError(f"Position must be an integer, got {type(position).__name__}")
        
        if position < DataModelValidator.MIN_POSITION or position > DataModelValidator.MAX_POSITION:
            raise ValidationError(
                f"Position must be between {DataModelValidator.MIN_POSITION} and "
                f"{DataModelValidator.MAX_POSITION}, got {position}"
            )
        
        return True
    
    @staticmethod
    def validate_unique_position_per_game(game_id: int, position: int, existing_moves: List[dict]) -> bool:
        """
        Validate that position hasn't been played in this game.
        
        Constraint: UNIQUE(game_id, position)
        
        Args:
            game_id: Game identifier
            position: Board position
            existing_moves: List of existing moves for the game
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If position already played
        """
        for move in existing_moves:
            if move.get('game_id') == game_id and move.get('position') == position:
                raise ValidationError(
                    f"Position {position} has already been played in game {game_id}"
                )
        
        return True
    
    @staticmethod
    def validate_player_number(player_number: int) -> bool:
        """
        Validate player number.
        
        Constraint: player_number IN (1, 2)
        
        Args:
            player_number: Player number
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if player_number not in DataModelValidator.VALID_PLAYER_NUMBERS:
            raise ValidationError(
                f"Player number must be 1 or 2, got {player_number}"
            )
        
        return True
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """
        Validate player/move symbol.
        
        Constraint: symbol IN ('X', 'O')
        
        Args:
            symbol: Player symbol
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        valid_symbols = {CellState.X.value, CellState.O.value}
        if symbol not in valid_symbols:
            raise ValidationError(
                f"Symbol must be 'X' or 'O', got '{symbol}'"
            )
        
        return True
    
    @staticmethod
    def validate_game_winner(status: str, winner: Any) -> bool:
        """
        Validate game winner based on status.
        
        Business rule: winner can only be set when status = 'completed'
        
        Args:
            status: Game status
            winner: Winner value
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if status == GameStatus.IN_PROGRESS.value and winner is not None:
            raise ValidationError(
                "Winner must be NULL when game status is 'in_progress'"
            )
        
        if status == GameStatus.COMPLETED.value and winner is None:
            raise ValidationError(
                "Winner must be set when game status is 'completed'"
            )
        
        return True


# Example usage and tests
if __name__ == "__main__":
    validator = DataModelValidator()
    
    # Test valid cell states
    try:
        valid_cells = ["empty", "X", "O", "empty", "X", "empty", "O", "empty", "empty"]
        validator.validate_cell_states(valid_cells)
        print("✓ Valid cell states passed")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test invalid cell states - wrong length
    try:
        invalid_cells = ["empty", "X", "O"]
        validator.validate_cell_states(invalid_cells)
        print("✗ Should have failed for wrong length")
    except ValidationError:
        print("✓ Correctly rejected wrong length")
    
    # Test invalid cell states - invalid value
    try:
        invalid_cells = ["empty", "X", "Y", "empty", "X", "empty", "O", "empty", "empty"]
        validator.validate_cell_states(invalid_cells)
        print("✗ Should have failed for invalid value")
    except ValidationError:
        print("✓ Correctly rejected invalid cell value")
    
    # Test valid position
    try:
        validator.validate_position(5)
        print("✓ Valid position passed")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test invalid position - out of range
    try:
        validator.validate_position(9)
        print("✗ Should have failed for position > 8")
    except ValidationError:
        print("✓ Correctly rejected position > 8")
    
    # Test invalid position - negative
    try:
        validator.validate_position(-1)
        print("✗ Should have failed for negative position")
    except ValidationError:
        print("✓ Correctly rejected negative position")
    
    # Test unique position constraint
    try:
        existing = [{"game_id": 1, "position": 4}]
        validator.validate_unique_position_per_game(1, 5, existing)
        print("✓ Unique position passed")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test duplicate position
    try:
        existing = [{"game_id": 1, "position": 4}]
        validator.validate_unique_position_per_game(1, 4, existing)
        print("✗ Should have failed for duplicate position")
    except ValidationError:
        print("✓ Correctly rejected duplicate position")
