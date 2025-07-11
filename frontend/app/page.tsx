'use client';

import { useState } from 'react';
import { PlayIcon, CalendarIcon, DocumentIcon, RssIcon } from '@heroicons/react/24/outline';

export default function Home() {
  const [isSignedIn, setIsSignedIn] = useState(false);

  const handleGoogleSignIn = () => {
    // TODO: Implement Google OAuth
    console.log('Google Sign In clicked');
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <PlayIcon className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">Podbot</span>
            </div>
            <div>
              {!isSignedIn ? (
                <button
                  onClick={handleGoogleSignIn}
                  className="btn-primary"
                >
                  Sign in with Google
                </button>
              ) : (
                <div className="flex items-center space-x-4">
                  <span className="text-gray-700">Welcome back!</span>
                  <button className="btn-secondary">Dashboard</button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
            Your Personal
            <span className="text-primary-600"> Podcast Generator</span>
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Transform your daily schedule and documents into personalized podcasts. 
            Get your day summarized, meetings briefed, and documents reviewed - all in audio format.
          </p>
          <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
            <div className="rounded-md shadow">
              <button
                onClick={handleGoogleSignIn}
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-lg md:px-10"
              >
                Get Started Free
              </button>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card text-center">
              <CalendarIcon className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Daily Schedule Summary</h3>
              <p className="text-gray-600">
                Get your day organized with AI-generated summaries of your calendar events, 
                meetings, and schedule patterns.
              </p>
            </div>
            <div className="card text-center">
              <DocumentIcon className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Document Reviews</h3>
              <p className="text-gray-600">
                Important documents shared with you get summarized and explained in 
                easy-to-understand podcast format.
              </p>
            </div>
            <div className="card text-center">
              <RssIcon className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Personal RSS Feed</h3>
              <p className="text-gray-600">
                Subscribe to your personalized podcast feed and listen anywhere, 
                anytime with your favorite podcast app.
              </p>
            </div>
          </div>
        </div>

        {/* How it works */}
        <div className="mt-20">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How Podbot Works
          </h2>
          <div className="space-y-8">
            <div className="flex items-center space-x-6">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold">
                  1
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Connect Your Google Account</h3>
                <p className="text-gray-600">
                  Securely connect your Google Calendar and Google Docs to get started.
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold">
                  2
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">AI Analyzes Your Data</h3>
                <p className="text-gray-600">
                  Our AI reviews your calendar and recent documents to create personalized content.
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold">
                  3
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Daily Podcast Delivered</h3>
                <p className="text-gray-600">
                  Wake up to a fresh podcast episode tailored to your day and priorities.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}