import secrets
import hashlib
import time
from typing import Optional, Dict
from dataclasses import dataclass
import hmac


@dataclass
class PlayerSession:
    """Represents an authenticated player session."""
    player_id: str
    session_token: str
    created_at: float
    expires_at: float
    ip_address: str
    
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        return time.time() < self.expires_at


class SessionManager:
    """Secure session management for TicTacToe players."""
    
    # Security configurations
    TOKEN_LENGTH = 32  # 256 bits
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    MAX_SESSIONS_PER_IP = 10
    
    def __init__(self, secret_key: Optional[str] = None):
        """Initialize session manager with secret key for HMAC."""
        self.secret_key = secret_key or secrets.token_hex(32)
        self.sessions: Dict[str, PlayerSession] = {}
        self.ip_session_count: Dict[str, int] = {}
    
    def generate_secure_token(self) -> str:
        """Generate cryptographically secure random token."""
        # Use secrets module for CSPRNG
        random_bytes = secrets.token_bytes(self.TOKEN_LENGTH)
        timestamp = str(time.time()).encode()
        
        # Add HMAC for integrity verification
        hmac_signature = hmac.new(
            self.secret_key.encode(),
            random_bytes + timestamp,
            hashlib.sha256
        ).digest()
        
        # Combine and encode as hex
        token = hashlib.sha256(random_bytes + hmac_signature).hexdigest()
        return token
    
    def create_session(self, player_id: str, ip_address: str) -> Optional[PlayerSession]:
        """Create new authenticated session for player."""
        # Rate limiting: check sessions per IP
        if self.ip_session_count.get(ip_address, 0) >= self.MAX_SESSIONS_PER_IP:
            return None
        
        # Generate secure token
        session_token = self.generate_secure_token()
        
        # Create session with expiration
        current_time = time.time()
        session = PlayerSession(
            player_id=player_id,
            session_token=session_token,
            created_at=current_time,
            expires_at=current_time + self.SESSION_TIMEOUT,
            ip_address=ip_address
        )
        
        # Store session
        self.sessions[session_token] = session
        self.ip_session_count[ip_address] = self.ip_session_count.get(ip_address, 0) + 1
        
        return session
    
    def validate_session(self, session_token: str, ip_address: str) -> Optional[PlayerSession]:
        """Validate session token and return session if valid."""
        # Constant-time comparison to prevent timing attacks
        session = self.sessions.get(session_token)
        
        if not session:
            return None
        
        # Verify session validity
        if not session.is_valid():
            self.revoke_session(session_token)
            return None
        
        # Verify IP address matches (prevent session hijacking)
        if not hmac.compare_digest(session.ip_address, ip_address):
            return None
        
        return session
    
    def revoke_session(self, session_token: str) -> bool:
        """Revoke/invalidate a session."""
        session = self.sessions.pop(session_token, None)
        if session:
            self.ip_session_count[session.ip_address] = max(
                0, self.ip_session_count.get(session.ip_address, 1) - 1
            )
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        current_time = time.time()
        expired_tokens = [
            token for token, session in self.sessions.items()
            if session.expires_at < current_time
        ]
        
        for token in expired_tokens:
            self.revoke_session(token)
        
        return len(expired_tokens)
    
    def refresh_session(self, session_token: str, ip_address: str) -> Optional[PlayerSession]:
        """Extend session expiration if valid."""
        session = self.validate_session(session_token, ip_address)
        if session:
            session.expires_at = time.time() + self.SESSION_TIMEOUT
            return session
        return None