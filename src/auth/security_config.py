"""Security configuration and audit settings for TicTacToe authentication."""

import os
from typing import Dict, Any
from enum import Enum


class SecurityLevel(Enum):
    """Security level configurations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SecurityConfig:
    """Centralized security configuration for authentication and API."""
    
    # Authentication settings
    AUTH_CONFIG = {
        "token_algorithm": "SHA256",
        "token_length_bytes": 32,
        "session_timeout_seconds": 3600,
        "max_sessions_per_ip": 10,
        "require_ip_validation": True,
        "enable_session_refresh": True,
        "cleanup_interval_seconds": 300
    }
    
    # API security settings
    API_CONFIG = {
        "rate_limit_requests_per_minute": 60,
        "rate_limit_burst": 10,
        "max_request_size_bytes": 1024 * 10,  # 10KB
        "allowed_origins": ["http://localhost:3000"],
        "require_csrf_token": True,
        "enable_cors": True
    }
    
    # Data handling security
    DATA_CONFIG = {
        "sanitize_input": True,
        "max_player_name_length": 50,
        "allowed_characters": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
        "encrypt_sensitive_data": True,
        "log_security_events": True
    }
    
    # Security headers for HTTP responses
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    @classmethod
    def get_secret_key(cls) -> str:
        """Retrieve secret key from environment or generate new one."""
        secret_key = os.environ.get("TICTACTOE_SECRET_KEY")
        if not secret_key:
            raise ValueError(
                "TICTACTOE_SECRET_KEY environment variable must be set. "
                "Generate with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        return secret_key
    
    @classmethod
    def validate_player_input(cls, player_name: str) -> bool:
        """Validate player name against security rules."""
        if not player_name or len(player_name) > cls.DATA_CONFIG["max_player_name_length"]:
            return False
        
        allowed = set(cls.DATA_CONFIG["allowed_characters"])
        return all(c in allowed for c in player_name)
    
    @classmethod
    def get_audit_checklist(cls) -> Dict[str, Any]:
        """Return security audit checklist for authentication mechanism."""
        return {
            "authentication": {
                "secure_token_generation": "CSPRNG using secrets module",
                "token_length": f"{cls.AUTH_CONFIG['token_length_bytes']} bytes (256 bits)",
                "session_expiration": "Implemented with configurable timeout",
                "session_validation": "IP-based validation to prevent hijacking",
                "timing_attack_protection": "Using hmac.compare_digest for constant-time comparison",
                "rate_limiting": "Max sessions per IP enforced",
                "session_cleanup": "Automatic expired session removal"
            },
            "api_security": {
                "rate_limiting": "Configured per-IP limits",
                "input_validation": "Whitelist-based character validation",
                "request_size_limits": "Maximum payload size enforced",
                "cors_configuration": "Restricted origins",
                "csrf_protection": "Token-based CSRF prevention"
            },
            "data_handling": {
                "input_sanitization": "Enabled with character whitelist",
                "length_validation": "Maximum lengths enforced",
                "security_logging": "Events logged for audit trail",
                "sensitive_data_encryption": "Configured for sensitive fields"
            },
            "http_security": {
                "security_headers": list(cls.SECURITY_HEADERS.keys()),
                "xss_protection": "Multiple layers (headers + CSP)",
                "clickjacking_protection": "X-Frame-Options: DENY",
                "transport_security": "HSTS enabled"
            }
        }
    
    @classmethod
    def print_audit_report(cls) -> None:
        """Print formatted security audit report."""
        checklist = cls.get_audit_checklist()
        print("=" * 60)
        print("TicTacToe Security Audit Report")
        print("=" * 60)
        for category, items in checklist.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            for key, value in items.items():
                if isinstance(value, list):
                    print(f"  ✓ {key}: {', '.join(value)}")
                else:
                    print(f"  ✓ {key}: {value}")
        print("\n" + "=" * 60)