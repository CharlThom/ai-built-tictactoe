"""Data Exposure Risk Assessment and Mitigation for TicTacToe"""
import re
import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class DataExposureRule:
    """Rule for identifying data exposure risks"""
    name: str
    pattern: str
    severity: str
    description: str


class DataExposureAuditor:
    """Audits client-side code and network requests for data exposure risks"""
    
    EXPOSURE_RULES = [
        DataExposureRule(
            name="sensitive_token_in_url",
            pattern=r"[?&](token|session|auth)=[^&\s]+",
            severity="HIGH",
            description="Authentication tokens should not be in URL parameters"
        ),
        DataExposureRule(
            name="api_key_exposure",
            pattern=r"(api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"][^'\"]+['\""],
            severity="CRITICAL",
            description="API keys or secrets exposed in client code"
        ),
        DataExposureRule(
            name="player_email_exposure",
            pattern=r"\bemail\s*[:=].*@",
            severity="MEDIUM",
            description="Player email addresses exposed in responses"
        ),
        DataExposureRule(
            name="internal_ids_exposure",
            pattern=r"(database_id|internal_id|user_id)\s*[:=]",
            severity="MEDIUM",
            description="Internal database IDs exposed to client"
        )
    ]
    
    def __init__(self):
        self.findings: List[Dict[str, Any]] = []
    
    def audit_response_payload(self, payload: Dict[str, Any], endpoint: str) -> List[Dict[str, Any]]:
        """Audit API response payload for sensitive data exposure"""
        issues = []
        payload_str = json.dumps(payload)
        
        for rule in self.EXPOSURE_RULES:
            if re.search(rule.pattern, payload_str, re.IGNORECASE):
                issues.append({
                    "endpoint": endpoint,
                    "rule": rule.name,
                    "severity": rule.severity,
                    "description": rule.description
                })
        
        # Check for excessive data in responses
        if self._check_excessive_data(payload):
            issues.append({
                "endpoint": endpoint,
                "rule": "excessive_data_exposure",
                "severity": "MEDIUM",
                "description": "Response contains more data than necessary for client"
            })
        
        self.findings.extend(issues)
        return issues
    
    def _check_excessive_data(self, payload: Dict[str, Any]) -> bool:
        """Check if response contains excessive or unnecessary data"""
        sensitive_fields = ['password', 'password_hash', 'salt', 'private_key', 
                          'ssn', 'credit_card', 'internal_notes']
        payload_str = json.dumps(payload).lower()
        return any(field in payload_str for field in sensitive_fields)
    
    def get_report(self) -> Dict[str, Any]:
        """Generate audit report"""
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for finding in self.findings:
            severity_counts[finding["severity"]] += 1
        
        return {
            "total_findings": len(self.findings),
            "severity_breakdown": severity_counts,
            "findings": self.findings,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = [
            "Use HTTP-only, Secure cookies for session tokens instead of localStorage",
            "Implement response filtering to exclude sensitive fields from API responses",
            "Use opaque tokens (UUIDs) instead of sequential IDs in client-facing APIs",
            "Enable CORS with strict origin validation",
            "Implement Content Security Policy (CSP) headers",
            "Sanitize all data before sending to client",
            "Use POST requests for sensitive operations, never GET with sensitive params",
            "Implement request/response logging with PII redaction"
        ]
        return recommendations


class SecureResponseFilter:
    """Filters sensitive data from API responses before sending to client"""
    
    SENSITIVE_FIELDS = {
        'password', 'password_hash', 'salt', 'secret', 'private_key',
        'api_key', 'internal_id', 'database_id', 'ssn', 'credit_card',
        'internal_notes', 'admin_notes', 'ip_address_internal'
    }
    
    PLAYER_SAFE_FIELDS = {
        'player_id', 'username', 'display_name', 'avatar_url', 
        'game_stats', 'current_game_id', 'is_online'
    }
    
    @classmethod
    def filter_player_data(cls, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter player data to only include safe fields"""
        return {k: v for k, v in player_data.items() if k in cls.PLAYER_SAFE_FIELDS}
    
    @classmethod
    def filter_game_state(cls, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Filter game state to prevent exposure of server-side data"""
        safe_state = {
            'game_id': game_state.get('game_id'),
            'board': game_state.get('board'),
            'current_player': game_state.get('current_player'),
            'status': game_state.get('status'),
            'winner': game_state.get('winner'),
            'players': [cls.filter_player_data(p) for p in game_state.get('players', [])]
        }
        return {k: v for k, v in safe_state.items() if v is not None}
    
    @classmethod
    def sanitize_response(cls, data: Any) -> Any:
        """Recursively sanitize response data"""
        if isinstance(data, dict):
            return {k: cls.sanitize_response(v) 
                   for k, v in data.items() 
                   if k.lower() not in cls.SENSITIVE_FIELDS}
        elif isinstance(data, list):
            return [cls.sanitize_response(item) for item in data]
        return data


def audit_network_request_security(request_config: Dict[str, Any]) -> List[str]:
    """Audit network request configuration for security issues"""
    issues = []
    
    # Check if sensitive data in URL
    url = request_config.get('url', '')
    if re.search(r'[?&](token|password|secret|key)=', url, re.IGNORECASE):
        issues.append("CRITICAL: Sensitive data found in URL parameters")
    
    # Check headers
    headers = request_config.get('headers', {})
    if 'Authorization' not in headers and 'Cookie' not in headers:
        issues.append("WARNING: No authentication headers found")
    
    # Check for credentials in body for GET requests
    if request_config.get('method') == 'GET' and request_config.get('body'):
        issues.append("WARNING: GET request should not have body with credentials")
    
    # Check HTTPS
    if url.startswith('http://') and 'localhost' not in url:
        issues.append("CRITICAL: Using HTTP instead of HTTPS for remote requests")
    
    return issues