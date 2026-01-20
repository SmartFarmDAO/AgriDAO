"""
Google OAuth Authentication Service
"""
import os
import logging
from typing import Dict, Optional
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

logger = logging.getLogger(__name__)

# OAuth configuration
config = Config(environ={
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
})

oauth = OAuth(config)

# Register Google OAuth
oauth.register(
    name='google',
    client_id=config.get('GOOGLE_CLIENT_ID'),
    client_secret=config.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


class GoogleOAuthService:
    """Service for Google OAuth authentication"""
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        self.enabled = bool(self.client_id and self.client_secret)
        
        if not self.enabled:
            logger.warning("Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
    
    def get_authorization_url(self, redirect_uri: Optional[str] = None) -> str:
        """Get Google OAuth authorization URL"""
        if not self.enabled:
            raise ValueError("Google OAuth not configured")
        
        uri = redirect_uri or self.redirect_uri
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={self.client_id}&"
            f"redirect_uri={uri}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile&"
            f"access_type=offline&"
            f"prompt=consent"
        )
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify Google ID token and get user info"""
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to verify Google token: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            return None
    
    async def exchange_code(self, code: str, redirect_uri: Optional[str] = None) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        import httpx
        
        try:
            uri = redirect_uri or self.redirect_uri
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": code,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": uri,
                        "grant_type": "authorization_code"
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    # Get user info with access token
                    user_info = await self.verify_token(token_data["access_token"])
                    return user_info
                else:
                    logger.error(f"Failed to exchange code: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error exchanging code: {e}")
            return None


google_oauth_service = GoogleOAuthService()
