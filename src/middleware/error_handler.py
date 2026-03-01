"""Error handling middleware for TicTacToe API."""

from datetime import datetime
from typing import Dict, Any, Optional
from flask import jsonify, request
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class TicTacToeError(Exception):
    """Base exception for TicTacToe errors."""
    
    def __init__(self, code: str, message: str, status_code: int = 400, details: Optional[Dict] = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class CellOccupiedError(TicTacToeError):
    """Raised when attempting to place mark in occupied cell."""
    
    def __init__(self, row: int, col: int, occupied_by: str):
        super().__init__(
            code="CELL_OCCUPIED",
            message=f"Cell at position ({row},{col}) is already occupied",
            status_code=422,
            details={
                "position": {"row": row, "col": col},
                "occupied_by": occupied_by
            }
        )


class InvalidPositionError(TicTacToeError):
    """Raised when position is out of bounds."""
    
    def __init__(self, row: int, col: int):
        super().__init__(
            code="INVALID_POSITION",
            message="Position must be within bounds (0-2 for row and col)",
            status_code=400,
            details={
                "provided": {"row": row, "col": col},
                "valid_range": {"min": 0, "max": 2}
            }
        )


class WrongTurnError(TicTacToeError):
    """Raised when player attempts move out of turn."""
    
    def __init__(self, attempted_player: str, current_turn: str):
        super().__init__(
            code="WRONG_TURN",
            message=f"It is not player {attempted_player}'s turn",
            status_code=409,
            details={
                "attempted_player": attempted_player,
                "current_turn": current_turn
            }
        )


class GameFinishedError(TicTacToeError):
    """Raised when attempting move on finished game."""
    
    def __init__(self, game_status: str, winner: Optional[str] = None):
        super().__init__(
            code="GAME_FINISHED",
            message="Cannot make move - game has already finished",
            status_code=409,
            details={
                "game_status": game_status,
                "winner": winner
            }
        )


class GameNotFoundError(TicTacToeError):
    """Raised when game ID doesn't exist."""
    
    def __init__(self, game_id: str):
        super().__init__(
            code="GAME_NOT_FOUND",
            message=f"Game with ID '{game_id}' does not exist",
            status_code=404,
            details={"game_id": game_id}
        )


class InvalidPlayerError(TicTacToeError):
    """Raised when player identifier is invalid."""
    
    def __init__(self, provided: str):
        super().__init__(
            code="INVALID_PLAYER",
            message="Player must be 'X' or 'O'",
            status_code=400,
            details={
                "provided": provided,
                "valid_values": ["X", "O"]
            }
        )


class MissingFieldError(TicTacToeError):
    """Raised when required field is missing."""
    
    def __init__(self, missing_fields: list, required_fields: list):
        super().__init__(
            code="MISSING_FIELD",
            message=f"Required field(s) {', '.join(missing_fields)} missing",
            status_code=400,
            details={
                "missing_fields": missing_fields,
                "required_fields": required_fields
            }
        )


class InvalidJSONError(TicTacToeError):
    """Raised when request contains invalid JSON."""
    
    def __init__(self, parse_error: str):
        super().__init__(
            code="INVALID_JSON",
            message="Request body contains invalid JSON",
            status_code=400,
            details={"parse_error": parse_error}
        )


def format_error_response(error: TicTacToeError) -> Dict[str, Any]:
    """Format error as standardized JSON response."""
    return {
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }


def handle_errors(f):
    """Decorator to handle errors in route handlers."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except TicTacToeError as e:
            logger.warning(
                f"TicTacToe error: {e.code}",
                extra={
                    "error_code": e.code,
                    "status_code": e.status_code,
                    "details": e.details,
                    "path": request.path,
                    "method": request.method
                }
            )
            return jsonify(format_error_response(e)), e.status_code
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            error = TicTacToeError(
                code="VALIDATION_ERROR",
                message=str(e),
                status_code=400
            )
            return jsonify(format_error_response(error)), 400
        except Exception as e:
            logger.exception("Unexpected error occurred")
            error = TicTacToeError(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                status_code=500,
                details={"error_type": type(e).__name__}
            )
            return jsonify(format_error_response(error)), 500
    return decorated_function


def validate_move_request(data: Dict[str, Any]) -> None:
    """Validate move request data and raise appropriate errors."""
    required_fields = ["game_id", "player", "position"]
    missing = [field for field in required_fields if field not in data]
    
    if missing:
        raise MissingFieldError(missing, required_fields)
    
    # Validate player
    player = data.get("player")
    if player not in ["X", "O"]:
        raise InvalidPlayerError(player)
    
    # Validate position
    position = data.get("position")
    if not isinstance(position, dict) or "row" not in position or "col" not in position:
        raise TicTacToeError(
            code="INVALID_POSITION_FORMAT",
            message="Position must be an object with 'row' and 'col' properties",
            status_code=400
        )
    
    row, col = position.get("row"), position.get("col")
    
    if not isinstance(row, int) or not isinstance(col, int):
        raise TicTacToeError(
            code="INVALID_POSITION_TYPE",
            message="Row and col must be integers",
            status_code=400
        )
    
    if not (0 <= row <= 2 and 0 <= col <= 2):
        raise InvalidPositionError(row, col)


def register_error_handlers(app):
    """Register global error handlers for Flask app."""
    
    @app.errorhandler(404)
    def not_found(e):
        error = TicTacToeError(
            code="ENDPOINT_NOT_FOUND",
            message="The requested endpoint does not exist",
            status_code=404,
            details={"path": request.path}
        )
        return jsonify(format_error_response(error)), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        error = TicTacToeError(
            code="METHOD_NOT_ALLOWED",
            message=f"Method {request.method} not allowed for this endpoint",
            status_code=405,
            details={"method": request.method, "path": request.path}
        )
        return jsonify(format_error_response(error)), 405
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Internal server error")
        error = TicTacToeError(
            code="INTERNAL_ERROR",
            message="An internal server error occurred",
            status_code=500
        )
        return jsonify(format_error_response(error)), 500