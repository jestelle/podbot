'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService, User, PodcastEpisode } from '@/lib/auth';
import { PlayIcon, CalendarIcon, DocumentIcon, RssIcon } from '@heroicons/react/24/outline';

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [episodes, setEpisodes] = useState<PodcastEpisode[]>([]);
  const [loading, setLoading] = useState(true);
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
                <div key={episode.id} className="border rounded-lg p-4">
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
                      <button className="btn-primary ml-4">
                        <PlayIcon className="h-4 w-4 mr-1" />
                        Play
                      </button>
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