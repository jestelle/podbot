#!/bin/bash

# Podbot Deployment Script for Google Cloud Platform (Full GCP Deployment)

set -e

echo "🚀 Starting Podbot deployment to GCP..."

# Check if required environment variables are set
if [ -z "$GOOGLE_CLOUD_PROJECT_ID" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT_ID environment variable is not set"
    exit 1
fi

if [ -z "$GOOGLE_CLOUD_REGION" ]; then
    export GOOGLE_CLOUD_REGION="us-central1"
    echo "Using default region: $GOOGLE_CLOUD_REGION"
fi

# Set project ID
gcloud config set project $GOOGLE_CLOUD_PROJECT_ID

echo "📦 Building and deploying backend..."

# Build and deploy backend to Cloud Run
cd backend
gcloud builds submit --config cloudbuild.yaml --substitutions=PROJECT_ID=$GOOGLE_CLOUD_PROJECT_ID

echo "🎉 Backend deployed successfully!"

# Get the backend URL
BACKEND_URL=$(gcloud run services describe podbot-backend --region=$GOOGLE_CLOUD_REGION --format="value(status.url)")
echo "Backend URL: $BACKEND_URL"

echo "📱 Building and deploying frontend..."

# Build and deploy frontend to Cloud Run
cd ../frontend

# Create production environment for frontend
cat > .env.production << EOL
NEXT_PUBLIC_API_URL=$BACKEND_URL
NEXT_PUBLIC_FRONTEND_URL=https://podbot-frontend-[hash].run.app
EOL

# Deploy frontend
gcloud builds submit --config cloudbuild.yaml --substitutions=PROJECT_ID=$GOOGLE_CLOUD_PROJECT_ID

echo "🎉 Frontend deployed successfully!"

# Get the frontend URL
FRONTEND_URL=$(gcloud run services describe podbot-frontend --region=$GOOGLE_CLOUD_REGION --format="value(status.url)")
echo "Frontend URL: $FRONTEND_URL"

echo "🔧 Updating frontend environment with actual URL..."

# Update frontend environment variables with actual URL
gcloud run services update podbot-frontend \
  --region=$GOOGLE_CLOUD_REGION \
  --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL,NEXT_PUBLIC_FRONTEND_URL=$FRONTEND_URL"

echo "✅ Full GCP deployment complete!"
echo ""
echo "🎯 Your Podbot URLs:"
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
echo ""
echo "📋 Next steps:"
echo "1. Update Google OAuth redirect URIs:"
echo "   - $BACKEND_URL/auth/google/callback"
echo "   - $FRONTEND_URL/auth/callback"
echo "2. Test the deployment"
echo "3. Set up custom domain (optional)"
echo "4. Configure monitoring and alerts"
echo ""
echo "🎉 Podbot is now live!"