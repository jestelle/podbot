from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry
from typing import List, Dict
from datetime import datetime, timezone
import os
import logging
from config import settings
import models

logger = logging.getLogger(__name__)

class RSSFeedGenerator:
    def __init__(self):
        self.base_url = settings.audio_base_url
    
    def generate_user_feed(self, user: models.User, episodes: List[models.PodcastEpisode]) -> str:
        """Generate RSS feed XML for a user's podcast episodes"""
        
        # Create feed generator
        fg = FeedGenerator()
        
        # Feed metadata
        fg.id(f"{self.base_url}/rss/{user.id}")
        fg.title(f"{user.email.split('@')[0]}'s Daily Podcast")
        fg.link(href=f"{self.base_url}/rss/{user.id}", rel='alternate')
        fg.description(f"Personalized daily podcast for {user.email}")
        fg.author({'name': 'Podbot', 'email': 'noreply@podbot.com'})
        fg.language('en')
        fg.lastBuildDate(datetime.now(timezone.utc))
        fg.generator('Podbot Podcast Generator')
        
        # Load podcast extension once
        try:
            fg.load_extension('podcast')
            # Podcast-specific metadata for iTunes
            fg.podcast.itunes_category('News', 'Daily News')
            fg.podcast.itunes_author('Podbot')
            fg.podcast.itunes_summary(f"Your personalized daily briefing podcast, created automatically from your calendar and documents.")
            fg.podcast.itunes_owner(name='Podbot', email='noreply@podbot.com')
            fg.podcast.itunes_image(f"{self.base_url}/static/podcast-cover.jpg")
            fg.podcast.itunes_explicit('clean')
        except Exception as e:
            logger.warning(f"Could not load podcast extension: {e}")
        
        # Add episodes
        for episode in episodes:
            if episode.audio_url:  # Only include episodes with audio
                fe = fg.add_entry()
                fe.id(f"{self.base_url}/episode/{episode.id}")
                fe.title(episode.title)
                fe.description(episode.description)
                fe.enclosure(episode.audio_url, str(episode.file_size_bytes), 'audio/mpeg')
                # Handle timezone-naive datetime objects
                pub_date = episode.published_at
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                fe.pubDate(pub_date)
                fe.guid(f"{self.base_url}/episode/{episode.id}")
                
                # Episode-specific metadata
                try:
                    fe.load_extension('podcast')
                    fe.podcast.itunes_author('Podbot')
                    fe.podcast.itunes_duration(self._format_duration(episode.duration_seconds))
                    fe.podcast.itunes_explicit('clean')
                    fe.podcast.itunes_episode_type('full')
                except Exception as e:
                    logger.warning(f"Could not load podcast extension for episode {episode.id}: {e}")
        
        return fg.rss_str(pretty=True).decode('utf-8')
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in HH:MM:SS format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def generate_feed_url(self, user: models.User) -> str:
        """Generate the public RSS feed URL for a user"""
        return f"{self.base_url}{user.rss_feed_url}"

# Global instance
rss_generator = RSSFeedGenerator()