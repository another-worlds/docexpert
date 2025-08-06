# DocExpert - Telegram Multi-Agent AI Bot

**DocExpert** is a powerful, AI-driven Telegram bot designed to intelligently process documents, retrieve YouTube transcripts, and provide context-aware responses. Leveraging **xAI Grok**, **HuggingFace embeddings**, and **MongoDB Atlas**, this bot offers advanced document analysis, YouTube content processing, and conversational AI capabilities.

---

## 🚀 Features

- **💬 Telegram Bot Integration** – Seamlessly interacts with users on Telegram
- **🧠 AI-Powered Responses** – Uses **xAI Grok** and **LangChain** for intelligent conversations
- **📄 Document Processing** – Supports PDF, TXT, DOCX, and other document formats
- **🎥 YouTube Transcript Analysis** – Automatically retrieves and processes YouTube video transcripts
- **🔍 Vector Search** – Advanced semantic search using **HuggingFace embeddings**
- **�️ MongoDB Atlas Integration** – Cloud-based document storage and retrieval
- **🎯 Multi-Agent Architecture** – Specialized agents for different tasks
- **� Docker Support** – Containerized deployment with Docker Compose
- **📊 Comprehensive Logging** – Advanced logging system with performance monitoring
- **⚡ FastAPI Backend** – Modern, scalable REST API

---

## 🛠 Quick Start

