from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./podbot.db"
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    
    # OpenAI
    openai_api_key: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Audio Storage
    audio_storage_path: str = "./audio_files"
    audio_base_url: str = "http://localhost:8000/audio"
    
    # Podcast Settings
    podcast_title_template: str = "Daily Briefing - {date}"
    podcast_description_template: str = "Your personalized daily podcast for {date}"
    
    # Google Cloud (for production)
    google_cloud_project_id: Optional[str] = None
    google_cloud_storage_bucket: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()