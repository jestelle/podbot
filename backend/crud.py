from sqlalchemy.orm import Session
from sqlalchemy import desc
import models
from auth import generate_rss_feed_url, generate_unique_feed_id
from datetime import datetime
from typing import List, Optional

class UserCRUD:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        """Get user by email"""
        return db.query(models.User).filter(models.User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
        """Get user by ID"""
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, email: str, google_access_token: str, 
                   google_refresh_token: str = None) -> models.User:
        """Create new user"""
        unique_feed_id = generate_unique_feed_id()
        rss_feed_url = f"/rss/{unique_feed_id}"
        
        user = models.User(
            email=email,
            google_access_token=google_access_token,
            google_refresh_token=google_refresh_token,
            rss_feed_url=rss_feed_url
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create welcome episode
        PodcastCRUD.create_welcome_episode(db, user.id)
        
        return user
    
    @staticmethod
    def update_user_tokens(db: Session, user_id: int, access_token: str, 
                          refresh_token: str = None) -> models.User:
        """Update user's Google tokens"""
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            user.google_access_token = access_token
            if refresh_token:
                user.google_refresh_token = refresh_token
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user

class PodcastCRUD:
    @staticmethod
    def create_welcome_episode(db: Session, user_id: int) -> models.PodcastEpisode:
        """Create welcome episode for new user"""
        episode = models.PodcastEpisode(
            user_id=user_id,
            title="Welcome to Podbot!",
            description="A short introduction to your personalized podcast service",
            audio_url="",  # Will be populated when audio is generated
            audio_file_path="",  # Will be populated when audio is generated
            duration_seconds=0,  # Will be updated when audio is generated
            file_size_bytes=0,  # Will be updated when audio is generated
            episode_type="welcome",
            source_data='{"type": "welcome", "message": "Welcome to Podbot!"}'
        )
        
        db.add(episode)
        db.commit()
        db.refresh(episode)
        return episode
    
    @staticmethod
    def get_user_episodes(db: Session, user_id: int, limit: int = 50) -> List[models.PodcastEpisode]:
        """Get user's podcast episodes"""
        return db.query(models.PodcastEpisode)\
            .filter(models.PodcastEpisode.user_id == user_id)\
            .order_by(desc(models.PodcastEpisode.published_at))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def create_episode(db: Session, user_id: int, title: str, description: str, 
                      episode_type: str, source_data: str) -> models.PodcastEpisode:
        """Create new podcast episode"""
        episode = models.PodcastEpisode(
            user_id=user_id,
            title=title,
            description=description,
            audio_url="",  # Will be populated when audio is generated
            audio_file_path="",  # Will be populated when audio is generated
            duration_seconds=0,  # Will be updated when audio is generated
            file_size_bytes=0,  # Will be updated when audio is generated
            episode_type=episode_type,
            source_data=source_data
        )
        
        db.add(episode)
        db.commit()
        db.refresh(episode)
        return episode
    
    @staticmethod
    def update_episode_audio(db: Session, episode_id: int, audio_url: str, 
                           audio_file_path: str, duration_seconds: int, 
                           file_size_bytes: int) -> models.PodcastEpisode:
        """Update episode with audio information"""
        episode = db.query(models.PodcastEpisode).filter(models.PodcastEpisode.id == episode_id).first()
        if episode:
            episode.audio_url = audio_url
            episode.audio_file_path = audio_file_path
            episode.duration_seconds = duration_seconds
            episode.file_size_bytes = file_size_bytes
            db.commit()
            db.refresh(episode)
        return episode

class GenerationLogCRUD:
    @staticmethod
    def create_log(db: Session, user_id: int) -> models.GenerationLog:
        """Create new generation log"""
        log = models.GenerationLog(
            user_id=user_id,
            status="pending"
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def update_log_status(db: Session, log_id: int, status: str, 
                         error_message: str = None, episodes_generated: int = 0) -> models.GenerationLog:
        """Update generation log status"""
        log = db.query(models.GenerationLog).filter(models.GenerationLog.id == log_id).first()
        if log:
            log.status = status
            if error_message:
                log.error_message = error_message
            log.episodes_generated = episodes_generated
            if status in ["completed", "failed"]:
                log.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(log)
        return log
    
    @staticmethod
    def get_user_logs(db: Session, user_id: int, limit: int = 10) -> List[models.GenerationLog]:
        """Get user's generation logs"""
        return db.query(models.GenerationLog)\
            .filter(models.GenerationLog.user_id == user_id)\
            .order_by(desc(models.GenerationLog.started_at))\
            .limit(limit)\
            .all()

# Global instances
user_crud = UserCRUD()
podcast_crud = PodcastCRUD()
generation_log_crud = GenerationLogCRUD()