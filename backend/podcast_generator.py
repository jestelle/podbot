import openai
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import logging
from pathlib import Path
from config import settings

logger = logging.getLogger(__name__)

class PodcastScriptGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def generate_welcome_script(self, user_email: str) -> str:
        """Generate a welcome script for new users"""
        prompt = f"""
        Create a warm, friendly welcome script for a new user of Podbot, a personalized podcast service. 
        
        User email: {user_email}
        
        The script should:
        - Be about 30-60 seconds when spoken
        - Welcome them to Podbot
        - Explain briefly what Podbot does (creates daily personalized podcasts from their calendar and documents)
        - Set expectations for their first real podcast (generated tomorrow morning)
        - Sound natural and conversational, like a friendly host
        - Be engaging and make them excited about the service
        
        Write this as a script that will be converted to speech, so use natural speech patterns.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional podcast script writer who creates engaging, conversational content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating welcome script: {e}")
            return self._fallback_welcome_script(user_email)
    
    def generate_daily_podcast_script(self, daily_content: Dict) -> str:
        """Generate a full daily podcast script from processed content"""
        
        # Extract key information
        calendar_summary = daily_content.get('calendar_summary', {})
        documents_summary = daily_content.get('documents_summary', {})
        individual_docs = daily_content.get('individual_documents', [])
        
        date_str = datetime.fromisoformat(daily_content['date']).strftime('%A, %B %d, %Y')
        
        # Build the prompt with structured information
        prompt = f"""
        Create a personalized daily podcast script for {date_str}. 
        
        CALENDAR INFORMATION:
        - Total events: {calendar_summary.get('total_events', 0)}
        - Busy hours: {calendar_summary.get('busy_hours', 0)}
        - Meeting density: {calendar_summary.get('meeting_density', 'unknown')}
        - Summary: {calendar_summary.get('summary', 'No calendar information')}
        - Key highlights: {', '.join(calendar_summary.get('key_highlights', []))}
        
        DOCUMENT INFORMATION:
        - Total documents: {documents_summary.get('total_documents', 0)}
        - Document summary: {documents_summary.get('summary', 'No new documents')}
        
        TOP DOCUMENTS TO MENTION:
        {self._format_documents_for_prompt(individual_docs[:3])}
        
        DETAILED MEETING SCHEDULE:
        {self._format_meetings_for_prompt(calendar_summary.get('meeting_details', []))}
        
        Create a 5-8 minute podcast script that:
        1. Opens with a warm greeting and the date
        2. Gives an overview of the day's schedule and document activity
        3. Provides a detailed walkthrough of the day's meetings (if any)
        4. Summarizes key documents that were shared or modified
        5. Ends with an encouraging note for the day
        
        Style guidelines:
        - Conversational and friendly tone
        - Natural speech patterns (use contractions, informal language)
        - Include smooth transitions between sections
        - Add personality and warmth
        - Keep it engaging and informative
        - Use "you" to address the listener directly
        - Break up dense information with commentary
        
        Format as a natural podcast script with clear sections.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert podcast host and script writer. Create engaging, conversational daily briefing content that sounds natural when spoken aloud."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating daily podcast script: {e}")
            return self._fallback_daily_script(daily_content)
    
    def generate_document_deep_dive_script(self, document: Dict) -> str:
        """Generate a detailed script for a specific document"""
        
        prompt = f"""
        Create a detailed podcast segment about this document:
        
        Document: {document.get('name', 'Untitled Document')}
        Content preview: {document.get('content_preview', 'No content available')}
        Word count: {document.get('word_count', 0)}
        Priority score: {document.get('priority_score', 0)}
        Sources: {', '.join(document.get('sources', []))}
        
        Create a 2-3 minute podcast segment that:
        - Introduces the document and its context
        - Summarizes the key points and main content
        - Explains why this document is important/relevant
        - Provides actionable insights or takeaways
        - Maintains an engaging, conversational tone
        
        Make it sound like a knowledgeable friend explaining the document to you.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a podcast host who specializes in breaking down complex documents into digestible, engaging content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating document script: {e}")
            return f"Here's a summary of the document '{document.get('name', 'Untitled Document')}': {document.get('content_preview', 'Content not available')}"
    
    def _format_documents_for_prompt(self, documents: List[Dict]) -> str:
        """Format documents for the prompt"""
        if not documents:
            return "No documents to review."
        
        formatted = []
        for doc in documents:
            formatted.append(f"- {doc.get('name', 'Untitled')}: {doc.get('content_preview', 'No preview')[:100]}...")
        
        return '\n'.join(formatted)
    
    def _format_meetings_for_prompt(self, meetings: List[Dict]) -> str:
        """Format meetings for the prompt"""
        if not meetings:
            return "No meetings scheduled."
        
        formatted = []
        for meeting in meetings:
            formatted.append(f"- {meeting.get('time', 'Time TBD')}: {meeting.get('title', 'Untitled Meeting')} ({meeting.get('duration', 'Duration unknown')})")
        
        return '\n'.join(formatted)
    
    def _fallback_welcome_script(self, user_email: str) -> str:
        """Fallback welcome script if OpenAI fails"""
        return f"""
        Welcome to Podbot! I'm excited to have you on board.
        
        Podbot is your personal podcast service that transforms your busy schedule into something meaningful. 
        Every morning, I'll create a personalized podcast just for you, summarizing your day ahead and 
        highlighting the important documents that have been shared with you.
        
        Your first real podcast will be generated tomorrow morning, giving you a head start on your day. 
        Think of it as having a personal assistant who's already read through everything and is ready to 
        brief you on what matters most.
        
        Thanks for joining Podbot, and I look forward to helping you stay organized and informed!
        """
    
    def _fallback_daily_script(self, daily_content: Dict) -> str:
        """Fallback daily script if OpenAI fails"""
        date_str = datetime.fromisoformat(daily_content['date']).strftime('%A, %B %d, %Y')
        return f"""
        Good morning! Here's your daily briefing for {date_str}.
        
        Today you have {daily_content.get('calendar_summary', {}).get('total_events', 0)} events scheduled, 
        and {daily_content.get('documents_summary', {}).get('total_documents', 0)} documents to review.
        
        Have a great day!
        """

class PodcastAudioGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.audio_dir = Path(settings.audio_storage_path)
        self.audio_dir.mkdir(exist_ok=True)
    
    def generate_audio_from_script(self, script: str, filename: str, voice: str = "alloy") -> Dict:
        """Generate audio from script using OpenAI TTS"""
        
        try:
            # Generate audio
            response = self.client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=script,
                response_format="mp3"
            )
            
            # Save audio file
            audio_path = self.audio_dir / f"{filename}.mp3"
            response.stream_to_file(audio_path)
            
            # Get file info
            file_size = audio_path.stat().st_size
            
            # Estimate duration (rough approximation: ~150 words per minute)
            word_count = len(script.split())
            estimated_duration = int((word_count / 150) * 60)  # seconds
            
            return {
                'file_path': str(audio_path),
                'file_size': file_size,
                'duration_seconds': estimated_duration,
                'audio_url': f"{settings.audio_base_url}/{filename}.mp3"
            }
            
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            raise
    
    def generate_welcome_audio(self, user_id: int, script: str) -> Dict:
        """Generate welcome audio for new user"""
        filename = f"welcome_{user_id}_{int(datetime.now().timestamp())}"
        return self.generate_audio_from_script(script, filename, voice="nova")
    
    def generate_daily_audio(self, user_id: int, date_str: str, script: str) -> Dict:
        """Generate daily podcast audio"""
        filename = f"daily_{user_id}_{date_str}"
        return self.generate_audio_from_script(script, filename, voice="alloy")
    
    def generate_document_audio(self, user_id: int, doc_id: str, script: str) -> Dict:
        """Generate document deep-dive audio"""
        filename = f"document_{user_id}_{doc_id}_{int(datetime.now().timestamp())}"
        return self.generate_audio_from_script(script, filename, voice="echo")

class PodcastGenerationService:
    def __init__(self):
        self.script_generator = PodcastScriptGenerator()
        self.audio_generator = PodcastAudioGenerator()
    
    def generate_welcome_podcast(self, user_id: int, user_email: str) -> Dict:
        """Generate complete welcome podcast"""
        logger.info(f"Generating welcome podcast for user {user_id}")
        
        # Generate script
        script = self.script_generator.generate_welcome_script(user_email)
        
        # Generate audio
        audio_info = self.audio_generator.generate_welcome_audio(user_id, script)
        
        return {
            'script': script,
            'audio_info': audio_info,
            'episode_type': 'welcome',
            'title': 'Welcome to Podbot!',
            'description': 'A warm welcome to your new personalized podcast service.'
        }
    
    def generate_daily_podcast(self, user_id: int, daily_content: Dict) -> Dict:
        """Generate complete daily podcast"""
        date_str = datetime.fromisoformat(daily_content['date']).strftime('%Y-%m-%d')
        logger.info(f"Generating daily podcast for user {user_id} on {date_str}")
        
        # Generate script
        script = self.script_generator.generate_daily_podcast_script(daily_content)
        
        # Generate audio
        audio_info = self.audio_generator.generate_daily_audio(user_id, date_str, script)
        
        date_formatted = datetime.fromisoformat(daily_content['date']).strftime('%A, %B %d, %Y')
        
        return {
            'script': script,
            'audio_info': audio_info,
            'episode_type': 'daily',
            'title': f'Daily Briefing - {date_formatted}',
            'description': f'Your personalized daily podcast for {date_formatted}',
            'source_data': json.dumps(daily_content)
        }
    
    def generate_document_podcast(self, user_id: int, document: Dict) -> Dict:
        """Generate document deep-dive podcast"""
        logger.info(f"Generating document podcast for user {user_id}, document {document.get('name', 'Unknown')}")
        
        # Generate script
        script = self.script_generator.generate_document_deep_dive_script(document)
        
        # Generate audio
        audio_info = self.audio_generator.generate_document_audio(user_id, document.get('id', 'unknown'), script)
        
        return {
            'script': script,
            'audio_info': audio_info,
            'episode_type': 'document',
            'title': f'Document Review: {document.get("name", "Unknown Document")}',
            'description': f'Deep dive into the document: {document.get("name", "Unknown Document")}',
            'source_data': json.dumps(document)
        }

# Global instance
podcast_service = PodcastGenerationService()