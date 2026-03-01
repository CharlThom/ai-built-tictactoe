import pytest
import html
import re
from typing import List


class XSSTestVectors:
    """Common XSS attack vectors for testing"""
    
    BASIC_VECTORS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "<select onfocus=alert('XSS') autofocus>",
        "<textarea onfocus=alert('XSS') autofocus>",
        "<marquee onstart=alert('XSS')>",
    ]
    
    ENCODED_VECTORS = [
        "&lt;script&gt;alert('XSS')&lt;/script&gt;",
        "&#60;script&#62;alert('XSS')&#60;/script&#62;",
        "\x3cscript\x3ealert('XSS')\x3c/script\x3e",
    ]
    
    OBFUSCATED_VECTORS = [
        "<ScRiPt>alert('XSS')</sCrIpT>",
        "<img src=\"x\" onerror=\"alert('XSS')\">",
        "<svg/onload=alert('XSS')>",
        "<img src=x onerror=\"alert`XSS`\">",
    ]


class PlayerNameSanitizer:
    """Sanitizes player names to prevent XSS attacks"""
    
    @staticmethod
    def sanitize(name: str, max_length: int = 50) -> str:
        """Sanitize player name by escaping HTML and removing dangerous patterns"""
        if not name or not isinstance(name, str):
            return "Player"
        
        # Truncate to max length
        name = name[:max_length]
        
        # HTML escape all special characters
        name = html.escape(name, quote=True)
        
        # Remove any remaining script-like patterns (defense in depth)
        dangerous_patterns = [
            r'javascript:',
            r'on\w+\s*=',
            r'<script',
            r'</script',
            r'<iframe',
            r'onerror',
            r'onload',
        ]
        
        for pattern in dangerous_patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        return name.strip() or "Player"
    
    @staticmethod
    def is_safe(name: str) -> bool:
        """Check if name contains potentially dangerous content"""
        dangerous_chars = ['<', '>', '"', "'", '&', '/', '\\']
        return not any(char in name for char in dangerous_chars)


class GameUIRenderer:
    """Safely renders game UI elements"""
    
    @staticmethod
    def render_player_name(name: str) -> str:
        """Render player name safely for UI display"""
        sanitized = PlayerNameSanitizer.sanitize(name)
        return f'<span class="player-name">{sanitized}</span>'
    
    @staticmethod
    def render_game_message(message: str) -> str:
        """Render game message safely"""
        sanitized = html.escape(message, quote=True)
        return f'<div class="game-message">{sanitized}</div>'
    
    @staticmethod
    def render_game_state(player1: str, player2: str, current_turn: str) -> dict:
        """Render complete game state with sanitized data"""
        return {
            'player1': PlayerNameSanitizer.sanitize(player1),
            'player2': PlayerNameSanitizer.sanitize(player2),
            'currentTurn': PlayerNameSanitizer.sanitize(current_turn),
        }


class TestXSSVulnerabilities:
    """Test suite for XSS vulnerabilities in TicTacToe"""
    
    def test_basic_xss_vectors_in_player_names(self):
        """Test that basic XSS vectors are properly sanitized"""
        for vector in XSSTestVectors.BASIC_VECTORS:
            sanitized = PlayerNameSanitizer.sanitize(vector)
            assert '<script' not in sanitized.lower()
            assert 'javascript:' not in sanitized.lower()
            assert 'onerror' not in sanitized.lower()
            assert 'onload' not in sanitized.lower()
    
    def test_encoded_xss_vectors(self):
        """Test that encoded XSS attempts are handled"""
        for vector in XSSTestVectors.ENCODED_VECTORS:
            sanitized = PlayerNameSanitizer.sanitize(vector)
            # Should be double-escaped or stripped
            assert '<script' not in sanitized.lower()
    
    def test_obfuscated_xss_vectors(self):
        """Test that obfuscated XSS attempts are caught"""
        for vector in XSSTestVectors.OBFUSCATED_VECTORS:
            sanitized = PlayerNameSanitizer.sanitize(vector)
            assert '<script' not in sanitized.lower()
            assert 'onerror' not in sanitized.lower()
    
    def test_html_escape_special_characters(self):
        """Test that HTML special characters are properly escaped"""
        test_cases = [
            ('<', '&lt;'),
            ('>', '&gt;'),
            ('&', '&amp;'),
            ('"', '&quot;'),
            ("'", '&#x27;'),
        ]
        
        for char, expected in test_cases:
            sanitized = PlayerNameSanitizer.sanitize(f"Player{char}Name")
            assert expected in sanitized or char not in sanitized
    
    def test_player_name_length_limit(self):
        """Test that player names are truncated to prevent buffer issues"""
        long_name = 'A' * 1000
        sanitized = PlayerNameSanitizer.sanitize(long_name)
        assert len(sanitized) <= 50
    
    def test_empty_and_invalid_names(self):
        """Test handling of empty and invalid player names"""
        assert PlayerNameSanitizer.sanitize('') == 'Player'
        assert PlayerNameSanitizer.sanitize(None) == 'Player'
        assert PlayerNameSanitizer.sanitize('   ') == 'Player'
    
    def test_ui_rendering_safety(self):
        """Test that UI rendering functions properly escape content"""
        malicious_name = "<script>alert('XSS')</script>"
        rendered = GameUIRenderer.render_player_name(malicious_name)
        
        assert '<script>' not in rendered
        assert '&lt;' in rendered or 'script' not in rendered.lower()
    
    def test_game_message_rendering(self):
        """Test that game messages are safely rendered"""
        malicious_msg = "You won! <img src=x onerror=alert('XSS')>"
        rendered = GameUIRenderer.render_game_message(malicious_msg)
        
        assert 'onerror' not in rendered.lower() or '&' in rendered
        assert '<img' not in rendered or '&lt;' in rendered
    
    def test_game_state_rendering(self):
        """Test that complete game state is safely rendered"""
        state = GameUIRenderer.render_game_state(
            "<script>alert('P1')</script>",
            "<img src=x onerror=alert('P2')>",
            "Player1"
        )
        
        assert '<script' not in state['player1'].lower()
        assert 'onerror' not in state['player2'].lower()
        assert state['currentTurn'] == 'Player1'
    
    def test_is_safe_detection(self):
        """Test that unsafe names are properly detected"""
        assert not PlayerNameSanitizer.is_safe("<script>")
        assert not PlayerNameSanitizer.is_safe("Player'Name")
        assert PlayerNameSanitizer.is_safe("ValidPlayerName")
        assert PlayerNameSanitizer.is_safe("Player 123")
    
    def test_context_specific_escaping(self):
        """Test that escaping works in different contexts"""
        # Test in attribute context
        name = 'Player" onload="alert(1)'
        sanitized = PlayerNameSanitizer.sanitize(name)
        assert 'onload' not in sanitized.lower()
        assert '&quot;' in sanitized or '"' not in sanitized
    
    def test_unicode_and_special_chars(self):
        """Test handling of unicode and special characters"""
        unicode_name = "Player™️🎮"
        sanitized = PlayerNameSanitizer.sanitize(unicode_name)
        # Should preserve safe unicode characters
        assert len(sanitized) > 0
        
    def test_sql_injection_in_names(self):
        """Test that SQL injection attempts in names are handled"""
        sql_injection = "Player'; DROP TABLE users; --"
        sanitized = PlayerNameSanitizer.sanitize(sql_injection)
        # Should be escaped, making it harmless
        assert "'" not in sanitized or "&#x27;" in sanitized


if __name__ == '__main__':
    pytest.main([__file__, '-v'])