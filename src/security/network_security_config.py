"""Network Security Configuration and Monitoring for TicTacToe"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import json


class NetworkSecurityConfig:
    """Centralized network security configuration"""
    
    # Security headers to include in all responses
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }
    
    # CORS configuration
    CORS_CONFIG = {
        'allowed_origins': ['https://tictactoe.example.com'],  # Update with actual domain
        'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE'],
        'allowed_headers': ['Content-Type', 'Authorization'],
        'expose_headers': ['X-Request-ID'],
        'max_age': 3600,
        'allow_credentials': True
    }
    
    # Rate limiting configuration
    RATE_LIMITS = {
        'default': {'requests': 100, 'window': 60},  # 100 requests per minute
        'auth': {'requests': 5, 'window': 60},  # 5 auth attempts per minute
        'game_move': {'requests': 30, 'window': 60}  # 30 moves per minute
    }
    
    @classmethod
    def get_security_headers(cls) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return cls.SECURITY_HEADERS.copy()
    
    @classmethod
    def validate_origin(cls, origin: str) -> bool:
        """Validate request origin against whitelist"""
        return origin in cls.CORS_CONFIG['allowed_origins']
    
    @classmethod
    def get_cors_headers(cls, origin: str) -> Dict[str, str]:
        """Get CORS headers if origin is allowed"""
        if not cls.validate_origin(origin):
            return {}
        
        return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': ', '.join(cls.CORS_CONFIG['allowed_methods']),
            'Access-Control-Allow-Headers': ', '.join(cls.CORS_CONFIG['allowed_headers']),
            'Access-Control-Expose-Headers': ', '.join(cls.CORS_CONFIG['expose_headers']),
            'Access-Control-Max-Age': str(cls.CORS_CONFIG['max_age']),
            'Access-Control-Allow-Credentials': 'true' if cls.CORS_CONFIG['allow_credentials'] else 'false'
        }


class RequestLogger:
    """Secure request/response logger with PII redaction"""
    
    PII_FIELDS = {'password', 'token', 'session', 'email', 'phone', 'ssn', 'credit_card'}
    
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
    
    def log_request(self, request_data: Dict[str, Any], response_data: Dict[str, Any], 
                   status_code: int, duration_ms: float) -> None:
        """Log request/response with PII redaction"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': self._generate_request_id(request_data),
            'method': request_data.get('method'),
            'endpoint': request_data.get('endpoint'),
            'status_code': status_code,
            'duration_ms': duration_ms,
            'request_body': self._redact_pii(request_data.get('body', {})),
            'response_body': self._redact_pii(response_data),
            'client_ip_hash': self._hash_ip(request_data.get('client_ip', ''))
        }
        self.logs.append(log_entry)
    
    def _redact_pii(self, data: Any) -> Any:
        """Recursively redact PII from data"""
        if isinstance(data, dict):
            return {k: '***REDACTED***' if k.lower() in self.PII_FIELDS 
                   else self._redact_pii(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._redact_pii(item) for item in data]
        return data
    
    def _hash_ip(self, ip: str) -> str:
        """Hash IP address for privacy"""
        return hashlib.sha256(ip.encode()).hexdigest()[:16]
    
    def _generate_request_id(self, request_data: Dict[str, Any]) -> str:
        """Generate unique request ID"""
        data = f"{datetime.utcnow().isoformat()}{request_data.get('endpoint', '')}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs"""
        return self.logs[-limit:]


class DataMinimizationHelper:
    """Helper to ensure minimal data exposure in API responses"""
    
    @staticmethod
    def create_game_response(game_id: str, board: List[List[str]], 
                           current_player: str, status: str, 
                           winner: Optional[str] = None) -> Dict[str, Any]:
        """Create minimal game state response"""
        response = {
            'game_id': game_id,
            'board': board,
            'current_player': current_player,
            'status': status
        }
        if winner:
            response['winner'] = winner
        return response
    
    @staticmethod
    def create_player_response(player_id: str, username: str, 
                             is_online: bool = False) -> Dict[str, Any]:
        """Create minimal player info response"""
        return {
            'player_id': player_id,
            'username': username,
            'is_online': is_online
        }
    
    @staticmethod
    def create_error_response(error_code: str, message: str, 
                            include_details: bool = False) -> Dict[str, Any]:
        """Create error response without exposing internal details"""
        response = {
            'error': error_code,
            'message': message
        }
        # Only include details in development, not production
        if include_details:
            response['timestamp'] = datetime.utcnow().isoformat()
        return response


# Security checklist for client-side implementation
CLIENT_SECURITY_CHECKLIST = {
    'storage': [
        'Never store sensitive tokens in localStorage',
        'Use httpOnly, secure cookies for session management',
        'Clear sensitive data on logout',
        'Implement session timeout on client side'
    ],
    'network': [
        'Always use HTTPS for API calls',
        'Never send credentials in URL parameters',
        'Validate server certificates',
        'Implement request timeout and retry logic'
    ],
    'data_handling': [
        'Validate all server responses before using',
        'Sanitize user input before display',
        'Never trust client-side data for authorization',
        'Implement CSP to prevent XSS'
    ],
    'error_handling': [
        'Never expose stack traces to users',
        'Log errors securely without PII',
        'Show generic error messages to users',
        'Implement proper error boundaries'
    ]
}