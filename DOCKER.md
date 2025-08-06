# Docker Deployment Guide

This document provides comprehensive instructions for deploying DocExpert using Docker and Docker Compose.

## Quick Start

### 1. Prerequisites
```bash
# Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version

# Clone the repository
git clone <repository-url>
cd docexpert
```

### 2. Environment Setup
```bash
# Run setup script (creates directories and .env template)
./setup.sh

# Edit .env with your actual values
nano .env
```

Required environment variables:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from [@BotFather](https://t.me/botfather)
- `XAI_API_KEY`: Your xAI API key from [xAI Console](https://console.x.ai/)
- `HUGGINGFACE_API_KEY`: Your HuggingFace API key
- `MONGODB_URI`: MongoDB Atlas connection string

### 3. Deploy
```bash
# Standard deployment
make run

# Development deployment (with hot reload)
make dev

# Production deployment (with Nginx and optimizations)
make prod
```

### 4. Verify Deployment
```bash
# Check service status
make status

# View logs
make logs

# Test health endpoint
curl http://localhost:8000/health

# Test MongoDB Atlas connection
python test_mongodb_atlas.py
```

## Available Services

| Service | Port | Description |
|---------|------|-------------|
| telegram-bot | 8000 | Main bot application with FastAPI |
| nginx (prod only) | 80/443 | Reverse proxy for production |

**Note**: This project uses **MongoDB Atlas** (cloud database) instead of local MongoDB containers.

## Deployment Environments

### Development Environment
```bash
# Start development environment
make dev

# Features:
# - Hot reload on code changes
# - Debug logging enabled
# - Volume mounted for live editing
# - Faster startup times
```

### Production Environment
```bash
# Start production environment
make prod

# Features:
# - Nginx reverse proxy
# - Optimized Docker images
# - Resource limits
# - Log rotation
# - Health checks
# - Security hardening
```

### Standard Environment
```bash
# Start standard environment
make run

# Features:
# - Basic Docker Compose setup
# - Good for testing and staging
# - Health checks enabled
# - Volume persistence
```

## Docker Commands Reference

### Basic Operations
```bash
# Start services
make run              # Standard environment
make dev             # Development environment  
make prod            # Production environment

# Stop services
make stop            # Stop all services
make dev-stop        # Stop development environment
make prod-stop       # Stop production environment

# View logs
make logs            # Application logs
make dev-logs        # Development logs
make prod-logs       # Production logs

# Health and status
make health          # Check service health
make status          # Show service status
```

### Advanced Operations
```bash
# Build operations
make build           # Build production images
docker-compose build --no-cache  # Force rebuild

# Cleanup operations
make clean           # Clean Python cache
docker system prune -f  # Clean Docker resources
docker-compose down -v  # Remove all volumes

# Maintenance
make restart         # Restart services
docker-compose pull  # Update base images
```

## Configuration Files

### docker-compose.yml (Standard)
- Basic deployment configuration
- Suitable for testing and staging
- Uses local volume mounts
- Health checks enabled

### docker-compose.dev.yml (Development)
- Hot reload configuration
- Debug logging
- Live code mounting
- Development optimizations

### docker-compose.production.yml (Production)
- Production-ready configuration
- Nginx reverse proxy
- Resource limits and reservations
- Enhanced security settings
- Log aggregation (optional)

## Environment Variables

### Required Configuration
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
XAI_API_KEY=your_xai_api_key
```

### Optional
```env
MONGODB_URI=mongodb://admin:password@mongodb:27017/telegram_bot?authSource=admin
MONGODB_DB_NAME=telegram_bot
DOCUMENT_UPLOAD_PATH=uploads
LOG_LEVEL=INFO
```

## Volumes

The following directories are mounted as volumes:
- `./uploads:/app/uploads` - Document uploads
- `./logs:/app/logs` - Application logs
- `mongodb_data:/data/db` - MongoDB data persistence

## Troubleshooting

### Bot Not Starting
1. Check environment variables in `.env`
2. Verify Telegram bot token
3. Check logs: `make docker-logs`

### MongoDB Connection Issues
1. Ensure MongoDB container is running: `docker-compose ps`
2. Check MongoDB logs: `docker-compose logs mongodb`
3. Verify connection string in `.env`

### Permission Issues
```bash
# Fix upload directory permissions
sudo chown -R $USER:$USER uploads/
chmod 755 uploads/
```

### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port
```

## Development Setup

For development with auto-reload:
```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up

# The application will auto-reload on code changes
```

## Health Monitoring

The application includes health checks:
- Docker health check every 30 seconds
- Health endpoint: `GET /health`
- Automatic container restart on failure

Check container health:
```bash
docker ps
# Look for "healthy" status
```
