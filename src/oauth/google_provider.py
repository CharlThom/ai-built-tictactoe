import os
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from datetime import datetime, timedelta
import secrets


class GoogleOAuthProvider:
    """Google OAuth2 authentication provider."""
    
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")
    
    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """Generate OAuth authorization URL with state token.
        
        Returns:
            tuple: (authorization_url, state_token)
        """
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        url = f"{self.AUTHORIZATION_URL}?{urlencode(params)}"
        return url, state
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            dict: Token response containing access_token, refresh_token, etc.
            
        Raises:
            requests.HTTPError: If token exchange fails
        """
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(self.TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Fetch user information from Google using access token.
        
        Args:
            access_token: OAuth access token
            
        Returns:
            dict: User profile information (id, email, name, picture)
            
        Raises:
            requests.HTTPError: If user info request fails
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.USERINFO_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token validity.
        
        Args:
            token: Access token to verify
            
        Returns:
            dict: Token info if valid, None otherwise
        """
        try:
            response = requests.get(
                f"https://oauth2.googleapis.com/tokeninfo?access_token={token}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None