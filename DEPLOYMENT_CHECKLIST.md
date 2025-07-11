# Podbot Deployment Checklist

## Pre-Deployment Setup ✅

- [x] Backend Dockerfile created
- [x] Frontend environment configuration updated
- [x] Production environment templates created
- [x] CORS configuration updated for production
- [x] Deployment scripts created
- [x] Comprehensive deployment documentation written

## Required Accounts & Tools

- [x] Google Cloud Platform account with billing enabled
- [x] `gcloud` CLI installed and configured
- [x] Docker installed (for local testing)

## Google Cloud Setup

- [x] Create GCP project: `podbot-465604`
- [x] Enable required APIs:
  - [x] Cloud Build API
  - [x] Cloud Run Admin API
  - [x] Cloud SQL Admin API
  - [x] Cloud Storage API
- [ ] Set up Cloud SQL PostgreSQL instance
- [ ] Create Cloud Storage bucket for audio files
- [ ] Configure IAM roles and permissions

## Environment Variables

### Backend (.env.production)
- [ ] `ENVIRONMENT=production`
- [ ] `DATABASE_URL` (PostgreSQL connection string)
- [ ] `GOOGLE_CLIENT_ID` (OAuth client ID)
- [ ] `GOOGLE_CLIENT_SECRET` (OAuth client secret)
- [ ] `GOOGLE_REDIRECT_URI` (production callback URL)
- [ ] `OPENAI_API_KEY` (OpenAI API key)
- [ ] `SECRET_KEY` (JWT secret, 32+ chars)
- [ ] `GOOGLE_CLOUD_PROJECT_ID`
- [ ] `GOOGLE_CLOUD_STORAGE_BUCKET`

### Frontend (GCP Environment Variables)
- [ ] `NEXT_PUBLIC_API_URL` (backend URL)
- [ ] `NEXT_PUBLIC_FRONTEND_URL` (frontend URL)

## Deployment Steps

### Backend Deployment
- [ ] Set environment variables:
  ```bash
  export GOOGLE_CLOUD_PROJECT_ID=your-project-id
  export GOOGLE_CLOUD_REGION=us-central1
  ```
- [ ] Run deployment script: `./deploy.sh`
- [ ] Or manual deployment: `gcloud builds submit --config cloudbuild.yaml`
- [ ] Verify backend health: `curl https://your-backend-url/health`

### Frontend Deployment
- [ ] Frontend builds with Docker
- [ ] Deploy to Cloud Run: `gcloud builds submit`
- [ ] Verify frontend loads correctly

## Post-Deployment Configuration

### Google OAuth Setup
- [ ] Update Google OAuth redirect URIs:
  - [ ] `https://your-backend-url/auth/google/callback`
  - [ ] `https://your-frontend-url/auth/callback`

### Testing
- [ ] Test Google OAuth login flow
- [ ] Test calendar and documents preview
- [ ] Generate welcome podcast
- [ ] Generate daily podcast
- [ ] Test audio playback
- [ ] Test RSS feed: `https://your-backend-url/rss/[uuid]`
- [ ] Test RSS feed in podcast app

### Security & Performance
- [ ] Enable HTTPS (automatic with Cloud Run/Vercel)
- [ ] Set up monitoring and alerting
- [ ] Configure rate limiting (if needed)
- [ ] Set up backup strategy

## Optional Enhancements

- [ ] Custom domain setup
- [ ] CDN configuration
- [ ] Advanced monitoring with Cloud Monitoring
- [ ] Automated daily podcast generation (Cloud Scheduler)
- [ ] Error reporting and logging
- [ ] Performance optimization

## Production URLs

After deployment, update these URLs:

- **Backend**: `https://podbot-backend-[hash]-uc.a.run.app`
- **Frontend**: `https://podbot-frontend-[hash]-uc.a.run.app` (or custom domain)
- **RSS Feed**: `https://[backend-url]/rss/[user-uuid]`

## Quick Commands Reference

```bash
# Deploy backend
export GOOGLE_CLOUD_PROJECT_ID=your-project-id
./deploy.sh

# Deploy both backend and frontend
./deploy.sh

# View logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Update environment variables
gcloud run services update podbot-backend --region=us-central1 --set-env-vars="KEY=value"
```

## Support

- Detailed instructions: `DEPLOYMENT.md`
- Troubleshooting: Check logs with commands above
- Issues: Create GitHub issue or check documentation

---

**Ready to deploy? Start with the "Google Cloud Setup" section!** 🚀