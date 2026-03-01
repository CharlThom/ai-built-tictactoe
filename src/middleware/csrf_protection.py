import secrets
import hmac
import hashlib
from functools import wraps
from flask import request, session, jsonify, abort
from datetime import datetime, timedelta

CSRF_TOKEN_LENGTH = 32
CSRF_TOKEN_EXPIRY = 3600  # 1 hour in seconds

class CSRFProtection:
    """CSRF protection middleware for game actions"""
    
    def __init__(self, app=None, secret_key=None):
        self.secret_key = secret_key
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize CSRF protection with Flask app"""
        self.secret_key = app.config.get('SECRET_KEY')
        if not self.secret_key:
            raise ValueError("SECRET_KEY must be configured for CSRF protection")
    
    def generate_csrf_token(self, session_id):
        """Generate a cryptographically secure CSRF token"""
        token = secrets.token_urlsafe(CSRF_TOKEN_LENGTH)
        timestamp = str(int(datetime.utcnow().timestamp()))
        
        # Create HMAC signature
        message = f"{token}:{timestamp}:{session_id}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Store in session
        session['csrf_token'] = token
        session['csrf_timestamp'] = timestamp
        session['csrf_signature'] = signature
        
        return token
    
    def validate_csrf_token(self, token, session_id):
        """Validate CSRF token against session data"""
        if not token:
            return False
        
        stored_token = session.get('csrf_token')
        stored_timestamp = session.get('csrf_timestamp')
        stored_signature = session.get('csrf_signature')
        
        if not all([stored_token, stored_timestamp, stored_signature]):
            return False
        
        # Check token match
        if not secrets.compare_digest(token, stored_token):
            return False
        
        # Check expiry
        token_age = int(datetime.utcnow().timestamp()) - int(stored_timestamp)
        if token_age > CSRF_TOKEN_EXPIRY:
            return False
        
        # Verify signature
        message = f"{stored_token}:{stored_timestamp}:{session_id}"
        expected_signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return secrets.compare_digest(stored_signature, expected_signature)
    
    def csrf_protect(self, f):
        """Decorator to protect endpoints with CSRF validation"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                # Get token from header or form data
                token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
                
                if request.is_json:
                    token = token or request.json.get('csrf_token')
                
                session_id = session.get('session_id', '')
                
                if not self.validate_csrf_token(token, session_id):
                    abort(403, description="CSRF token validation failed")
            
            return f(*args, **kwargs)
        
        return decorated_function

csrf = CSRFProtection()

def get_csrf_token():
    """Get or generate CSRF token for current session"""
    session_id = session.get('session_id', '')
    if not session.get('csrf_token'):
        return csrf.generate_csrf_token(session_id)
    return session.get('csrf_token')