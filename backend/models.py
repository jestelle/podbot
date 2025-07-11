from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    google_access_token = Column(Text, nullable=False)
    google_refresh_token = Column(Text, nullable=True)
    rss_feed_url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    episodes = relationship("PodcastEpisode", back_populates="user")

class PodcastEpisode(Base):
    __tablename__ = "podcast_episodes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    audio_url = Column(String, nullable=False)
    audio_file_path = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, default=datetime.utcnow)
    episode_type = Column(String, nullable=False)  # 'welcome', 'daily', 'document'
    source_data = Column(Text)  # JSON string containing source data used for generation
    
    user = relationship("User", back_populates="episodes")

class GenerationLog(Base):
    __tablename__ = "generation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(Text, nullable=True)
    episodes_generated = Column(Integer, default=0)
    
    user = relationship("User")