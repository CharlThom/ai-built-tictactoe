from typing import Dict, Any, Tuple
import re

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class GameValidator:
    """Validates input for TicTacToe game endpoints"""
    
    VALID_PLAYERS = ['X', 'O']
    BOARD_SIZE = 9
    VALID_POSITIONS = list(range(BOARD_SIZE))
    
    @staticmethod
    def validate_game_id(game_id: str) -> str:
        """Validate game ID format"""
        if not game_id:
            raise ValidationError("Game ID is required", 400)
        
        if not isinstance(game_id, str):
            raise ValidationError("Game ID must be a string", 400)
        
        if len(game_id) < 1 or len(game_id) > 100:
            raise ValidationError("Game ID must be between 1 and 100 characters", 400)
        
        # Allow alphanumeric, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', game_id):
            raise ValidationError("Game ID contains invalid characters", 400)
        
        return game_id
    
    @staticmethod
    def validate_new_game_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate POST /game request body"""
        if data is None:
            data = {}
        
        if not isinstance(data, dict):
            raise ValidationError("Request body must be a JSON object", 400)
        
        # Validate starting player if provided
        starting_player = data.get('starting_player', 'X')
        if starting_player not in GameValidator.VALID_PLAYERS:
            raise ValidationError(
                f"Invalid starting player. Must be one of {GameValidator.VALID_PLAYERS}",
                400
            )
        
        return {
            'starting_player': starting_player
        }
    
    @staticmethod
    def validate_move_request(data: Dict[str, Any]) -> Tuple[int, str]:
        """Validate move request (PUT /game/:id/move)"""
        if not data or not isinstance(data, dict):
            raise ValidationError("Request body must be a JSON object", 400)
        
        # Validate position
        if 'position' not in data:
            raise ValidationError("Position is required", 400)
        
        position = data['position']
        
        if not isinstance(position, int):
            raise ValidationError("Position must be an integer", 400)
        
        if position not in GameValidator.VALID_POSITIONS:
            raise ValidationError(
                f"Position must be between 0 and {GameValidator.BOARD_SIZE - 1}",
                400
            )
        
        # Validate player
        if 'player' not in data:
            raise ValidationError("Player is required", 400)
        
        player = data['player']
        
        if player not in GameValidator.VALID_PLAYERS:
            raise ValidationError(
                f"Invalid player. Must be one of {GameValidator.VALID_PLAYERS}",
                400
            )
        
        return position, player
    
    @staticmethod
    def validate_game_state(game_state: Dict[str, Any]) -> None:
        """Validate game state structure"""
        if not game_state:
            raise ValidationError("Game not found", 404)
        
        required_fields = ['board', 'current_player', 'status']
        for field in required_fields:
            if field not in game_state:
                raise ValidationError(f"Invalid game state: missing {field}", 500)
        
        # Validate board
        board = game_state['board']
        if not isinstance(board, list) or len(board) != GameValidator.BOARD_SIZE:
            raise ValidationError("Invalid game state: board must be a list of 9 elements", 500)
        
        # Validate current player
        if game_state['current_player'] not in GameValidator.VALID_PLAYERS:
            raise ValidationError("Invalid game state: invalid current player", 500)
        
        # Validate status
        valid_statuses = ['in_progress', 'X_wins', 'O_wins', 'draw']
        if game_state['status'] not in valid_statuses:
            raise ValidationError("Invalid game state: invalid status", 500)
    
    @staticmethod
    def validate_move_legality(game_state: Dict[str, Any], position: int, player: str) -> None:
        """Validate if a move is legal in the current game state"""
        # Check if game is already finished
        if game_state['status'] != 'in_progress':
            raise ValidationError("Game is already finished", 400)
        
        # Check if it's the correct player's turn
        if game_state['current_player'] != player:
            raise ValidationError(
                f"It's not {player}'s turn. Current player is {game_state['current_player']}",
                400
            )
        
        # Check if position is already occupied
        if game_state['board'][position] is not None:
            raise ValidationError(f"Position {position} is already occupied", 400)