from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets
import uuid
from config import settings

# Google OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

class GoogleAuth:
    def __init__(self):
        self.flow = None
        self._setup_flow()
    
    def _setup_flow(self):
        """Initialize Google OAuth flow"""
        if not settings.google_client_id or not settings.google_client_secret:
            return
        
        client_config = {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri]
            }
        }
        
        self.flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=settings.google_redirect_uri
        )
    
    def get_authorization_url(self, state: str = None) -> str:
        """Get Google OAuth authorization URL"""
        if not self.flow:
            raise ValueError("Google OAuth not configured")
        
        if not state:
            state = secrets.token_urlsafe(32)
        
        auth_url, _ = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',  # Force consent screen to get refresh token
            state=state
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, code: str) -> dict:
        """Exchange authorization code for tokens"""
        if not self.flow:
            raise ValueError("Google OAuth not configured")
        
        self.flow.fetch_token(code=code)
        
        credentials = self.flow.credentials
        
        # Get user info
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_expiry': credentials.expiry,
            'user_info': user_info
        }
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret
        )
        
        credentials.refresh(Request())
        
        return {
            'access_token': credentials.token,
            'token_expiry': credentials.expiry
        }
    
    def verify_token(self, token: str) -> dict:
        """Verify Google access token and get user info"""
        credentials = Credentials(token=token)
        
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        
        return user_info

class JWTAuth:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None

def generate_rss_feed_url(user_id: int) -> str:
    """Generate unique RSS feed URL for user"""
    unique_id = str(uuid.uuid4())
    return f"{settings.audio_base_url}/rss/{user_id}/{unique_id}"

def generate_unique_feed_id() -> str:
    """Generate unique feed identifier"""
    return str(uuid.uuid4())

# Global instances
google_auth = GoogleAuth()
jwt_auth = JWTAuth()