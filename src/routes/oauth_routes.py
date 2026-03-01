from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import secrets
from datetime import datetime, timedelta

from src.oauth.google_provider import GoogleOAuthProvider
from src.database import get_db
from src.models import User, OAuthAccount
from src.auth import create_access_token, create_refresh_token
from src.schemas import TokenResponse


router = APIRouter(prefix="/api/auth", tags=["oauth"])
google_provider = GoogleOAuthProvider()

# In-memory state storage (use Redis in production)
oauth_states = {}


def store_oauth_state(state: str, expires_minutes: int = 10) -> None:
    """Store OAuth state token with expiration."""
    oauth_states[state] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    # Clean expired states
    expired = [k for k, v in oauth_states.items() if v < datetime.utcnow()]
    for k in expired:
        del oauth_states[k]


def verify_oauth_state(state: str) -> bool:
    """Verify OAuth state token is valid and not expired."""
    if state not in oauth_states:
        return False
    if oauth_states[state] < datetime.utcnow():
        del oauth_states[state]
        return False
    del oauth_states[state]
    return True


@router.get("/google")
async def google_login(request: Request):
    """Initiate Google OAuth flow.
    
    Returns:
        RedirectResponse: Redirects to Google authorization page
    """
    try:
        auth_url, state = google_provider.get_authorization_url()
        store_oauth_state(state)
        return RedirectResponse(url=auth_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth flow: {str(e)}"
        )


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback.
    
    Args:
        code: Authorization code from Google
        state: State token for CSRF protection
        error: Error message if authorization failed
        db: Database session
        
    Returns:
        TokenResponse: JWT access and refresh tokens
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authorization failed: {error}"
        )
    
    # Verify state token
    if not verify_oauth_state(state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token"
        )
    
    try:
        # Exchange code for tokens
        token_data = google_provider.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token"
            )
        
        # Get user info from Google
        user_info = google_provider.get_user_info(access_token)
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name", "")
        picture = user_info.get("picture")
        
        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user information"
            )
        
        # Check if OAuth account exists
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.provider == "google",
            OAuthAccount.provider_user_id == google_id
        ).first()
        
        if oauth_account:
            # Existing OAuth account - get associated user
            user = oauth_account.user
        else:
            # Check if user exists with this email
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Create new user
                user = User(
                    email=email,
                    username=email.split("@")[0] + "_" + secrets.token_hex(4),
                    full_name=name,
                    is_active=True,
                    email_verified=True
                )
                db.add(user)
                db.flush()
            
            # Create OAuth account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="google",
                provider_user_id=google_id,
                access_token=access_token,
                refresh_token=token_data.get("refresh_token"),
                token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
                profile_data={"name": name, "picture": picture, "email": email}
            )
            db.add(oauth_account)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate JWT tokens
        jwt_access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        jwt_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=jwt_access_token,
            refresh_token=jwt_refresh_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@router.post("/google/unlink")
async def unlink_google_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlink Google OAuth account from user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Success message
    """
    oauth_account = db.query(OAuthAccount).filter(
        OAuthAccount.user_id == current_user.id,
        OAuthAccount.provider == "google"
    ).first()
    
    if not oauth_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google account not linked"
        )
    
    # Ensure user has password set before unlinking
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unlink OAuth account without setting a password first"
        )
    
    db.delete(oauth_account)
    db.commit()
    
    return {"message": "Google account unlinked successfully"}