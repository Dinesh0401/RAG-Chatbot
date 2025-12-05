# RAG Chatbot with LangChain

A production-ready Retrieval-Augmented Generation (RAG) chatbot built with FastAPI, Streamlit, and LangChain. Upload PDFs and ask questions - the chatbot retrieves relevant context and generates answers using OpenAI.

## 🚀 Live Deployment

### **Try it Online NOW**
- **🎯 Streamlit UI (Interactive):** https://rag-spark-chatbot.streamlit.app/
- **📚 API Documentation:** Coming soon on Render

---

## ✨ Features

- ✅ **PDF Ingestion** - Upload and process multiple PDFs simultaneously
- ✅ **RAG Pipeline** - Retrieve relevant context before generating answers
- ✅ **LangChain Integration** - Powered by LangChain + OpenAI GPT
- ✅ **ChromaDB Storage** - Efficient vector database for document embeddings
- ✅ **FastAPI Backend** - Production-ready REST API with auto-docs
- ✅ **Streamlit UI** - User-friendly, responsive web interface
- ✅ **Worldwide Deployment** - Available globally with HTTPS encryption
- ✅ **Docker Support** - Easy containerization and scaling
- ✅ **Logging** - Comprehensive error tracking and debugging

---

## 📋 Prerequisites

- **Python 3.11+**
- **OpenAI API Key** - Get it from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Git** - For cloning the repository
- **Docker** (optional) - For containerized deployment

---

## 🛠️ Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Dinesh0401/RAG-Chatbot.git
cd RAG-Chatbot
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\Activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy template and add your OpenAI API Key
cp .env.template .env

# Edit .env file:
OPENAI_API_KEY=sk-your-actual-key-here
```

### 5. Initialize Database (Optional - for local RAG)
```bash
python ingest_database.py
```

### 6. Run Locally

**Terminal 1 - Start FastAPI Backend:**
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
✅ API running at: http://localhost:8000
✅ API docs at: http://localhost:8000/docs

**Terminal 2 - Start Streamlit UI:**
```bash
streamlit run streamlit_ui.py
```
✅ UI running at: http://localhost:8501

---

## 🐳 Docker Setup

### Build Docker Image
```bash
docker build -t rag-chatbot .
```

### Run Container Locally
```bash
docker run -p 8000:8000 \
  --env-file .env \
  -v ${PWD}/chroma_db:/app/chroma_db \
  rag-chatbot
```

### Run on Docker Hub
```bash
# Build and tag
docker build -t yourusername/rag-chatbot .

# Login and push
docker login
docker push yourusername/rag-chatbot

# Anyone can run it
docker run -p 8000:8000 yourusername/rag-chatbot
```

---

## 📡 API Endpoints

### Main Chat Endpoint
**POST** `/chat`

Upload PDFs and ask questions:
```bash
curl -X POST http://localhost:8000/chat \
  -F "question=What is in the documents?" \
  -F "files=@document.pdf" \
  -F "k=5"
```

**Parameters:**
- `question` (required) - Your question
- `files` (optional) - PDF files to upload
- `k` (optional) - Number of sources to retrieve (default: 5)

**Response Example:**
```json
{
  "answer": "Based on the documents, the RAG chatbot is a system that combines retrieval and generation...",
  "sources": [
    {
      "source": "document.pdf",
      "page": 1
    },
    {
      "source": "document.pdf",
      "page": 3
    }
  ]
}
```

### API Documentation
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🌍 Deployment Options

### Option 1: Streamlit Cloud (Easiest - UI Only)
1. Make your repo **public** on GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New app" → Select your repository
4. Main file path: `streamlit_ui.py`
5. Click Deploy

**Live URL:** https://rag-spark-chatbot.streamlit.app/

### Option 2: Render.com (Full Stack - Recommended)
1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click "New +" → "Blueprint"
4. Select your repository
5. Auto-detects `render.yaml` configuration
6. Click Deploy

**Gets you:**
- 🔗 API endpoint URL
- 🎨 UI endpoint URL
- 🔒 Free SSL/HTTPS
- 🌐 Worldwide CDN
- 💰 Free tier available

### Option 3: Railway.app
1. Go to [railway.app](https://railway.app)
2. Connect GitHub
3. Select repository
4. Railway auto-detects configuration
5. Deploy with one click
6. $5/month per service

### Option 4: Fly.io
1. Sign up at [fly.io](https://fly.io)
2. Install Fly CLI
3. Run: `flyctl launch`
4. Follow prompts to deploy
5. Pay only for what you use

### Option 5: AWS/Google Cloud/Azure
- More complex but highly scalable
- Best for enterprise deployments
- Requires more configuration

---

## 📁 Project Structure

```
RAG-Chatbot/
│
├── 📄 app.py                  # FastAPI application main file
├── 🎨 streamlit_ui.py         # Streamlit web interface
├── 🤖 rag_service.py          # RAG pipeline & LangChain logic
├── 📥 ingest_database.py      # PDF ingestion & embedding
│
├── 📋 requirements.txt        # Python dependencies
├── 🐳 Dockerfile              # Docker configuration
├── 📦 render.yaml             # Render deployment config
│
├── 📁 utils/
│   └── logging_config.py      # Centralized logging setup
│
├── 📁 chroma_db/              # Vector database storage
│   ├── chroma.sqlite3         # ChromaDB storage
│   └── [embedding vectors]    # Embedded documents
│
├── 📁 data/                   # Sample documents
│
├── .env.template              # Environment variables template
├── .gitignore                 # Git ignore rules
└── readme.md                  # This file
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Database Configuration
CHROMA_DB_PATH=./chroma_db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
```

### Render Environment Variables
Set these in Render dashboard:
- `OPENAI_API_KEY=sk-...`
- `API_URL=https://your-api-url.onrender.com`

