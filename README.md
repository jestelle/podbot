# Podbot - Personal Podcast Generator

Transform your daily schedule and documents into personalized podcasts. Podbot connects to your Google Calendar and Google Docs to create AI-generated audio summaries of your day, meetings, and important documents.

## Features

- **Daily Schedule Summaries**: Get your day organized with AI-generated summaries of your calendar events and meetings
- **Document Reviews**: Important documents shared with you get summarized and explained in podcast format
- **Personal RSS Feed**: Subscribe to your personalized podcast feed and listen anywhere with your favorite podcast app
- **Google Integration**: Seamlessly connects with Google Calendar and Google Docs
- **AI-Powered**: Uses OpenAI for content generation and text-to-speech

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd podbot
   ```

2. **Set up environment**:
   ```bash
   make setup-env
   # Edit .env file with your configuration
   ```

3. **Start development environment**:
   ```bash
   make dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Architecture

- **Backend**: Python FastAPI application handling authentication, data processing, and podcast generation
- **Frontend**: Next.js React application providing the user interface
- **Database**: PostgreSQL for user data and podcast metadata
- **Audio Storage**: Local filesystem (development) or Google Cloud Storage (production)
- **AI Services**: OpenAI for content generation and text-to-speech

## Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Google Cloud account (for OAuth and deployment)
- OpenAI API key

### Local Development

```bash
# Install dependencies
make install

# Start development servers
make dev

# Run tests
make test

# Build application
make build
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: Google OAuth credentials
- `OPENAI_API_KEY`: OpenAI API key for content generation
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: PostgreSQL connection string

## Deployment

The application is designed to deploy on Google Cloud Platform:

- **Cloud Run**: For backend API
- **Cloud Storage**: For audio file storage
- **Cloud SQL**: For PostgreSQL database
- **Cloud Build**: For CI/CD pipeline

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.
