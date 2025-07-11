from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

from database import get_db, create_tables
from auth import google_auth, jwt_auth
from crud import user_crud, podcast_crud
from dependencies import get_current_active_user
from content_processor import ContentProcessor
from podcast_pipeline import podcast_pipeline
from config import settings
import models

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Podbot API", version="1.0.0")

# Create database tables
create_tables()

# Mount static files for audio
app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

# CORS configuration for frontend
allowed_origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    settings.frontend_url
]

# Add production frontend URL if different
if settings.is_production:
    allowed_origins.append("https://podbot.vercel.app")  # Add your Vercel domain

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
    
    try:
        rss_xml = podcast_pipeline.get_user_rss_feed(user_id)
        if rss_xml:
            return Response(content=rss_xml, media_type="application/rss+xml")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate RSS feed"
            )
    except Exception as e:
        logger.error(f"Error generating RSS feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate RSS feed"
        )

@app.get("/rss/{feed_id}")
async def get_rss_feed_by_id(feed_id: str, db: Session = Depends(get_db)):
    """Get RSS feed by UUID"""
    try:
        # Find user by RSS feed URL
        user = db.query(models.User).filter(models.User.rss_feed_url == f"/rss/{feed_id}").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RSS feed not found"
            )
        
        rss_xml = podcast_pipeline.get_user_rss_feed(user.id)
        if rss_xml:
            return Response(content=rss_xml, media_type="application/rss+xml")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate RSS feed"
            )
    except Exception as e:
        logger.error(f"Error generating RSS feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate RSS feed"
        )

@app.get("/users/{user_id}/calendar-preview")
async def get_calendar_preview(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a preview of user's calendar data"""
    # Ensure user can only access their own data
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        processor = ContentProcessor(
            access_token=current_user.google_access_token,
            refresh_token=current_user.google_refresh_token
        )
        
        # Get today's calendar events
        calendar_events = processor.calendar_service.get_today_events()
        schedule_analysis = processor.calendar_service.analyze_day_schedule(calendar_events)
        
        return {
            "events": processor._serialize_calendar_events(calendar_events),
            "analysis": schedule_analysis,
            "calendars_info": processor.calendar_service._get_all_calendars()
        }
        
    except Exception as e:
        logger.error(f"Error fetching calendar data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch calendar data"
        )

@app.get("/users/{user_id}/documents-preview")
async def get_documents_preview(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a preview of user's recent documents"""
    # Ensure user can only access their own data
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        processor = ContentProcessor(
            access_token=current_user.google_access_token,
            refresh_token=current_user.google_refresh_token
        )
        
        # Get recent documents
        recent_docs = processor.docs_service.get_recent_documents(days=1)
        shared_docs = processor.docs_service.get_documents_shared_with_user(days=1)
        
        return {
            "recent_documents": processor._serialize_documents(recent_docs),
            "shared_documents": processor._serialize_documents(shared_docs)
        }
        
    except Exception as e:
        logger.error(f"Error fetching documents data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch documents data"
        )

@app.get("/users/{user_id}/daily-content")
async def get_daily_content(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get processed daily content for podcast generation"""
    # Ensure user can only access their own data
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        processor = ContentProcessor(
            access_token=current_user.google_access_token,
            refresh_token=current_user.google_refresh_token
        )
        
        # Generate daily content
        daily_content = processor.generate_daily_content()
        
        return daily_content
        
    except Exception as e:
        logger.error(f"Error generating daily content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate daily content"
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
    
    try:
        # Generate daily podcast, passing the database session
        episode = podcast_pipeline.generate_daily_podcast_for_user(user_id, db=db)
        
        if episode:
            return {
                "success": True,
                "episode": PodcastEpisodeResponse.model_validate(episode),
                "message": "Podcast generated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate podcast"
            )
            
    except Exception as e:
        logger.error(f"Error generating podcast: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate podcast: {str(e)}"
        )

@app.post("/generate-welcome-podcast/{user_id}")
async def generate_welcome_podcast(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate welcome podcast for a user"""
    # Ensure user can only generate their own podcasts
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        episode = podcast_pipeline.generate_welcome_podcast_for_user(user_id, db)
        
        if episode:
            # Refresh the episode from the database to ensure it's attached to the session
            episode = db.query(models.PodcastEpisode).filter(models.PodcastEpisode.id == episode.id).first()
            
            return {
                "success": True,
                "episode": PodcastEpisodeResponse.model_validate(episode),
                "message": "Welcome podcast generated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate welcome podcast"
            )
            
    except Exception as e:
        logger.error(f"Error generating welcome podcast: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate welcome podcast: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)