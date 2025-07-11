from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import logging
from google_services import create_google_services

logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self, access_token: str, refresh_token: str = None):
        self.calendar_service, self.docs_service = create_google_services(access_token, refresh_token)
    
    def generate_daily_content(self, target_date: datetime = None) -> Dict:
        """Generate content for daily podcast"""
        if target_date is None:
            target_date = datetime.now()
        
        # Get calendar events for the day
        calendar_events = self.calendar_service.get_today_events()
        schedule_analysis = self.calendar_service.analyze_day_schedule(calendar_events)
        
        # Get recent documents
        recent_docs = self.docs_service.get_recent_documents(days=1)
        shared_docs = self.docs_service.get_documents_shared_with_user(days=1)
        
        # Combine and prioritize documents
        all_documents = self._prioritize_documents(recent_docs, shared_docs, calendar_events)
        
        return {
            'date': target_date.isoformat(),
            'calendar_summary': self._create_calendar_summary(calendar_events, schedule_analysis),
            'documents_summary': self._create_documents_summary(all_documents),
            'individual_documents': self._process_individual_documents(all_documents[:5]),  # Top 5
            'raw_data': {
                'calendar_events': calendar_events,
                'schedule_analysis': schedule_analysis,
                'documents': all_documents
            }
        }
    
    def _create_calendar_summary(self, events: List[Dict], analysis: Dict) -> Dict:
        """Create a summary of the day's calendar"""
        if not events:
            return {
                'type': 'light_day',
                'summary': "You have a light day ahead with no scheduled meetings.",
                'total_events': 0,
                'busy_hours': 0,
                'key_highlights': []
            }
        
        # Determine day type
        density = analysis['meeting_density']
        day_type = 'busy_day' if density == 'heavy' else 'moderate_day' if density == 'moderate' else 'light_day'
        
        # Create summary text
        total_events = analysis['total_events']
        busy_hours = analysis['busy_hours']
        
        if density == 'heavy':
            summary = f"You have a packed day with {total_events} meetings spanning {busy_hours} hours."
        elif density == 'moderate':
            summary = f"You have a moderately busy day with {total_events} meetings over {busy_hours} hours."
        else:
            summary = f"You have a light day with {total_events} meetings taking up {busy_hours} hours."
        
        # Add back-to-back meetings warning
        if analysis['back_to_back_meetings'] > 0:
            summary += f" You have {analysis['back_to_back_meetings']} back-to-back meetings."
        
        # Key highlights
        highlights = []
        
        # Important meetings (with many attendees or external attendees)
        important_meetings = [
            event for event in events 
            if len(event.get('attendees', [])) > 5 or 
            any('@' in att.get('email', '') and not att.get('email', '').endswith('@gmail.com') 
                for att in event.get('attendees', []))
        ]
        
        if important_meetings:
            highlights.append(f"Important meetings: {', '.join([m['title'] for m in important_meetings[:3]])}")
        
        # Meetings with location/travel
        travel_meetings = [event for event in events if event.get('location')]
        if travel_meetings:
            locations = list(set([m['location'] for m in travel_meetings]))
            highlights.append(f"Travel required to: {', '.join(locations[:2])}")
        
        # Long meetings
        if analysis['longest_meeting']:
            longest = analysis['longest_meeting']
            duration = (longest['end_time'] - longest['start_time']).total_seconds() / 3600
            if duration > 2:  # More than 2 hours
                highlights.append(f"Long meeting: {longest['title']} ({duration:.1f} hours)")
        
        return {
            'type': day_type,
            'summary': summary,
            'total_events': total_events,
            'busy_hours': busy_hours,
            'key_highlights': highlights,
            'meeting_details': self._format_meeting_details(events)
        }
    
    def _format_meeting_details(self, events: List[Dict]) -> List[Dict]:
        """Format meeting details for podcast"""
        formatted_events = []
        
        for event in events:
            start_time = event['start_time']
            end_time = event['end_time']
            
            # Format time
            if event['is_all_day']:
                time_str = "All day"
            else:
                time_str = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
            
            # Calculate duration
            if not event['is_all_day']:
                duration_minutes = (end_time - start_time).total_seconds() / 60
                if duration_minutes >= 60:
                    duration_str = f"{duration_minutes/60:.1f} hours"
                else:
                    duration_str = f"{int(duration_minutes)} minutes"
            else:
                duration_str = "All day"
            
            formatted_events.append({
                'title': event['title'],
                'time': time_str,
                'duration': duration_str,
                'location': event.get('location', ''),
                'attendee_count': len(event.get('attendees', [])),
                'has_attachments': len(event.get('attachments', [])) > 0,
                'description': event.get('description', '')[:200] + '...' if len(event.get('description', '')) > 200 else event.get('description', '')
            })
        
        return formatted_events
    
    def _prioritize_documents(self, recent_docs: List[Dict], shared_docs: List[Dict], 
                            calendar_events: List[Dict]) -> List[Dict]:
        """Prioritize documents based on relevance"""
        all_docs = {}
        
        # Add recent documents
        for doc in recent_docs:
            all_docs[doc['id']] = {**doc, 'priority_score': 1, 'sources': ['recent']}
        
        # Add shared documents with higher priority
        for doc in shared_docs:
            if doc['id'] in all_docs:
                all_docs[doc['id']]['priority_score'] += 2
                all_docs[doc['id']]['sources'].append('shared')
            else:
                all_docs[doc['id']] = {**doc, 'priority_score': 2, 'sources': ['shared']}
        
        # Boost priority for documents attached to calendar events
        for event in calendar_events:
            for attachment in event.get('attachments', []):
                # Extract document ID from Google Drive URLs
                if 'docs.google.com' in attachment.get('fileUrl', ''):
                    doc_id = self._extract_doc_id_from_url(attachment['fileUrl'])
                    if doc_id and doc_id in all_docs:
                        all_docs[doc_id]['priority_score'] += 3
                        all_docs[doc_id]['sources'].append('calendar_attachment')
        
        # Sort by priority score and modification time
        sorted_docs = sorted(
            all_docs.values(),
            key=lambda x: (x['priority_score'], x['modified_time']),
            reverse=True
        )
        
        return sorted_docs
    
    def _extract_doc_id_from_url(self, url: str) -> Optional[str]:
        """Extract document ID from Google Docs URL"""
        try:
            if '/document/d/' in url:
                return url.split('/document/d/')[1].split('/')[0]
            return None
        except:
            return None
    
    def _create_documents_summary(self, documents: List[Dict]) -> Dict:
        """Create a summary of documents"""
        if not documents:
            return {
                'total_documents': 0,
                'summary': "No new documents were shared with you recently.",
                'categories': []
            }
        
        total_docs = len(documents)
        shared_docs = len([d for d in documents if 'shared' in d.get('sources', [])])
        calendar_docs = len([d for d in documents if 'calendar_attachment' in d.get('sources', [])])
        
        summary = f"You have {total_docs} document(s) to review"
        if shared_docs > 0:
            summary += f", including {shared_docs} shared with you"
        if calendar_docs > 0:
            summary += f" and {calendar_docs} attached to calendar events"
        summary += "."
        
        return {
            'total_documents': total_docs,
            'shared_documents': shared_docs,
            'calendar_documents': calendar_docs,
            'summary': summary,
            'top_documents': [
                {
                    'name': doc['name'],
                    'modified_time': doc['modified_time'].strftime('%I:%M %p'),
                    'priority_score': doc['priority_score'],
                    'sources': doc['sources']
                }
                for doc in documents[:5]
            ]
        }
    
    def _process_individual_documents(self, documents: List[Dict]) -> List[Dict]:
        """Process individual documents for detailed review"""
        processed_docs = []
        
        for doc in documents:
            try:
                # Get document content
                content = self.docs_service.get_document_content(doc['id'])
                
                if content:
                    processed_docs.append({
                        'id': doc['id'],
                        'name': doc['name'],
                        'modified_time': doc['modified_time'],
                        'web_link': doc['web_link'],
                        'content_preview': content['content'][:500] + '...' if len(content['content']) > 500 else content['content'],
                        'word_count': content['word_count'],
                        'priority_score': doc['priority_score'],
                        'sources': doc['sources']
                    })
                else:
                    # If we can't get content, still include basic info
                    processed_docs.append({
                        'id': doc['id'],
                        'name': doc['name'],
                        'modified_time': doc['modified_time'],
                        'web_link': doc['web_link'],
                        'content_preview': f"Document: {doc['name']} (content not accessible)",
                        'word_count': 0,
                        'priority_score': doc['priority_score'],
                        'sources': doc['sources']
                    })
            except Exception as e:
                logger.error(f"Error processing document {doc['id']}: {e}")
                continue
        
        return processed_docs