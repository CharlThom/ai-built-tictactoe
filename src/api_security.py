from functools import wraps
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
from typing import Any, Callable
import bleach

# Rate limiter configuration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Input validation patterns
PATTERNS = {
    'player_name': re.compile(r'^[a-zA-Z0-9_-]{3,20}$'),
    'game_id': re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'),
    'position': re.compile(r'^[0-8]$'),
    'token': re.compile(r'^[a-zA-Z0-9_-]{32,128}$')
}

ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}


def sanitize_input(value: str) -> str:
    """Sanitize string input to prevent XSS and injection attacks."""
    if not isinstance(value, str):
        return str(value)
    return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)


def validate_input(field_name: str, value: Any) -> tuple[bool, str]:
    """Validate input against predefined patterns."""
    if value is None:
        return False, f"{field_name} is required"
    
    str_value = str(value).strip()
    
    if field_name not in PATTERNS:
        return False, f"Unknown field: {field_name}"
    
    if not PATTERNS[field_name].match(str_value):
        return False, f"Invalid {field_name} format"
    
    return True, ""


def validate_request(*required_fields):
    """Decorator to validate request data against injection attacks."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json(silent=True) or {}
            
            # Check for required fields
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'error': 'Validation failed',
                        'message': f'Missing required field: {field}'
                    }), 400
                
                # Validate field format
                is_valid, error_msg = validate_input(field, data[field])
                if not is_valid:
                    return jsonify({
                        'error': 'Validation failed',
                        'message': error_msg
                    }), 400
                
                # Sanitize string inputs
                if isinstance(data[field], str):
                    data[field] = sanitize_input(data[field])
            
            # Attach sanitized data to request
            request.validated_data = data
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def check_sql_injection(value: str) -> bool:
    """Check for common SQL injection patterns."""
    sql_patterns = [
        r"('|(\-\-)|(;)|(\|\|)|(\*))",
        r"(\bOR\b|\bAND\b).*=.*",
        r"\bUNION\b.*\bSELECT\b",
        r"\bDROP\b.*\bTABLE\b",
        r"\bINSERT\b.*\bINTO\b",
        r"\bDELETE\b.*\bFROM\b"
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False


def check_nosql_injection(data: dict) -> bool:
    """Check for NoSQL injection patterns."""
    dangerous_operators = ['$where', '$ne', '$gt', '$lt', '$regex', '$exists']
    
    def check_dict(d: dict) -> bool:
        for key, value in d.items():
            if key in dangerous_operators:
                return True
            if isinstance(value, dict):
                if check_dict(value):
                    return True
        return False
    
    return check_dict(data)


def secure_headers(f: Callable) -> Callable:
    """Add security headers to response."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if hasattr(response, 'headers'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    return decorated_function