# DocExpert Troubleshooting Guide

## Common Issues and Solutions

### 1. Deployment Issues

#### Permission Denied: `/app/logs/bot.log`
**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/app/logs/bot.log'
```

**Solution:**
The logging system now handles this gracefully:
```bash
# Check if logs directory exists and has correct permissions
ls -la logs/

# Fix permissions if needed
chmod 755 logs/
chmod 666 logs/*.log

# Or recreate with proper permissions
./setup.sh
```

**Verification:**
```bash
# Test logging setup
python -c "from app.utils.logging import setup_logging; setup_logging()"
```

#### MongoDB Atlas Connection Failed
**Symptoms:**
```
ServerSelectionTimeoutError: connection timeout
```

**Diagnosis:**
```bash
# Test MongoDB connection
python test_mongodb_atlas.py
```

**Solutions:**
1. **Check IP Whitelist:**
   - Go to MongoDB Atlas → Network Access
   - Add your current IP or `0.0.0.0/0` for testing
   - Wait 2-3 minutes for changes to propagate

2. **Verify Credentials:**
   ```bash
   # Check .env file
   grep MONGODB_URI .env
   
   # Ensure password doesn't contain special characters that need encoding
   # Use URL encoding for special characters: @ = %40, : = %3A, etc.
   ```

3. **Test Connection String:**
   ```bash
   # Install mongosh for testing
   npm install -g mongosh
   
   # Test connection directly
   mongosh "your_connection_string_here"
   ```

#### xAI API Key Issues
**Symptoms:**
```
HTTPError: 401 Unauthorized
```

**Solutions:**
1. **Verify API Key:**
   ```bash
   # Test xAI API key
   curl -H "Authorization: Bearer $XAI_API_KEY" \
        https://api.x.ai/v1/models
   ```

2. **Check Environment Loading:**
   ```bash
   # Verify .env file is loaded
   python -c "
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print('XAI_API_KEY:', os.getenv('XAI_API_KEY')[:10] + '...')
   "
   ```

3. **API Key Format:**
   - Ensure key starts with `xai-`
   - No extra spaces or quotes
   - Key should be around 64 characters

#### HuggingFace API Issues
**Symptoms:**
```
HTTPError: 429 Too Many Requests
```

**Solutions:**
1. **Check Rate Limits:**
   ```bash
   # Test HuggingFace API
   curl -H "Authorization: Bearer $HUGGINGFACE_API_KEY" \
        "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
   ```

2. **Rate Limit Handling:**
   - Free tier has rate limits
   - Consider upgrading to Pro plan
   - Implement request queuing

### 2. Docker Issues

#### Container Won't Start
**Symptoms:**
```
docker-compose up fails with exit code 1
```

**Diagnosis:**
```bash
# Check container logs
docker-compose logs telegram-bot

# Check container status
docker-compose ps

# Check resource usage
docker stats
```

**Solutions:**
1. **Memory Issues:**
   ```yaml
   # Add to docker-compose.yml
   services:
     telegram-bot:
       deploy:
         resources:
           limits:
             memory: 1G
           reservations:
             memory: 512M
   ```

2. **Environment Variables:**
   ```bash
   # Verify .env file exists
   ls -la .env
   
   # Check environment variables are loaded
   docker-compose config
   ```

#### Build Issues
**Symptoms:**
```
failed to solve: failed to read dockerfile
```

**Solutions:**
```bash
# Clean Docker cache
docker system prune -f

# Rebuild without cache
docker-compose build --no-cache

# Check Dockerfile syntax
docker build --dry-run .
```

### 3. Telegram Bot Issues

#### Bot Not Responding
**Symptoms:**
- Messages sent to bot but no response
- Bot appears offline

**Diagnosis:**
```bash
# Check bot health
curl http://localhost:8000/health

# Check webhook status
curl -X GET "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

**Solutions:**
1. **Webhook Issues:**
   ```bash
   # Delete webhook
   curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/deleteWebhook"
   
   # Reset webhook (if using webhook mode)
   curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
        -d "url=https://your-domain.com/webhook"
   ```

2. **Token Issues:**
   ```bash
   # Test bot token
   curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
   ```

#### File Upload Issues
**Symptoms:**
- Bot receives file but doesn't process it
- Error when uploading large files

**Solutions:**
1. **File Size Limits:**
   ```python
   # Check file size in handler
   if file_size > 20 * 1024 * 1024:  # 20MB limit
       await update.message.reply_text("File too large. Max size: 20MB")
   ```

2. **Format Support:**
   ```python
   # Supported formats
   SUPPORTED_FORMATS = ['.pdf', '.txt', '.docx', '.doc']
   ```

### 4. Performance Issues

#### Slow Response Times
**Symptoms:**
- Bot takes >30 seconds to respond
- Timeout errors

**Diagnosis:**
```bash
# Check performance logs
tail -f logs/performance.log

# Monitor resource usage
htop
```

**Solutions:**
1. **Database Optimization:**
   ```javascript
   // Create indexes in MongoDB
   db.documents.createIndex({ "user_id": 1, "created_at": -1 })
   db.documents.createIndex({ "embedding": "2dsphere" })
   ```

2. **Embedding Caching:**
   ```python
   # Implement caching
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_cached_embedding(text_hash):
       return embedding_service.encode(text)
   ```

#### Memory Leaks
**Symptoms:**
- Memory usage constantly increasing
- Container restarts due to OOM

**Solutions:**
```python
# Clean up large objects
import gc

async def process_document(document):
    try:
        # Process document
        result = await process_large_document(document)
        return result
    finally:
        # Force garbage collection
        gc.collect()
```

### 5. Data Issues

#### Embeddings Not Working
**Symptoms:**
- Search returns no results
- Embedding generation fails

**Diagnosis:**
```bash
# Test embedding service
python test_embedding_service.py
```

**Solutions:**
1. **HuggingFace API Issues:**
   ```python
   # Check API status
   import httpx
   
   async def test_hf_api():
       async with httpx.AsyncClient() as client:
           response = await client.get(
               "https://api-inference.huggingface.co/status"
           )
           print(response.json())
   ```

2. **Dimension Mismatch:**
   ```python
   # Verify embedding dimensions
   EXPECTED_DIMENSIONS = 384  # all-MiniLM-L6-v2
   
   embedding = await embedding_service.encode("test")
   assert len(embedding) == EXPECTED_DIMENSIONS
   ```

#### Database Corruption
**Symptoms:**
- Queries return unexpected results
- Index errors

**Solutions:**
```bash
# Backup database first
python test_mongodb_atlas.py

# Re-create indexes
mongosh "$MONGODB_URI" --eval "
  use telegram_bot;
  db.documents.dropIndexes();
  db.documents.createIndex({'user_id': 1, 'created_at': -1});
  db.documents.createIndex({'embedding': '2dsphere'});
"
```

### 6. YouTube Issues

#### Transcript Not Available
**Symptoms:**
```
NoTranscriptFound: No transcripts found for video
```

**Solutions:**
1. **Check Video Availability:**
   ```python
   # Verify video exists and has transcripts
   from youtube_transcript_api import YouTubeTranscriptApi
   
   try:
       transcript = YouTubeTranscriptApi.get_transcript('VIDEO_ID')
       print("Transcript available")
   except Exception as e:
       print(f"Error: {e}")
   ```

2. **Language Issues:**
   ```python
   # Try different languages
   languages = ['en', 'auto', 'en-US', 'en-GB']
   for lang in languages:
       try:
           transcript = YouTubeTranscriptApi.get_transcript('VIDEO_ID', languages=[lang])
           break
       except:
           continue
   ```

## Monitoring and Debugging

### 1. Health Monitoring

```bash
# Comprehensive health check
curl -s http://localhost:8000/health | jq '.'

# Monitor specific services
curl -s http://localhost:8000/health | jq '.services.database.status'
curl -s http://localhost:8000/health | jq '.services.embedding_service.status'
```

### 2. Log Analysis

```bash
# Real-time log monitoring
tail -f logs/bot.log | grep ERROR

# Performance analysis
grep "completed in" logs/performance.log | tail -20

# User activity
grep "User interaction" logs/user_interactions.log | tail -10

# Database operations
grep "MongoDB" logs/database.log | tail -15
```

### 3. Resource Monitoring

```bash
# Docker resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# System resources
htop
iotop
```

### 4. Network Debugging

```bash
# Test external connections
curl -I https://api.x.ai/v1/models
curl -I https://api-inference.huggingface.co/status
curl -I https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe

# DNS resolution
nslookup api.x.ai
nslookup cluster0.mongodb.net
```

## Emergency Procedures

### 1. Service Recovery

```bash
# Quick restart
make stop
make run

# Clean restart
docker-compose down -v
docker system prune -f
make run
```

### 2. Database Backup

```bash
# Create emergency backup
python -c "
from app.database.mongodb import MongoDB
import json
from datetime import datetime

db = MongoDB()
# Export critical collections
documents = list(db.documents.find())
with open(f'backup_{datetime.now().isoformat()}.json', 'w') as f:
    json.dump(documents, f, default=str)
"
```

### 3. Configuration Reset

```bash
# Reset to known good configuration
git checkout main -- docker-compose.yml
git checkout main -- Dockerfile
git checkout main -- requirements.txt

# Recreate environment
cp .env.example .env
# Edit .env with correct values
```

## Getting Help

### 1. Debugging Information to Collect

When reporting issues, include:

```bash
# System information
uname -a
docker --version
docker-compose --version

# Application logs
tail -50 logs/bot.log
tail -20 logs/database.log

# Configuration (remove sensitive data)
cat docker-compose.yml
env | grep -E "(EMBEDDING|LOG|MONGODB_DB)" | head -5

# Health status
curl -s http://localhost:8000/health | jq '.'
```

### 2. Support Channels

- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check ARCHITECTURE.md and API.md
- **Logs**: Enable DEBUG logging for detailed information

### 3. Self-Diagnosis Script

```bash
#!/bin/bash
# diagnose.sh - Quick system diagnosis

echo "🔍 DocExpert System Diagnosis"
echo "=============================="

echo "📊 System Status:"
echo "- Docker: $(docker --version)"
echo "- Compose: $(docker-compose --version)"
echo "- Python: $(python3 --version)"

echo "🐳 Container Status:"
docker-compose ps

echo "🔗 Service Health:"
curl -s http://localhost:8000/health | jq '.status' 2>/dev/null || echo "Service not responding"

echo "💾 Disk Space:"
df -h | grep -E "(Filesystem|/dev/)"

echo "🧠 Memory Usage:"
free -h

echo "📁 Log Files:"
ls -la logs/ 2>/dev/null || echo "No logs directory"

echo "🔧 Environment:"
echo "- .env exists: $([ -f .env ] && echo 'Yes' || echo 'No')"
echo "- Logs directory: $([ -d logs ] && echo 'Yes' || echo 'No')"

echo "✅ Diagnosis complete!"
```

This troubleshooting guide covers the most common issues and provides systematic approaches to diagnosing and resolving problems with DocExpert.
