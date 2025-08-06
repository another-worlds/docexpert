# DocExpert Deployment Guide

## Deployment Options

### 1. Local Development
Quick setup for development and testing.

### 2. Cloud Deployment
Production-ready deployment on cloud platforms.

### 3. Container Orchestration
Kubernetes or Docker Swarm deployment.

## Prerequisites

### Required Accounts & Services
- **Telegram Bot**: Get token from [@BotFather](https://t.me/botfather)
- **xAI Account**: Get API key from [xAI Console](https://console.x.ai/)
- **HuggingFace Account**: Get API token from [HuggingFace](https://huggingface.co/settings/tokens)
- **MongoDB Atlas**: Create free cluster at [MongoDB Atlas](https://cloud.mongodb.com/)

### Required Software
- **Docker** (v20.10+)
- **Docker Compose** (v2.0+)
- **Git**
- **Python 3.11+** (for local development)

## Quick Deployment

### 1. Clone Repository
```bash
git clone https://github.com/your-username/docexpert.git
cd docexpert
```

### 2. Setup Environment
```bash
# Run setup script
./setup.sh

# Edit configuration
nano .env
```

### 3. Configure Services

#### MongoDB Atlas Setup
1. Create account at [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a new cluster (free tier is sufficient for testing)
3. Create database user:
   - Username: `docexpert`
   - Password: Generate secure password
   - Permissions: Read and write to any database
4. Configure Network Access:
   - Add current IP address
   - For cloud deployment, add `0.0.0.0/0` (restrict in production)
5. Get connection string:
   - Click "Connect" → "Connect your application"
   - Copy connection string
   - Replace `<password>` with your actual password

#### Environment Configuration
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# AI API Keys
XAI_API_KEY=xai-1234567890abcdef
HUGGINGFACE_API_KEY=hf_1234567890abcdef

# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://docexpert:password@cluster0.mongodb.net/
MONGODB_DB_NAME=docexpert_bot

# Service Configuration
EMBEDDING_SERVICE=huggingface
LOG_LEVEL=INFO
```

### 4. Deploy
```bash
# Standard deployment
make run

# Check status
make status

# View logs
make logs
```

## Production Deployment

### 1. Google Cloud Platform

#### Prerequisites
- Google Cloud account
- `gcloud` CLI installed
- Docker registry access

#### Deploy to Cloud Run
```bash
# Build and push image
docker build -t gcr.io/your-project/docexpert:latest .
docker push gcr.io/your-project/docexpert:latest

# Deploy to Cloud Run
gcloud run deploy docexpert \
  --image gcr.io/your-project/docexpert:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars="TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,XAI_API_KEY=$XAI_API_KEY"
```

#### Deploy to GKE
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docexpert
spec:
  replicas: 2
  selector:
    matchLabels:
      app: docexpert
  template:
    metadata:
      labels:
        app: docexpert
    spec:
      containers:
      - name: docexpert
        image: gcr.io/your-project/docexpert:latest
        ports:
        - containerPort: 8000
        env:
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: docexpert-secrets
              key: telegram-token
        - name: XAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: docexpert-secrets
              key: xai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### 2. AWS Deployment

#### Deploy to ECS
```bash
# Create task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create or update service
aws ecs create-service \
  --cluster docexpert-cluster \
  --service-name docexpert \
  --task-definition docexpert:1 \
  --desired-count 2
```

#### Deploy to EC2
```bash
# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --count 1 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-12345678 \
  --user-data file://user-data.sh
```

### 3. DigitalOcean App Platform

#### app.yaml
```yaml
name: docexpert
region: nyc
services:
- name: bot
  source_dir: /
  github:
    repo: your-username/docexpert
    branch: main
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: TELEGRAM_BOT_TOKEN
    value: ${TELEGRAM_BOT_TOKEN}
    type: SECRET
  - key: XAI_API_KEY
    value: ${XAI_API_KEY}
    type: SECRET
  - key: MONGODB_URI
    value: ${MONGODB_URI}
    type: SECRET
```

## Advanced Configurations

### 1. Load Balancing

#### Nginx Configuration
```nginx
upstream docexpert_backend {
    server docexpert_1:8000;
    server docexpert_2:8000;
    server docexpert_3:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://docexpert_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        access_log off;
        proxy_pass http://docexpert_backend/health;
    }
}
```

### 2. SSL/TLS Configuration

#### Let's Encrypt with Certbot
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Monitoring Setup

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'docexpert'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
    scrape_interval: 5s
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "DocExpert Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
          }
        ]
      }
    ]
  }
}
```

## Scaling Strategies

### 1. Horizontal Scaling

#### Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.production.yml docexpert

# Scale services
docker service scale docexpert_bot=3
```

#### Kubernetes
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: docexpert-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: docexpert
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. Database Scaling

#### MongoDB Atlas Auto-Scaling
```javascript
// Enable auto-scaling in MongoDB Atlas
{
  "replicationSpec": {
    "regionConfigs": [{
      "regionName": "US_EAST_1",
      "providerSettings": {
        "providerName": "AWS",
        "instanceSizeName": "M30",
        "autoScaling": {
          "compute": {
            "enabled": true,
            "scaleDownEnabled": true,
            "minInstanceSize": "M30",
            "maxInstanceSize": "M60"
          },
          "diskGBEnabled": true
        }
      }
    }]
  }
}
```

## Security Hardening

### 1. Container Security

#### Dockerfile Best Practices
```dockerfile
# Use specific version tags
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r docexpert && useradd -r -g docexpert docexpert

# Set secure permissions
COPY --chown=docexpert:docexpert . /app

# Switch to non-root user
USER docexpert

# Use security scanning
# RUN trivy filesystem --exit-code 1 .
```

### 2. Network Security

#### Firewall Rules
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 3. Secret Management

#### Kubernetes Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: docexpert-secrets
type: Opaque
data:
  telegram-token: <base64-encoded-token>
  xai-key: <base64-encoded-key>
  mongodb-uri: <base64-encoded-uri>
```

#### HashiCorp Vault
```bash
# Store secrets in Vault
vault kv put secret/docexpert \
  telegram_token="your-token" \
  xai_key="your-key" \
  mongodb_uri="your-uri"
```

## Backup and Recovery

### 1. Database Backup

#### MongoDB Atlas Backup
```bash
# Create manual backup
mongodump --uri="$MONGODB_URI" --out=./backup/$(date +%Y%m%d)

# Restore from backup
mongorestore --uri="$MONGODB_URI" ./backup/20231201
```

### 2. Application Backup

#### Configuration Backup
```bash
#!/bin/bash
# backup.sh

# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup configuration
cp .env backups/$(date +%Y%m%d)/
cp docker-compose.yml backups/$(date +%Y%m%d)/

# Backup logs
tar -czf backups/$(date +%Y%m%d)/logs.tar.gz logs/

# Upload to cloud storage
aws s3 cp backups/$(date +%Y%m%d)/ s3://your-backup-bucket/ --recursive
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   ```bash
   # Test connection
   python test_mongodb_atlas.py
   
   # Check IP whitelist
   # Verify credentials
   # Check network connectivity
   ```

2. **API Rate Limits**
   ```python
   # Implement rate limiting
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Increase memory limits
   # Optimize embedding caching
   ```

### Monitoring Commands

```bash
# Check service health
curl http://localhost:8000/health

# View logs
docker-compose logs -f telegram-bot

# Monitor resources
docker stats

# Database connection test
python test_mongodb_atlas.py
```

## Performance Optimization

### 1. Caching Strategy
```python
from functools import lru_cache
import redis

# In-memory caching
@lru_cache(maxsize=1000)
def get_embedding(text: str):
    return embedding_service.encode(text)

# Redis caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(key: str, value: Any, ttl: int = 3600):
    redis_client.setex(key, ttl, json.dumps(value))
```

### 2. Database Optimization
```javascript
// Create indexes for better performance
db.documents.createIndex({ "user_id": 1, "created_at": -1 })
db.documents.createIndex({ "embedding": "2dsphere" })
db.messages.createIndex({ "user_id": 1, "timestamp": -1 })
```

### 3. Connection Pooling
```python
# MongoDB connection pooling
client = MongoClient(
    MONGODB_URI,
    maxPoolSize=20,
    minPoolSize=5,
    maxIdleTimeMS=30000
)
```

This deployment guide provides comprehensive instructions for deploying DocExpert in various environments while maintaining security, scalability, and performance best practices.