---

## 🧪 Testing

### Test API with cURL

**Test with Documents:**
```bash
curl -X POST http://localhost:8000/chat \
  -F "question=What is the main topic?" \
  -F "files=@sample.pdf"
```

**Test API Docs:**
```bash
# Open in browser
http://localhost:8000/docs
```

### Test Streamlit UI
1. Open http://localhost:8501
2. Upload a PDF file
3. Type a question
4. Click "Ask"
5. View answer and sources

### Test Deployed App
1. Visit: https://rag-spark-chatbot.streamlit.app/
2. Upload test PDF
3. Ask a question
4. Verify response

---

## 📚 Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | High-performance REST API |
| **Frontend** | Streamlit | Interactive web UI |
| **LLM** | OpenAI GPT-3.5/4 | Question answering |
| **RAG** | LangChain | LLM orchestration |
| **Vector DB** | ChromaDB | Document embeddings storage |
| **Server** | Uvicorn | ASGI application server |
| **Containerization** | Docker | Easy deployment |
| **Hosting** | Render, Streamlit | Worldwide deployment |

---

## 🚨 Troubleshooting

### Issue: "OpenAI API Key not found"
```bash
# Solution: Create .env file with your key
echo "OPENAI_API_KEY=sk-your-key" > .env
```

### Issue: "ChromaDB connection error"
```bash
# Solution: Reinitialize database
rm -rf chroma_db/
python ingest_database.py
```

### Issue: "Port 8000 already in use"
```bash
# Solution: Use different port
python -m uvicorn app:app --port 8001
```

### Issue: Streamlit not finding API
```bash
# Ensure both services are running and API_URL is correct in streamlit_ui.py
# For deployment, set environment variable API_URL
```

---

## 📈 Performance Tips

- Use `k=3` for faster retrieval (fewer sources)
- Cache ChromaDB for repeated queries
- Use GPT-3.5-turbo for faster responses
- Enable streaming for large documents
- Deploy with multiple replicas for high traffic

---

## 🔐 Security Best Practices

- ✅ Never commit `.env` file to git
- ✅ Use environment variables for API keys
- ✅ Validate user inputs
- ✅ Use HTTPS for all connections
- ✅ Set rate limits on API endpoints
- ✅ Implement authentication for production
- ✅ Keep dependencies updated

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Author

**Dinesh0401** - [GitHub Profile](https://github.com/Dinesh0401)

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support & Contact

- 🐛 **Bug Reports:** [Open an Issue](https://github.com/Dinesh0401/RAG-Chatbot/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/Dinesh0401/RAG-Chatbot/discussions)
- 📧 **Email:** your-email@example.com
- 🎥 **YouTube:** [Tutorial Link](https://www.youtube.com/watch?v=xf3gAFclwqo)

---

## 🙏 Acknowledgments

- OpenAI for GPT API
- LangChain for LLM orchestration
- Streamlit for UI framework
- Render for hosting
- ChromaDB for vector storage

---

## 📊 Stats

- ⭐ Stars: [View on GitHub](https://github.com/Dinesh0401/RAG-Chatbot)
- 🍴 Forks: [View on GitHub](https://github.com/Dinesh0401/RAG-Chatbot)
- 👁️ Watchers: [View on GitHub](https://github.com/Dinesh0401/RAG-Chatbot)

---

**Last Updated:** December 5, 2025

**Status:** ✅ Production Ready | 🌐 Globally Deployed | 🚀 Active Development
