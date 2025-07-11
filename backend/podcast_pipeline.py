from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from content_processor import ContentProcessor
from podcast_generator import podcast_service
from crud import user_crud, podcast_crud, generation_log_crud
from rss_generator import rss_generator
import models

logger = logging.getLogger(__name__)

class PodcastPipeline:
    def __init__(self):
        self.podcast_service = podcast_service
        self.rss_generator = rss_generator
    
    def generate_welcome_podcast_for_user(self, user_id: int, db: Session) -> Optional[models.PodcastEpisode]:
        """Generate welcome podcast for a new user"""
        try:
            user = user_crud.get_user_by_id(db, user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return None
            
            logger.info(f"Generating welcome podcast for user {user_id}")
            
            # Generate podcast content
            podcast_data = self.podcast_service.generate_welcome_podcast(user_id, user.email)
            
            # Create episode in database
            episode = podcast_crud.create_episode(
                db=db,
                user_id=user_id,
                title=podcast_data['title'],
                description=podcast_data['description'],
                episode_type=podcast_data['episode_type'],
                source_data='{}'
            )
            
            # Update episode with audio information
            audio_info = podcast_data['audio_info']
            episode = podcast_crud.update_episode_audio(
                db=db,
                episode_id=episode.id,
                audio_url=audio_info['audio_url'],
                audio_file_path=audio_info['file_path'],
                duration_seconds=audio_info['duration_seconds'],
                file_size_bytes=audio_info['file_size']
            )
            
            logger.info(f"Welcome podcast generated successfully for user {user_id}")
            return episode
            
        except Exception as e:
            logger.error(f"Error generating welcome podcast for user {user_id}: {e}")
            return None
    
    def generate_daily_podcast_for_user(self, user_id: int, target_date: datetime = None, db: Session = None) -> Optional[models.PodcastEpisode]:
        """Generate daily podcast for a user"""
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
            
        try:
            user = user_crud.get_user_by_id(db, user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return None
            
            if target_date is None:
                target_date = datetime.now()
            
            logger.info(f"Generating daily podcast for user {user_id} on {target_date.date()}")
            
            # Create generation log
            log = generation_log_crud.create_log(db, user_id)
            generation_log_crud.update_log_status(db, log.id, "processing")
            
            try:
                # Get content from Google services
                content_processor = ContentProcessor(
                    access_token=user.google_access_token,
                    refresh_token=user.google_refresh_token
                )
                
                daily_content = content_processor.generate_daily_content(target_date)
                
                # Generate podcast
                podcast_data = self.podcast_service.generate_daily_podcast(user_id, daily_content)
                
                # Create episode in database
                episode = podcast_crud.create_episode(
                    db=db,
                    user_id=user_id,
                    title=podcast_data['title'],
                    description=podcast_data['description'],
                    episode_type=podcast_data['episode_type'],
                    source_data=podcast_data['source_data']
                )
                
                # Update episode with audio information
                audio_info = podcast_data['audio_info']
                episode = podcast_crud.update_episode_audio(
                    db=db,
                    episode_id=episode.id,
                    audio_url=audio_info['audio_url'],
                    audio_file_path=audio_info['file_path'],
                    duration_seconds=audio_info['duration_seconds'],
                    file_size_bytes=audio_info['file_size']
                )
                
                # Update generation log
                generation_log_crud.update_log_status(db, log.id, "completed", episodes_generated=1)
                
                logger.info(f"Daily podcast generated successfully for user {user_id}")
                return episode
                
            except Exception as e:
                generation_log_crud.update_log_status(db, log.id, "failed", error_message=str(e))
                raise
                
        except Exception as e:
            logger.error(f"Error generating daily podcast for user {user_id}: {e}")
            return None
        finally:
            if should_close_db:
                db.close()
    
    def generate_document_podcast_for_user(self, user_id: int, document_data: Dict) -> Optional[models.PodcastEpisode]:
        """Generate document deep-dive podcast for a user"""
        db = SessionLocal()
        try:
            user = user_crud.get_user_by_id(db, user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return None
            
            logger.info(f"Generating document podcast for user {user_id}")
            
            # Generate podcast
            podcast_data = self.podcast_service.generate_document_podcast(user_id, document_data)
            
            # Create episode in database
            episode = podcast_crud.create_episode(
                db=db,
                user_id=user_id,
                title=podcast_data['title'],
                description=podcast_data['description'],
                episode_type=podcast_data['episode_type'],
                source_data=podcast_data['source_data']
            )
            
            # Update episode with audio information
            audio_info = podcast_data['audio_info']
            episode = podcast_crud.update_episode_audio(
                db=db,
                episode_id=episode.id,
                audio_url=audio_info['audio_url'],
                audio_file_path=audio_info['file_path'],
                duration_seconds=audio_info['duration_seconds'],
                file_size_bytes=audio_info['file_size']
            )
            
            logger.info(f"Document podcast generated successfully for user {user_id}")
            return episode
            
        except Exception as e:
            logger.error(f"Error generating document podcast for user {user_id}: {e}")
            return None
        finally:
            db.close()
    
    def generate_daily_podcasts_for_all_users(self) -> Dict[str, int]:
        """Generate daily podcasts for all active users"""
        db = SessionLocal()
        try:
            # Get all active users
            users = db.query(models.User).filter(models.User.is_active == True).all()
            
            results = {
                'total_users': len(users),
                'successful': 0,
                'failed': 0,
                'errors': []
            }
            
            for user in users:
                try:
                    episode = self.generate_daily_podcast_for_user(user.id)
                    if episode:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to generate podcast for user {user.id}")
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Error for user {user.id}: {str(e)}")
            
            logger.info(f"Daily podcast generation completed: {results['successful']}/{results['total_users']} successful")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk podcast generation: {e}")
            return {'total_users': 0, 'successful': 0, 'failed': 0, 'errors': [str(e)]}
        finally:
            db.close()
    
    def get_user_rss_feed(self, user_id: int) -> Optional[str]:
        """Generate RSS feed XML for a user"""
        db = SessionLocal()
        try:
            user = user_crud.get_user_by_id(db, user_id)
            if not user:
                return None
            
            episodes = podcast_crud.get_user_episodes(db, user_id, limit=50)
            
            return self.rss_generator.generate_user_feed(user, episodes)
            
        except Exception as e:
            logger.error(f"Error generating RSS feed for user {user_id}: {e}")
            return None
        finally:
            db.close()

# Global instance
podcast_pipeline = PodcastPipeline()