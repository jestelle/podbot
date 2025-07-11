from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Podbot API", version="1.0.0")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class UserCreate(BaseModel):
    email: str
    google_token: str

class UserResponse(BaseModel):
    id: int
    email: str
    rss_feed_url: str
    created_at: str

class PodcastEpisode(BaseModel):
    title: str
    description: str
    audio_url: str
    duration: int
    pub_date: str

@app.get("/")
async def root():
    return {"message": "Podbot API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/auth/google", response_model=UserResponse)
async def google_auth(user_data: UserCreate):
    """Handle Google OAuth authentication and user creation"""
    # TODO: Implement Google OAuth token verification
    # TODO: Create or get existing user
    # TODO: Generate unique RSS feed URL
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google authentication not implemented yet"
    )

@app.get("/users/{user_id}/rss")
async def get_user_rss_feed(user_id: int):
    """Generate RSS feed for user's podcasts"""
    # TODO: Implement RSS feed generation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="RSS feed generation not implemented yet"
    )

@app.get("/users/{user_id}/episodes")
async def get_user_episodes(user_id: int):
    """Get user's podcast episodes"""
    # TODO: Implement episode retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Episode retrieval not implemented yet"
    )

@app.post("/generate-podcast/{user_id}")
async def generate_podcast(user_id: int):
    """Trigger podcast generation for a user"""
    # TODO: Implement podcast generation pipeline
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Podcast generation not implemented yet"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)