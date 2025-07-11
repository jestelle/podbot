from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    def __init__(self, access_token: str, refresh_token: str = None):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,  # Will be set by the auth system
            client_secret=None  # Will be set by the auth system
        )
        self.service = build('calendar', 'v3', credentials=self.credentials)
    
    def get_today_events(self, timezone: str = 'UTC') -> List[Dict]:
        """Get today's calendar events from all calendars"""
        try:
            # Get today's date range
            today = datetime.now().date()
            start_time = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
            end_time = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'
            
            # Get all calendars
            calendars = self._get_all_calendars()
            
            all_events = []
            
            # Fetch events from each calendar
            for calendar in calendars:
                try:
                    events_result = self.service.events().list(
                        calendarId=calendar['id'],
                        timeMin=start_time,
                        timeMax=end_time,
                        maxResults=50,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                    events = events_result.get('items', [])
                    
                    for event in events:
                        processed_event = self._process_event(event, calendar)
                        if processed_event:
                            all_events.append(processed_event)
                            
                except HttpError as error:
                    logger.warning(f"Error fetching events from calendar {calendar['summary']}: {error}")
                    continue
            
            # Sort all events by start time
            all_events.sort(key=lambda x: x['start_time'])
            
            return all_events
            
        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            return []
    
    def get_week_events(self, timezone: str = 'UTC') -> List[Dict]:
        """Get this week's calendar events from all calendars"""
        try:
            # Get week date range (Monday to Sunday)
            today = datetime.now().date()
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            
            start_time = datetime.combine(monday, datetime.min.time()).isoformat() + 'Z'
            end_time = datetime.combine(sunday, datetime.max.time()).isoformat() + 'Z'
            
            # Get all calendars
            calendars = self._get_all_calendars()
            
            all_events = []
            
            # Fetch events from each calendar
            for calendar in calendars:
                try:
                    events_result = self.service.events().list(
                        calendarId=calendar['id'],
                        timeMin=start_time,
                        timeMax=end_time,
                        maxResults=100,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                    events = events_result.get('items', [])
                    
                    for event in events:
                        processed_event = self._process_event(event, calendar)
                        if processed_event:
                            all_events.append(processed_event)
                            
                except HttpError as error:
                    logger.warning(f"Error fetching events from calendar {calendar['summary']}: {error}")
                    continue
            
            # Sort all events by start time
            all_events.sort(key=lambda x: x['start_time'])
            
            return all_events
            
        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            return []
    
    def _get_all_calendars(self) -> List[Dict]:
        """Get all calendars the user has access to"""
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = []
            
            for calendar_item in calendar_list.get('items', []):
                # Only include calendars that are selected/visible and not hidden
                if calendar_item.get('selected', True) and not calendar_item.get('hidden', False):
                    calendars.append({
                        'id': calendar_item['id'],
                        'summary': calendar_item.get('summary', ''),
                        'description': calendar_item.get('description', ''),
                        'primary': calendar_item.get('primary', False),
                        'access_role': calendar_item.get('accessRole', ''),
                        'color': calendar_item.get('backgroundColor', ''),
                        'timezone': calendar_item.get('timeZone', '')
                    })
            
            logger.info(f"Found {len(calendars)} accessible calendars")
            return calendars
            
        except HttpError as error:
            logger.error(f"Error fetching calendar list: {error}")
            # Fallback to primary calendar only
            return [{'id': 'primary', 'summary': 'Primary Calendar', 'primary': True}]
    
    def _process_event(self, event: Dict, calendar: Dict = None) -> Optional[Dict]:
        """Process a calendar event into a standardized format"""
        try:
            # Skip events without start time (all-day events without time)
            start = event.get('start', {})
            end = event.get('end', {})
            
            # Handle different time formats
            start_time = start.get('dateTime', start.get('date'))
            end_time = end.get('dateTime', end.get('date'))
            
            if not start_time:
                return None
            
            # Parse datetime
            if 'T' in start_time:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                is_all_day = False
            else:
                # All-day event - create timezone-aware datetime
                start_dt = datetime.fromisoformat(start_time + 'T00:00:00+00:00')
                is_all_day = True
            
            if end_time and 'T' in end_time:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            elif end_time:
                # All-day event - create timezone-aware datetime
                end_dt = datetime.fromisoformat(end_time + 'T23:59:59+00:00')
            else:
                end_dt = start_dt + timedelta(hours=1)  # Default 1 hour
            
            # Extract attachments/links
            attachments = []
            if 'attachments' in event:
                for attachment in event['attachments']:
                    attachments.append({
                        'title': attachment.get('title', ''),
                        'fileUrl': attachment.get('fileUrl', ''),
                        'mimeType': attachment.get('mimeType', '')
                    })
            
            # Extract meeting details
            meeting_info = {}
            if 'conferenceData' in event:
                conference = event['conferenceData']
                if 'entryPoints' in conference:
                    for entry in conference['entryPoints']:
                        if entry.get('entryPointType') == 'video':
                            meeting_info['video_url'] = entry.get('uri', '')
                        elif entry.get('entryPointType') == 'phone':
                            meeting_info['phone'] = entry.get('uri', '')
            
            return {
                'id': event.get('id', ''),
                'title': event.get('summary', 'Untitled Event'),
                'description': event.get('description', ''),
                'start_time': start_dt,
                'end_time': end_dt,
                'is_all_day': is_all_day,
                'location': event.get('location', ''),
                'calendar': {
                    'id': calendar.get('id', '') if calendar else '',
                    'name': calendar.get('summary', 'Unknown Calendar') if calendar else 'Unknown Calendar',
                    'color': calendar.get('color', '') if calendar else '',
                    'primary': calendar.get('primary', False) if calendar else False
                },
                'attendees': [
                    {
                        'email': attendee.get('email', ''),
                        'name': attendee.get('displayName', ''),
                        'status': attendee.get('responseStatus', '')
                    }
                    for attendee in event.get('attendees', [])
                ],
                'attachments': attachments,
                'meeting_info': meeting_info,
                'creator': event.get('creator', {}),
                'status': event.get('status', '')
            }
            
        except Exception as e:
            logger.error(f"Error processing event {event.get('id', '')}: {e}")
            return None
    
    def analyze_day_schedule(self, events: List[Dict]) -> Dict:
        """Analyze daily schedule patterns"""
        if not events:
            return {
                'total_events': 0,
                'busy_hours': 0,
                'free_time_blocks': [],
                'meeting_density': 'light',
                'longest_meeting': None,
                'back_to_back_meetings': 0
            }
        
        # Sort events by start time
        events = sorted(events, key=lambda x: x['start_time'])
        
        # Calculate metrics
        total_events = len(events)
        busy_hours = sum(
            (event['end_time'] - event['start_time']).total_seconds() / 3600
            for event in events if not event['is_all_day']
        )
        
        # Find free time blocks
        free_blocks = []
        for i in range(len(events) - 1):
            current_end = events[i]['end_time']
            next_start = events[i + 1]['start_time']
            gap = (next_start - current_end).total_seconds() / 60  # minutes
            
            if gap > 30:  # More than 30 minutes
                free_blocks.append({
                    'start': current_end.isoformat() if hasattr(current_end, 'isoformat') else str(current_end),
                    'end': next_start.isoformat() if hasattr(next_start, 'isoformat') else str(next_start),
                    'duration_minutes': gap
                })
        
        # Find longest meeting
        if events:
            longest_event = max(events, key=lambda x: (x['end_time'] - x['start_time']).total_seconds())
            longest_meeting = {
                'title': longest_event['title'],
                'duration_seconds': (longest_event['end_time'] - longest_event['start_time']).total_seconds(),
                'start_time': longest_event['start_time'].isoformat() if hasattr(longest_event['start_time'], 'isoformat') else str(longest_event['start_time']),
                'end_time': longest_event['end_time'].isoformat() if hasattr(longest_event['end_time'], 'isoformat') else str(longest_event['end_time'])
            }
        else:
            longest_meeting = None
        
        # Count back-to-back meetings
        back_to_back = 0
        for i in range(len(events) - 1):
            current_end = events[i]['end_time']
            next_start = events[i + 1]['start_time']
            gap = (next_start - current_end).total_seconds() / 60
            
            if gap <= 15:  # Less than 15 minutes gap
                back_to_back += 1
        
        # Determine meeting density
        if total_events >= 8:
            density = 'heavy'
        elif total_events >= 4:
            density = 'moderate'
        else:
            density = 'light'
        
        return {
            'total_events': total_events,
            'busy_hours': round(busy_hours, 1),
            'free_time_blocks': free_blocks,
            'meeting_density': density,
            'longest_meeting': longest_meeting,
            'back_to_back_meetings': back_to_back
        }

class GoogleDocsService:
    def __init__(self, access_token: str, refresh_token: str = None):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,
            client_secret=None
        )
        self.docs_service = build('docs', 'v1', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
    
    def get_recent_documents(self, days: int = 1) -> List[Dict]:
        """Get documents modified in the last N days"""
        try:
            # Calculate date range
            since_date = datetime.now() - timedelta(days=days)
            since_date_str = since_date.isoformat()
            
            # Search for documents
            query = f"mimeType='application/vnd.google-apps.document' and modifiedTime > '{since_date_str}'"
            
            results = self.drive_service.files().list(
                q=query,
                orderBy='modifiedTime desc',
                fields='files(id,name,modifiedTime,owners,lastModifyingUser,webViewLink)',
                pageSize=50
            ).execute()
            
            documents = []
            for file in results.get('files', []):
                doc_info = {
                    'id': file['id'],
                    'name': file['name'],
                    'modified_time': datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00')),
                    'web_link': file['webViewLink'],
                    'owners': file.get('owners', []),
                    'last_modifier': file.get('lastModifyingUser', {})
                }
                documents.append(doc_info)
            
            return documents
            
        except HttpError as error:
            logger.error(f"Drive API error: {error}")
            return []
    
    def get_document_content(self, document_id: str) -> Optional[Dict]:
        """Get the content of a specific document"""
        try:
            document = self.docs_service.documents().get(documentId=document_id).execute()
            
            # Extract text content
            content = ""
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for elem in paragraph.get('elements', []):
                        if 'textRun' in elem:
                            content += elem['textRun'].get('content', '')
            
            return {
                'id': document_id,
                'title': document.get('title', ''),
                'content': content.strip(),
                'word_count': len(content.split()),
                'char_count': len(content)
            }
            
        except HttpError as error:
            logger.error(f"Docs API error for document {document_id}: {error}")
            return None
    
    def get_documents_shared_with_user(self, days: int = 1) -> List[Dict]:
        """Get documents that were shared with the user in the last N days"""
        try:
            since_date = datetime.now() - timedelta(days=days)
            since_date_str = since_date.isoformat()
            
            # Search for documents shared with user
            query = f"mimeType='application/vnd.google-apps.document' and sharedWithMe and modifiedTime > '{since_date_str}'"
            
            results = self.drive_service.files().list(
                q=query,
                orderBy='modifiedTime desc',
                fields='files(id,name,modifiedTime,owners,lastModifyingUser,webViewLink,sharingUser)',
                pageSize=50
            ).execute()
            
            documents = []
            for file in results.get('files', []):
                doc_info = {
                    'id': file['id'],
                    'name': file['name'],
                    'modified_time': datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00')),
                    'web_link': file['webViewLink'],
                    'owners': file.get('owners', []),
                    'last_modifier': file.get('lastModifyingUser', {}),
                    'sharing_user': file.get('sharingUser', {}),
                    'is_shared': True
                }
                documents.append(doc_info)
            
            return documents
            
        except HttpError as error:
            logger.error(f"Drive API error: {error}")
            return []

def create_google_services(access_token: str, refresh_token: str = None) -> tuple:
    """Create Google Calendar and Docs services"""
    calendar_service = GoogleCalendarService(access_token, refresh_token)
    docs_service = GoogleDocsService(access_token, refresh_token)
    return calendar_service, docs_service