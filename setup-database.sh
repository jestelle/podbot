#!/bin/bash

# Database setup script for Podbot

set -e

echo "🗄️  Setting up Cloud SQL database..."

# Generate a secure password
DB_PASSWORD=$(openssl rand -base64 32)
echo "Generated database password: $DB_PASSWORD"

# Create database
echo "Creating database..."
gcloud sql databases create podbot --instance=podbot-db

# Create database user
echo "Creating database user..."
gcloud sql users create podbot-user \
  --instance=podbot-db \
  --password="$DB_PASSWORD"

# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe podbot-db --format="value(connectionName)")
echo "Connection name: $CONNECTION_NAME"

# Create final database URL
DATABASE_URL="postgresql://podbot-user:$DB_PASSWORD@/podbot?host=/cloudsql/$CONNECTION_NAME"

echo "✅ Database setup complete!"
echo ""
echo "📋 Update your .env.production file with:"
echo "DATABASE_URL=$DATABASE_URL"
echo ""
echo "🔐 Save this password securely: $DB_PASSWORD"