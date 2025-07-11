'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService, User, PodcastEpisode } from '@/lib/auth';
import { PlayIcon, CalendarIcon, DocumentIcon, RssIcon, EyeIcon, SparklesIcon, StopIcon } from '@heroicons/react/24/outline';

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [episodes, setEpisodes] = useState<PodcastEpisode[]>([]);
  const [loading, setLoading] = useState(true);
  const [calendarData, setCalendarData] = useState<any>(null);
  const [documentsData, setDocumentsData] = useState<any>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [generatingPodcast, setGeneratingPodcast] = useState(false);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<number | null>(null);
  const [audioRef, setAudioRef] = useState<HTMLAudioElement | null>(null);
  const [audioLoading, setAudioLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const loadUserData = async () => {
      try {
        if (!authService.isAuthenticated()) {
          router.push('/');
          return;
        }

        const currentUser = await authService.getCurrentUser();
        if (!currentUser) {
          router.push('/');
          return;
        }

        setUser(currentUser);
        
        // Load user's episodes
        const userEpisodes = await authService.getUserEpisodes(currentUser.id);
        setEpisodes(userEpisodes);
        
      } catch (error) {
        console.error('Failed to load user data:', error);
        router.push('/');
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, [router]);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef) {
        audioRef.pause();
        audioRef.currentTime = 0;
      }
    };
  }, [audioRef]);

  const handleLogout = () => {
    authService.logout();
    router.push('/');
  };

  const copyRssUrl = () => {
    if (user) {
      const fullRssUrl = `http://localhost:8000${user.rss_feed_url}`;
      navigator.clipboard.writeText(fullRssUrl);
      alert('RSS feed URL copied to clipboard!');
    }
  };

  const loadCalendarPreview = async () => {
    if (!user) return;
    setLoadingPreview(true);
    try {
      const response = await fetch(`http://localhost:8000/users/${user.id}/calendar-preview`, {
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCalendarData(data);
      }
    } catch (error) {
      console.error('Failed to load calendar preview:', error);
    } finally {
      setLoadingPreview(false);
    }
  };

  const loadDocumentsPreview = async () => {
    if (!user) return;
    setLoadingPreview(true);
    try {
      const response = await fetch(`http://localhost:8000/users/${user.id}/documents-preview`, {
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setDocumentsData(data);
      }
    } catch (error) {
      console.error('Failed to load documents preview:', error);
    } finally {
      setLoadingPreview(false);
    }
  };

  const generatePodcast = async () => {
    if (!user) return;
    setGeneratingPodcast(true);
    try {
      const response = await fetch(`http://localhost:8000/generate-podcast/${user.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        alert('Podcast generated successfully!');
        // Refresh episodes
        const userEpisodes = await authService.getUserEpisodes(user.id);
        setEpisodes(userEpisodes);
      } else {
        const errorData = await response.json();
        alert(`Failed to generate podcast: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Failed to generate podcast:', error);
      alert('Failed to generate podcast. Please try again.');
    } finally {
      setGeneratingPodcast(false);
    }
  };

  const generateWelcomePodcast = async () => {
    if (!user) return;
    setGeneratingPodcast(true);
    try {
      const response = await fetch(`http://localhost:8000/generate-welcome-podcast/${user.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        alert('Welcome podcast generated successfully!');
        // Refresh episodes
        const userEpisodes = await authService.getUserEpisodes(user.id);
        setEpisodes(userEpisodes);
      } else {
        const errorData = await response.json();
        alert(`Failed to generate welcome podcast: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Failed to generate welcome podcast:', error);
      alert('Failed to generate welcome podcast. Please try again.');
    } finally {
      setGeneratingPodcast(false);
    }
  };

  const playEpisode = (episode: PodcastEpisode) => {
    // Stop current audio if playing
    if (audioRef) {
      audioRef.pause();
      audioRef.currentTime = 0;
    }

    setAudioLoading(true);
    
    // Create new audio element
    const audio = new Audio(episode.audio_url);
    setAudioRef(audio);
    setCurrentlyPlaying(episode.id);

    // Handle audio events
    audio.addEventListener('canplaythrough', () => {
      setAudioLoading(false);
    });

    audio.addEventListener('loadstart', () => {
      setAudioLoading(true);
    });

    audio.addEventListener('ended', () => {
      setCurrentlyPlaying(null);
      setAudioRef(null);
      setAudioLoading(false);
    });

    audio.addEventListener('error', (e) => {
      console.error('Audio error:', e);
      alert('Error loading audio file. The audio may not be available yet.');
      setCurrentlyPlaying(null);
      setAudioRef(null);
      setAudioLoading(false);
    });

    // Play the audio
    audio.play().catch(error => {
      console.error('Error playing audio:', error);
      alert('Error playing audio. Please check if the audio file exists.');
      setCurrentlyPlaying(null);
      setAudioRef(null);
      setAudioLoading(false);
    });
  };

  const stopEpisode = () => {
    if (audioRef) {
      audioRef.pause();
      audioRef.currentTime = 0;
      setCurrentlyPlaying(null);
      setAudioRef(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <PlayIcon className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">Podbot</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user.email}</span>
              <button
                onClick={handleLogout}
                className="btn-secondary"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Podcast Dashboard</h1>
          <p className="text-gray-600">
            Your personalized podcast feed is being generated daily. Here's what's ready for you.
          </p>
        </div>

        {/* RSS Feed Card */}
        <div className="card mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <RssIcon className="h-8 w-8 text-primary-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Your RSS Feed</h3>
                <p className="text-gray-600">Subscribe to this feed in your favorite podcast app</p>
              </div>
            </div>
            <button
              onClick={copyRssUrl}
              className="btn-primary"
            >
              Copy RSS URL
            </button>
          </div>
          <div className="mt-4 p-3 bg-gray-100 rounded-lg">
            <code className="text-sm text-gray-800">
              http://localhost:8000{user.rss_feed_url}
            </code>
          </div>
        </div>

        {/* Google Data Preview */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Calendar Preview</h3>
              <button
                onClick={loadCalendarPreview}
                disabled={loadingPreview}
                className="btn-secondary flex items-center"
              >
                <EyeIcon className="h-4 w-4 mr-1" />
                {loadingPreview ? 'Loading...' : 'Preview'}
              </button>
            </div>
            
            {calendarData ? (
              <div className="space-y-3">
                <div className="text-sm text-gray-600">
                  <strong>Today's Schedule:</strong> {calendarData.analysis.total_events} events, {calendarData.analysis.busy_hours} busy hours
                </div>
                <div className="text-sm text-gray-600">
                  <strong>Meeting Density:</strong> {calendarData.analysis.meeting_density}
                </div>
                <div className="text-sm text-gray-600">
                  <strong>Calendars:</strong> {calendarData.calendars_info?.length || 0} calendars accessible
                </div>
                {calendarData.events.length === 0 ? (
                  <div className="text-sm text-gray-500 py-2">
                    No events found today across {calendarData.calendars_info?.length || 0} calendars
                  </div>
                ) : (
                  calendarData.events.slice(0, 3).map((event: any, index: number) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-3 py-2">
                      <div className="font-medium">{event.title}</div>
                      <div className="text-sm text-gray-600">
                        {new Date(event.start_time).toLocaleTimeString()} - {new Date(event.end_time).toLocaleTimeString()}
                      </div>
                      {event.calendar && (
                        <div className="text-xs text-gray-500">
                          📅 {event.calendar.name}
                        </div>
                      )}
                    </div>
                  ))
                )}
                {calendarData.events.length > 3 && (
                  <div className="text-sm text-gray-500">
                    ... and {calendarData.events.length - 3} more events
                  </div>
                )}
              </div>
            ) : (
              <div className="text-gray-500">
                Click "Preview" to see your calendar data
              </div>
            )}
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Documents Preview</h3>
              <button
                onClick={loadDocumentsPreview}
                disabled={loadingPreview}
                className="btn-secondary flex items-center"
              >
                <EyeIcon className="h-4 w-4 mr-1" />
                {loadingPreview ? 'Loading...' : 'Preview'}
              </button>
            </div>
            
            {documentsData ? (
              <div className="space-y-3">
                <div className="text-sm text-gray-600">
                  <strong>Recent Documents:</strong> {documentsData.recent_documents.length}
                </div>
                <div className="text-sm text-gray-600">
                  <strong>Shared Documents:</strong> {documentsData.shared_documents.length}
                </div>
                {[...documentsData.recent_documents, ...documentsData.shared_documents].slice(0, 3).map((doc: any, index: number) => (
                  <div key={index} className="border-l-4 border-green-500 pl-3 py-2">
                    <div className="font-medium">{doc.name}</div>
                    <div className="text-sm text-gray-600">
                      Modified: {new Date(doc.modified_time).toLocaleString()}
                    </div>
                  </div>
                ))}
                {([...documentsData.recent_documents, ...documentsData.shared_documents].length > 3) && (
                  <div className="text-sm text-gray-500">
                    ... and {[...documentsData.recent_documents, ...documentsData.shared_documents].length - 3} more documents
                  </div>
                )}
              </div>
            ) : (
              <div className="text-gray-500">
                Click "Preview" to see your documents data
              </div>
            )}
          </div>
        </div>

        {/* Podcast Generation */}
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate Podcast</h2>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={generatePodcast}
              disabled={generatingPodcast}
              className="btn-primary flex items-center"
            >
              <SparklesIcon className="h-4 w-4 mr-2" />
              {generatingPodcast ? 'Generating...' : 'Generate Daily Podcast'}
            </button>
            <button
              onClick={generateWelcomePodcast}
              disabled={generatingPodcast}
              className="btn-secondary flex items-center"
            >
              <PlayIcon className="h-4 w-4 mr-2" />
              {generatingPodcast ? 'Generating...' : 'Generate Welcome Podcast'}
            </button>
          </div>
          <p className="text-sm text-gray-600 mt-3">
            Generate a podcast based on your current calendar and documents. This uses AI to create both the script and audio.
          </p>
        </div>

        {/* Episodes List */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Episodes</h2>
          
          {episodes.length === 0 ? (
            <div className="text-center py-8">
              <div className="mb-4">
                <CalendarIcon className="h-12 w-12 text-gray-400 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No episodes yet</h3>
              <p className="text-gray-600 mb-4">
                Your first podcast episode will be generated automatically. 
                This usually happens early in the morning based on your calendar and recent documents.
              </p>
              <div className="flex justify-center space-x-4">
                <div className="flex items-center text-sm text-gray-500">
                  <CalendarIcon className="h-4 w-4 mr-1" />
                  Daily schedule summaries
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <DocumentIcon className="h-4 w-4 mr-1" />
                  Document reviews
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {episodes.map((episode) => (
                <div key={episode.id} className={`border rounded-lg p-4 ${currentlyPlaying === episode.id ? 'border-blue-500 bg-blue-50' : ''}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{episode.title}</h3>
                      <p className="text-gray-600 mt-1">{episode.description}</p>
                      <div className="flex items-center mt-2 text-sm text-gray-500">
                        <span>
                          {Math.floor(episode.duration_seconds / 60)}:{(episode.duration_seconds % 60).toString().padStart(2, '0')}
                        </span>
                        <span className="mx-2">•</span>
                        <span>{new Date(episode.published_at).toLocaleDateString()}</span>
                        <span className="mx-2">•</span>
                        <span className="capitalize">{episode.episode_type}</span>
                      </div>
                    </div>
                    {episode.audio_url && (
                      <div className="ml-4">
                        {currentlyPlaying === episode.id ? (
                          <button 
                            onClick={stopEpisode}
                            className="btn-secondary flex items-center"
                          >
                            <StopIcon className="h-4 w-4 mr-1" />
                            Stop
                          </button>
                        ) : (
                          <button 
                            onClick={() => playEpisode(episode)}
                            disabled={audioLoading}
                            className="btn-primary flex items-center disabled:opacity-50"
                          >
                            {audioLoading ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1"></div>
                                Loading...
                              </>
                            ) : (
                              <>
                                <PlayIcon className="h-4 w-4 mr-1" />
                                Play
                              </>
                            )}
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}