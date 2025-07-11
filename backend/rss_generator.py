from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry
from typing import List, Dict
from datetime import datetime
import os
from config import settings
import models

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
        fg.lastBuildDate(datetime.utcnow())
        fg.generator('Podbot Podcast Generator')
        
        # Podcast-specific metadata
        fg.podcast.itunes_category('News', 'Daily News')
        fg.podcast.itunes_author('Podbot')
        fg.podcast.itunes_summary(f"Your personalized daily briefing podcast, created automatically from your calendar and documents.")
        fg.podcast.itunes_owner(name='Podbot', email='noreply@podbot.com')
        fg.podcast.itunes_image(f"{self.base_url}/static/podcast-cover.jpg")
        fg.podcast.itunes_explicit('clean')
        
        # Add episodes
        for episode in episodes:
            if episode.audio_url:  # Only include episodes with audio
                fe = fg.add_entry()
                fe.id(f"{self.base_url}/episode/{episode.id}")
                fe.title(episode.title)
                fe.description(episode.description)
                fe.enclosure(episode.audio_url, str(episode.file_size_bytes), 'audio/mpeg')
                fe.pubDate(episode.published_at)
                fe.guid(f"{self.base_url}/episode/{episode.id}")
                
                # Episode-specific metadata
                fe.podcast.itunes_author('Podbot')
                fe.podcast.itunes_duration(self._format_duration(episode.duration_seconds))
                fe.podcast.itunes_explicit('clean')
                fe.podcast.itunes_episode_type('full')
        
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