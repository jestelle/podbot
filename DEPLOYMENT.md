# Podbot Deployment Guide

This guide will help you deploy Podbot to production using Google Cloud Platform and Vercel.

## Prerequisites

1. **Google Cloud Platform Account**
   - Create a new project or use existing one
   - Enable billing
   - Install `gcloud` CLI tool

2. **Vercel Account**
   - Sign up at vercel.com
   - Install `vercel` CLI tool

3. **Domain (Optional)**
   - Custom domain for your deployment

## Step 1: Set Up Google Cloud Platform

### 1.1 Create a New Project
```bash
gcloud projects create podbot-prod-[YOUR-SUFFIX]
gcloud config set project podbot-prod-[YOUR-SUFFIX]
```

### 1.2 Enable Required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
```

### 1.3 Set Up Cloud SQL (PostgreSQL)
```bash
# Create Cloud SQL instance
gcloud sql instances create podbot-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create podbot --instance=podbot-db

# Create database user
gcloud sql users create podbot-user \
  --instance=podbot-db \
  --password=[SECURE-PASSWORD]
```

### 1.4 Set Up Cloud Storage
```bash
# Create storage bucket for audio files
gsutil mb gs://podbot-audio-[YOUR-SUFFIX]

# Make bucket publicly readable
gsutil iam ch allUsers:objectViewer gs://podbot-audio-[YOUR-SUFFIX]
```

## Step 2: Configure Environment Variables

### 2.1 Backend Environment Variables

Create `.env.production` in the `backend/` directory:

```env
# Copy from .env.production.template and fill in:
ENVIRONMENT=production
DATABASE_URL=postgresql://podbot-user:[PASSWORD]@[CLOUD-SQL-IP]:5432/podbot
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_REDIRECT_URI=https://your-backend-url/auth/google/callback
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-super-secret-jwt-key-min-32-chars
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_STORAGE_BUCKET=podbot-audio-[YOUR-SUFFIX]
AUDIO_BASE_URL=https://your-backend-url/audio
```

### 2.2 Set Cloud Run Environment Variables
```bash
gcloud run services update podbot-backend \
  --region=us-central1 \
  --set-env-vars="ENVIRONMENT=production,DATABASE_URL=postgresql://...,GOOGLE_CLIENT_ID=...,GOOGLE_CLIENT_SECRET=...,OPENAI_API_KEY=...,SECRET_KEY=..."
```

## Step 3: Deploy Backend to Cloud Run

### 3.1 Set Environment Variables
```bash
export GOOGLE_CLOUD_PROJECT_ID=your-project-id
export GOOGLE_CLOUD_REGION=us-central1
```

### 3.2 Run Deployment Script
```bash
./deploy.sh
```

### 3.3 Manual Deployment (Alternative)
```bash
cd backend
gcloud builds submit --config cloudbuild.yaml --substitutions=PROJECT_ID=your-project-id
```

## Step 4: Deploy Frontend to Vercel

### 4.1 Set Up Environment Variables in Vercel
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Enter your Cloud Run backend URL: https://podbot-backend-[hash]-uc.a.run.app

vercel env add NEXT_PUBLIC_FRONTEND_URL production
# Enter your Vercel URL: https://podbot.vercel.app
```

### 4.2 Deploy Frontend
```bash
cd frontend
vercel --prod
```

## Step 5: Update Google OAuth Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" → "Credentials"
3. Edit your OAuth 2.0 client ID
4. Add authorized redirect URIs:
   - `https://your-backend-url/auth/google/callback`
   - `https://your-frontend-url/auth/callback`

## Step 6: Test Your Deployment

1. **Test Backend Health**
   ```bash
   curl https://your-backend-url/health
   ```

2. **Test Frontend**
   - Visit your frontend URL
   - Try Google OAuth login
   - Generate a test podcast
   - Test RSS feed

## Step 7: Set Up Custom Domain (Optional)

### 7.1 Backend Domain
```bash
gcloud run domain-mappings create \
  --service=podbot-backend \
  --domain=api.your-domain.com \
  --region=us-central1
```

### 7.2 Frontend Domain
In Vercel dashboard:
1. Go to your project settings
2. Add custom domain
3. Update DNS records as instructed

## Step 8: Set Up Monitoring (Optional)

### 8.1 Cloud Monitoring
```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# Set up alerts for Cloud Run service
gcloud alpha monitoring policies create --policy-from-file=monitoring-policy.yaml
```

### 8.2 Logging
```bash
# View logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50
```

## Environment Variables Reference

### Backend Required Variables
- `ENVIRONMENT` - Set to "production"
- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `GOOGLE_REDIRECT_URI` - OAuth redirect URI
- `OPENAI_API_KEY` - OpenAI API key
- `SECRET_KEY` - JWT secret key (32+ characters)

### Frontend Required Variables
- `NEXT_PUBLIC_API_URL` - Backend URL
- `NEXT_PUBLIC_FRONTEND_URL` - Frontend URL

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check Cloud SQL instance is running
   - Verify connection string format
   - Check firewall rules

2. **OAuth Redirect Issues**
   - Verify redirect URIs in Google Console
   - Check CORS configuration
   - Ensure HTTPS is used in production

3. **Audio File Issues**
   - Check Cloud Storage bucket permissions
   - Verify audio file paths
   - Check CORS on storage bucket

### Logs and Debugging

```bash
# View Cloud Run logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=podbot-backend" --limit=100

# View build logs
gcloud builds log [BUILD-ID]
```

## Security Considerations

1. **Environment Variables**
   - Use Cloud Secret Manager for sensitive data
   - Rotate secrets regularly
   - Use least privilege access

2. **Database Security**
   - Use SSL connections
   - Regular backups
   - Monitor access logs

3. **API Security**
   - Implement rate limiting
   - Use HTTPS only
   - Validate all inputs

## Cost Optimization

1. **Cloud Run**
   - Use minimum instances: 0
   - Set appropriate memory limits
   - Monitor cold starts

2. **Cloud SQL**
   - Use appropriate instance size
   - Enable automatic backups
   - Monitor usage

3. **Cloud Storage**
   - Set up lifecycle policies
   - Monitor storage usage
   - Use appropriate storage class

## Maintenance

1. **Regular Updates**
   - Update dependencies
   - Monitor security advisories
   - Test deployments in staging

2. **Monitoring**
   - Set up alerts for errors
   - Monitor performance metrics
   - Track usage patterns

3. **Backups**
   - Regular database backups
   - Code repository backups
   - Environment configuration backups

---

For issues or questions, refer to the main README.md or create an issue in the repository.