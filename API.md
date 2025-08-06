# DocExpert API Documentation

## Overview

DocExpert provides a REST API built with FastAPI for health monitoring, webhook management, and service integration. The primary interface is through Telegram, but the API enables monitoring and integration capabilities.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

The API uses environment-based authentication for webhook endpoints. No authentication is required for public endpoints like health checks.

## Endpoints

### Health Check

#### GET `/health`

Returns the health status of the application and its dependencies.

**Response Format:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-06T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": {
      "status": "connected",
      "response_time_ms": 45,
      "details": "MongoDB Atlas connection active"
    },
    "embedding_service": {
      "status": "available",
      "service_type": "huggingface",
      "model": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "ai_service": {
      "status": "available",
      "provider": "xai",
      "model": "grok-beta"
    }
  },
  "system": {
    "memory_usage_mb": 256,
    "uptime_seconds": 3600,
    "active_connections": 5
  }
}
```

**Status Codes:**
- `200 OK`: All services healthy
- `503 Service Unavailable`: One or more critical services unavailable

**Example:**
```bash
curl -X GET http://localhost:8000/health
```

### Telegram Webhook

#### POST `/webhook`

Telegram webhook endpoint for receiving bot updates. This endpoint is automatically configured when the bot starts.

**Request Headers:**
```
Content-Type: application/json
X-Telegram-Bot-Api-Secret-Token: <webhook_secret>
```

**Request Body:**
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 12345678,
      "is_bot": false,
      "first_name": "John",
      "username": "john_doe"
    },
    "chat": {
      "id": 12345678,
      "first_name": "John",
      "username": "john_doe",
      "type": "private"
    },
    "date": 1691328000,
    "text": "Hello, bot!"
  }
}
```

**Response:**
```json
{
  "status": "ok",
  "processed": true
}
```

### Metrics (Future Enhancement)

#### GET `/metrics`

Prometheus-compatible metrics endpoint for monitoring.

**Response Format:**
```
# HELP docexpert_requests_total Total number of requests
# TYPE docexpert_requests_total counter
docexpert_requests_total{method="POST",endpoint="/webhook"} 1234

# HELP docexpert_request_duration_seconds Request duration
# TYPE docexpert_request_duration_seconds histogram
docexpert_request_duration_seconds_bucket{le="0.1"} 100
docexpert_request_duration_seconds_bucket{le="0.5"} 250
docexpert_request_duration_seconds_bucket{le="1.0"} 450
docexpert_request_duration_seconds_bucket{le="+Inf"} 500

# HELP docexpert_active_users_total Currently active users
# TYPE docexpert_active_users_total gauge
docexpert_active_users_total 25

# HELP docexpert_documents_processed_total Documents processed
# TYPE docexpert_documents_processed_total counter
docexpert_documents_processed_total{type="pdf"} 123
docexpert_documents_processed_total{type="txt"} 45
docexpert_documents_processed_total{type="docx"} 67
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request could not be processed",
    "details": "Additional error information",
    "timestamp": "2025-08-06T12:00:00Z",
    "request_id": "req_123456789"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request data |
| `UNAUTHORIZED` | 401 | Invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `SERVICE_UNAVAILABLE` | 503 | External service unavailable |
| `INTERNAL_ERROR` | 500 | Internal server error |

## Telegram Bot API Integration

### Supported Commands

#### `/start`
Initializes the bot and provides welcome message.

**Response:**
```
Welcome to DocExpert! 🤖

I can help you with:
📄 Document analysis (PDF, TXT, DOCX)
🎥 YouTube transcript processing
🔍 Semantic search across your content
💬 Intelligent Q&A

Send me a document or YouTube URL to get started!
```

#### `/help`
Shows available commands and features.

#### `/clear`
Clears conversation history for the user.

### Supported Content Types

#### Documents
- **PDF**: Full text extraction and analysis
- **TXT**: Plain text processing
- **DOCX**: Microsoft Word document processing

**Process Flow:**
1. User uploads document via Telegram
2. Bot downloads and processes file
3. Text is extracted and chunked
4. Embeddings are generated via HuggingFace
5. Content is stored in MongoDB Atlas
6. User receives confirmation with document summary

#### YouTube URLs
- **Supported formats**: 
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://m.youtube.com/watch?v=VIDEO_ID`

**Process Flow:**
1. User sends YouTube URL
2. Bot extracts video ID
3. Transcript is downloaded via youtube-transcript-api
4. Content is processed and embedded
5. Transcript is stored with video metadata
6. User can query transcript content

### Message Processing

#### Text Messages
- **Context-aware responses** using conversation history
- **Semantic search** across user's documents and YouTube content
- **Multi-turn conversations** with memory management

#### File Uploads
- **Automatic format detection**
- **Progress indicators** for large files
- **Error handling** for unsupported formats
- **Content summarization** after processing

## Integration Examples

### Health Check Monitoring

```python
import httpx
import asyncio

async def check_health():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        health_data = response.json()
        
        if health_data["status"] == "healthy":
            print("✅ Service is healthy")
        else:
            print("❌ Service has issues")
            for service, status in health_data["services"].items():
                print(f"  {service}: {status['status']}")

asyncio.run(check_health())
```

### Webhook Verification

```python
import hmac
import hashlib

def verify_telegram_webhook(token: str, request_body: bytes, signature: str) -> bool:
    """Verify Telegram webhook signature"""
    secret_key = hashlib.sha256(token.encode()).digest()
    expected_signature = hmac.new(
        secret_key, 
        request_body, 
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### Performance Monitoring

```python
import time
import httpx

async def monitor_performance():
    """Monitor API response times"""
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
    
    response_time = time.time() - start_time
    
    if response_time > 1.0:
        print(f"⚠️ Slow response: {response_time:.2f}s")
    else:
        print(f"✅ Good response time: {response_time:.2f}s")
```

## Rate Limiting

### Current Limits
- **Health endpoint**: 60 requests/minute per IP
- **Webhook endpoint**: No limit (Telegram controlled)
- **Future endpoints**: 1000 requests/hour per API key

### Rate Limit Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1691328000
```

### Rate Limit Response
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests",
    "retry_after": 60
  }
}
```

## Security

### Webhook Security
- **Secret token verification** for Telegram webhooks
- **IP allowlisting** for webhook endpoints
- **Request signature validation**

### API Security
- **CORS configuration** for cross-origin requests
- **Request size limits** to prevent abuse
- **Error message sanitization** to prevent information leakage

### Data Privacy
- **No persistent user data** beyond conversation context
- **Automatic cleanup** of processed files
- **Encrypted connections** (TLS) for all API calls

## Development

### Local Development Setup

1. **Start the development server:**
```bash
make dev
```

2. **API will be available at:**
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

3. **Test the API:**
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

### Testing

```python
import pytest
import httpx

@pytest.mark.asyncio
async def test_health_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
```

### API Documentation

The API includes interactive documentation available at:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## Future Enhancements

### Planned API Features
- **Document management endpoints** for CRUD operations
- **User analytics API** for usage metrics
- **Bulk processing endpoints** for multiple documents
- **Search API** for direct content queries
- **Webhook management** for third-party integrations

### Security Enhancements
- **API key authentication** for protected endpoints
- **OAuth2 integration** for user authentication
- **Role-based access control** for different user types
- **Audit logging** for all API interactions

This API documentation provides a comprehensive overview of DocExpert's current and planned API capabilities, enabling effective integration and monitoring of the service.
