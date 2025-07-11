from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from database import get_db, create_tables
from auth import google_auth, jwt_auth
from crud import user_crud, podcast_crud
from dependencies import get_current_active_user
import models

load_dotenv()

app = FastAPI(title="Podbot API", version="1.0.0")

# Create database tables
create_tables()

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserResponse(BaseModel):
    id: int
    email: str
    rss_feed_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PodcastEpisodeResponse(BaseModel):
    id: int
    title: str
    description: str
    audio_url: str
    duration_seconds: int
    published_at: datetime
    episode_type: str
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@app.get("/")
async def root():
    return {"message": "Podbot API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Google OAuth endpoints
@app.get("/auth/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    try:
        auth_url = google_auth.get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Google OAuth: {str(e)}"
        )

@app.get("/auth/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens
        token_data = google_auth.exchange_code_for_tokens(code)
        
        user_info = token_data['user_info']
        email = user_info.get('email')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Check if user exists
        user = user_crud.get_user_by_email(db, email)
        
        if not user:
            # Create new user
            user = user_crud.create_user(
                db=db,
                email=email,
                google_access_token=token_data['access_token'],
                google_refresh_token=token_data.get('refresh_token')
            )
        else:
            # Update existing user's tokens
            user = user_crud.update_user_tokens(
                db=db,
                user_id=user.id,
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token')
            )
        
        # Create JWT token
        access_token_expires = timedelta(minutes=30)
        access_token = jwt_auth.create_access_token(
            data={"user_id": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to authenticate with Google: {str(e)}"
        )

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)

@app.get("/users/{user_id}/episodes", response_model=List[PodcastEpisodeResponse])
async def get_user_episodes(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's podcast episodes"""
    # Ensure user can only access their own episodes
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    episodes = podcast_crud.get_user_episodes(db, user_id)
    return [PodcastEpisodeResponse.model_validate(episode) for episode in episodes]

@app.get("/users/{user_id}/rss")
async def get_user_rss_feed(user_id: int, db: Session = Depends(get_db)):
    """Generate RSS feed for user's podcasts"""
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # TODO: Implement RSS feed generation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="RSS feed generation not implemented yet"
    )

@app.post("/generate-podcast/{user_id}")
async def generate_podcast(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger podcast generation for a user"""
    # Ensure user can only generate their own podcasts
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # TODO: Implement podcast generation pipeline
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Podcast generation not implemented yet"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)