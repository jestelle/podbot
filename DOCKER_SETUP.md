# Docker Setup Guide for Podbot Deployment

## Installing Docker on macOS

### Option 1: Docker Desktop (Recommended)

1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Download Docker Desktop for Mac
   - Choose the right version for your Mac:
     - Apple Silicon (M1/M2/M3): `Docker Desktop for Mac with Apple Silicon`
     - Intel: `Docker Desktop for Mac with Intel chip`

2. **Install Docker Desktop**
   - Open the downloaded `.dmg` file
   - Drag Docker to Applications folder
   - Launch Docker Desktop
   - Complete the setup wizard

3. **Verify Installation**
   ```bash
   docker --version
   docker-compose --version
   ```

### Option 2: Using Homebrew

1. **Install Homebrew (if not already installed)**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Docker Desktop**
   ```bash
   brew install --cask docker
   ```

3. **Launch Docker Desktop**
   - Open Docker Desktop from Applications
   - Complete the setup

### Option 3: Command Line Only (Advanced)

```bash
# Install Docker and Docker Compose
brew install docker docker-compose

# Install Docker Machine (for managing Docker hosts)
brew install docker-machine

# Note: You'll still need Docker Desktop or a Docker daemon running
```

## Post-Installation Setup

1. **Start Docker Desktop**
   - Launch Docker Desktop from Applications
   - Wait for the Docker daemon to start (whale icon in menu bar)

2. **Test Docker Installation**
   ```bash
   # Test basic Docker functionality
   docker run hello-world
   
   # Test Docker Compose
   docker-compose --version
   ```

3. **Configure Docker Resources (Optional)**
   - Open Docker Desktop settings
   - Adjust CPU, Memory, and Disk limits as needed
   - For Podbot development, 4GB RAM and 2 CPUs are sufficient

## Docker for Podbot Development

### Local Development with Docker

1. **Build Backend Container**
   ```bash
   cd backend
   docker build -t podbot-backend .
   docker run -p 8000:8000 podbot-backend
   ```

2. **Build Frontend Container**
   ```bash
   cd frontend
   docker build -t podbot-frontend .
   docker run -p 3000:3000 podbot-frontend
   ```

### Docker Compose for Full Stack

Create `docker-compose.yml` in the root directory:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./podbot.db
      - ENVIRONMENT=development
    volumes:
      - ./backend:/app
      - ./backend/audio_files:/app/audio_files

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
```

Run with:
```bash
docker-compose up --build
```

## Troubleshooting

### Common Issues

1. **Docker Desktop won't start**
   - Restart your Mac
   - Check for macOS updates
   - Try reinstalling Docker Desktop

2. **Permission denied errors**
   ```bash
   sudo chown -R $(whoami) /var/run/docker.sock
   ```

3. **Build fails with "No space left on device"**
   ```bash
   # Clean up Docker images and containers
   docker system prune -a
   ```

4. **M1/M2 Mac compatibility issues**
   - Ensure you downloaded the Apple Silicon version
   - Use `--platform linux/amd64` for builds if needed

### Performance Tips

1. **Enable BuildKit for faster builds**
   ```bash
   export DOCKER_BUILDKIT=1
   ```

2. **Use .dockerignore files**
   - Already included in the Podbot project
   - Reduces build context size

3. **Multi-stage builds**
   - Both Dockerfiles use multi-stage builds for optimization

## Ready for Deployment

Once Docker is installed and working:

1. **Test local Docker builds**
   ```bash
   cd backend && docker build -t podbot-backend .
   cd ../frontend && docker build -t podbot-frontend .
   ```

2. **Run the deployment script**
   ```bash
   export GOOGLE_CLOUD_PROJECT_ID=your-project-id
   ./deploy.sh
   ```

Docker will be used by Google Cloud Build to create the production containers for Cloud Run deployment.

## Additional Resources

- [Docker Desktop Documentation](https://docs.docker.com/desktop/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Google Cloud Build Documentation](https://cloud.google.com/build/docs)

---

**Next Step**: Once Docker is installed, return to the deployment checklist and run `./deploy.sh`!