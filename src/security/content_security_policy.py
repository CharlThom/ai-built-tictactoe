from typing import Dict, List
from dataclasses import dataclass


@dataclass
class CSPConfig:
    """Content Security Policy configuration for TicTacToe application"""
    
    # Strict CSP directives to prevent XSS
    DIRECTIVES = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'strict-dynamic'"],
        'style-src': ["'self'", "'unsafe-inline'"],  # For inline styles only
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'"],
        'connect-src': ["'self'"],
        'frame-ancestors': ["'none'"],
        'base-uri': ["'self'"],
        'form-action': ["'self'"],
        'object-src': ["'none'"],
        'upgrade-insecure-requests': [],
    }
    
    @classmethod
    def generate_header(cls) -> str:
        """Generate CSP header string"""
        directives = []
        for directive, sources in cls.DIRECTIVES.items():
            if sources:
                directives.append(f"{directive} {' '.join(sources)}")
            else:
                directives.append(directive)
        return '; '.join(directives)
    
    @classmethod
    def get_security_headers(cls) -> Dict[str, str]:
        """Get all security headers for XSS protection"""
        return {
            'Content-Security-Policy': cls.generate_header(),
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        }


class InputValidator:
    """Validates and sanitizes all user inputs"""
    
    ALLOWED_NAME_CHARS = set(
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        ' -_'
    )
    
    @classmethod
    def validate_player_name(cls, name: str) -> tuple[bool, str]:
        """Validate player name and return (is_valid, error_message)"""
        if not name:
            return False, "Player name cannot be empty"
        
        if len(name) > 50:
            return False, "Player name too long (max 50 characters)"
        
        if len(name) < 2:
            return False, "Player name too short (min 2 characters)"
        
        # Check for dangerous characters
        if not all(c in cls.ALLOWED_NAME_CHARS for c in name):
            return False, "Player name contains invalid characters"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            'script', 'javascript', 'onerror', 'onload',
            'eval', 'expression', 'vbscript', 'iframe'
        ]
        
        name_lower = name.lower()
        for pattern in suspicious_patterns:
            if pattern in name_lower:
                return False, f"Player name contains forbidden pattern: {pattern}"
        
        return True, ""
    
    @classmethod
    def validate_game_move(cls, row: int, col: int) -> tuple[bool, str]:
        """Validate game move coordinates"""
        if not isinstance(row, int) or not isinstance(col, int):
            return False, "Invalid move coordinates type"
        
        if not (0 <= row <= 2 and 0 <= col <= 2):
            return False, "Move coordinates out of bounds"
        
        return True, ""
    
    @classmethod
    def sanitize_output(cls, text: str) -> str:
        """Sanitize text for safe output (defense in depth)"""
        import html
        return html.escape(text, quote=True)


class SecurityMiddleware:
    """Middleware to apply security headers and input validation"""
    
    def __init__(self):
        self.csp_config = CSPConfig()
        self.validator = InputValidator()
    
    def apply_security_headers(self, response_headers: Dict[str, str]) -> Dict[str, str]:
        """Apply security headers to response"""
        security_headers = self.csp_config.get_security_headers()
        response_headers.update(security_headers)
        return response_headers
    
    def validate_request_data(self, data: dict) -> tuple[bool, List[str]]:
        """Validate all request data for security issues"""
        errors = []
        
        # Validate player names if present
        for key in ['player1', 'player2', 'playerName']:
            if key in data:
                is_valid, error = self.validator.validate_player_name(data[key])
                if not is_valid:
                    errors.append(f"{key}: {error}")
        
        # Validate move coordinates if present
        if 'row' in data and 'col' in data:
            is_valid, error = self.validator.validate_game_move(data['row'], data['col'])
            if not is_valid:
                errors.append(f"move: {error}")
        
        return len(errors) == 0, errors


# Example usage in Flask/FastAPI
def create_secure_response(data: dict, status_code: int = 200) -> dict:
    """Create a secure API response with proper headers"""
    middleware = SecurityMiddleware()
    
    # Sanitize all string values in response
    sanitized_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized_data[key] = InputValidator.sanitize_output(value)
        else:
            sanitized_data[key] = value
    
    return {
        'data': sanitized_data,
        'headers': middleware.apply_security_headers({}),
        'status': status_code
    }


if __name__ == '__main__':
    # Test CSP generation
    print("Content-Security-Policy:")
    print(CSPConfig.generate_header())
    print("\nAll Security Headers:")
    for header, value in CSPConfig.get_security_headers().items():
        print(f"{header}: {value}")