### Prerequisites
- **Docker** and **Docker Compose**
- **MongoDB Atlas** account (free tier available)
- **Telegram Bot Token** (from [@BotFather](https://t.me/botfather))
- **xAI API Key** (from [xAI Console](https://console.x.ai/))
- **HuggingFace API Key** (from [HuggingFace](https://huggingface.co/settings/tokens))

### 1. Clone and Setup
```bash
git clone <repository-url>
cd docexpert
./setup.sh  # Creates directories and .env template
```

### 2. Configure Environment
Edit the `.env` file with your API keys:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# AI API Keys
XAI_API_KEY=your_xai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
MONGODB_DB_NAME=telegram_bot

# Service Configuration
EMBEDDING_SERVICE=huggingface
LOG_LEVEL=INFO
```

### 3. Start the Bot
```bash
# Using Docker Compose (recommended)
make run

# Or for development
make dev

# Or for production
make prod
```

### 4. Test Connection
```bash
# Test MongoDB Atlas connection
python test_mongodb_atlas.py

# Test YouTube tool
python test_youtube_tool_fixed.py
```

---

## ▶️ Usage

### Bot Commands
- `/start` - Initialize the bot and get welcome message
- `/help` - Show available commands and features
- Send documents (PDF, TXT, DOCX) for analysis
- Send YouTube URLs for transcript processing
- Ask questions about uploaded documents or YouTube content

### Supported Features

#### 📄 Document Processing
- **PDF Files** - Extracts text and creates searchable embeddings
- **Text Files** - Processes plain text documents
- **Word Documents** - Handles DOCX format files
- **Automatic Analysis** - Semantic chunking and vector indexing

#### 🎥 YouTube Integration
- **Transcript Retrieval** - Automatically downloads video transcripts
- **Content Analysis** - Processes transcript content for Q&A
- **Multi-language Support** - Handles various transcript languages
- **Search Integration** - Find relevant content across videos

#### 🔍 Smart Search
- **Semantic Search** - Find documents by meaning, not just keywords
- **Context-Aware** - Maintains conversation context
- **Multi-source** - Search across documents and YouTube content
- **Relevance Ranking** - Returns most relevant results first

---

## 🎨 System Architecture

### Core Components

1. **Telegram Bot Interface**
   - Receives messages and files from users
   - Handles command processing and responses
   - Manages user sessions and context

2. **Multi-Agent AI System**
   - **Document Agent** - Processes and analyzes uploaded files
   - **YouTube Agent** - Retrieves and processes video transcripts
   - **Search Agent** - Performs semantic search across all content
   - **Chat Agent** - Handles conversational interactions

3. **Embedding Service**
   - **HuggingFace Integration** - Uses sentence-transformers for embeddings
   - **Vector Storage** - Stores embeddings in MongoDB Atlas
   - **Similarity Search** - Finds relevant content using cosine similarity

4. **Database Layer**
   - **MongoDB Atlas** - Cloud database for document storage
   - **Collections**: documents, messages, youtube_transcripts
   - **Indexes** - Optimized for vector and text search

### Data Flow

```
User Message → Telegram Bot → Message Handler → AI Agent → Database Query → Response Generation → User
```

1. **Message Reception** - Bot receives user input via Telegram API
2. **Content Analysis** - Determines message type (document, YouTube URL, query)
3. **Agent Selection** - Routes to appropriate specialized agent
4. **Context Retrieval** - Searches relevant documents/transcripts
5. **AI Processing** - Generates response using xAI Grok
6. **Response Delivery** - Sends formatted response to user

---

## � Available Commands

### Development Commands
| Command | Description |
|---------|-------------|
| `make setup` | Complete environment setup (directories, .env template) |
| `make dev` | Start development environment with hot reload |
| `make prod` | Start production environment with optimizations |
| `make build` | Build Docker images |
| `make logs` | View application logs |
| `make health` | Check service health status |

### Database Commands
| Command | Description |
|---------|-------------|
| `make db-shell` | Connect to MongoDB Atlas via mongosh |
| `make db-backup` | Create database backup |

### Testing Commands
| Command | Description |
|---------|-------------|
| `test_mongodb_atlas.py` | Test MongoDB Atlas connectivity |
| `test_youtube_tool_fixed.py` | Test YouTube transcript functionality |
| `test_embedding_service.py` | Test HuggingFace embedding service |

### Utility Commands
| Command | Description |
|---------|-------------|
| `make clean` | Clean Python cache files |
| `make setup-env` | Create .env template only |
| `make security-scan` | Run security scan on Docker images |

## 🔧 Configuration

### Environment Variables

#### Required Variables
```env
TELEGRAM_BOT_TOKEN=     # Get from @BotFather
XAI_API_KEY=           # Get from xAI Console
HUGGINGFACE_API_KEY=   # Get from HuggingFace
MONGODB_URI=           # MongoDB Atlas connection string
```

#### Optional Variables
```env
MONGODB_DB_NAME=telegram_bot    # Database name (default: telegram_bot)
EMBEDDING_SERVICE=huggingface   # Embedding service (default: huggingface)
LOG_LEVEL=INFO                  # Logging level (DEBUG, INFO, WARNING, ERROR)
YOUTUBE_API_KEY=               # Optional: For enhanced YouTube features
```

### MongoDB Atlas Setup
1. Create account at [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a free cluster
3. Add your IP to Network Access whitelist
4. Create database user with read/write permissions
5. Get connection string and add to `MONGODB_URI`

### Docker Configuration
The bot supports multiple deployment modes:
- **Development**: `docker-compose.dev.yml` - Hot reload, debug logging
- **Production**: `docker-compose.production.yml` - Optimized, with Nginx
- **Standard**: `docker-compose.yml` - Basic deployment

## 🚀 Advanced Features

### YouTube Transcript Processing
- Automatic transcript download from YouTube URLs
- Multi-language transcript support
- Chunked processing for long videos
- Vector search across transcript content

### Document Analysis
- Smart text extraction from various formats
- Semantic chunking for optimal search
- Automatic embedding generation
- Context-aware retrieval

### AI Agents
- **Specialized Tools**: Each agent has specific capabilities
- **Context Management**: Maintains conversation history
- **Performance Optimization**: Cached embeddings and smart retrieval

## 🛡️ Security & Best Practices

### API Key Security
- Never commit API keys to version control
- Use environment variables for all sensitive data
- Rotate API keys regularly
- Monitor API usage and quotas

### Database Security
- Use MongoDB Atlas for managed security
- Enable authentication and authorization
- Restrict network access with IP whitelisting
- Regular backups and monitoring

### Docker Security
- Non-root user in containers
- Minimal base images
- Regular security scans
- Proper volume mounting

## 📊 Monitoring & Logs

### Log Files
- `logs/bot.log` - Main application logs
- `logs/database.log` - Database operations
- `logs/document_pipeline.log` - Document processing
- `logs/performance.log` - Performance metrics

### Health Monitoring
- Health check endpoint: `http://localhost:8000/health`
- MongoDB connection monitoring
- API availability checks
- Performance metrics tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup
```bash
git clone <your-fork>
cd docexpert
make setup
make dev
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the `/docs` folder for detailed guides
- **Community**: Join our discussions for help and tips

---

**Built with ❤️ using xAI Grok, HuggingFace, MongoDB Atlas, and Docker**


