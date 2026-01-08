# ContentForge: Intelligent Enterprise Content Engine

<div align="center">

**Production-Ready AI Platform for Enterprise Content Generation**

[![CI/CD](https://github.com/your-org/contentforge/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/your-org/contentforge/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)

</div>

---

## 🎯 Overview

**ContentForge** is a production-ready SaaS platform that generates structured business content using multi-agent AI orchestration, RAG (Retrieval-Augmented Generation), and enterprise integrations.

### What Makes ContentForge Different?

- **🤖 Multi-Agent Architecture**: Specialized AI agents (Planning, Research, Drafting, Editing) work together for high-quality content
- **📚 RAG-Powered**: Grounds all content in your enterprise documents using Azure AI Search
- **✅ Responsible AI**: Automatic citation tracking, anti-hallucination safeguards, and transparent source attribution
- **🔗 Enterprise Integration**: Publishes directly to SharePoint and Microsoft Teams
- **⚡ Production-Ready**: Clean architecture, comprehensive logging, error handling, and testing

---

## ✨ Features

### Content Generation
- **Multiple Content Types**: Reports, summaries, articles, marketing copy, emails, presentations
- **Intelligent Planning**: Automatic task decomposition and section structuring
- **RAG Integration**: Retrieves and cites relevant enterprise documents
- **Citation Management**: APA, MLA, Chicago, IEEE formats
- **Quality Assurance**: Multi-stage editing and fact-checking

### Enterprise Integration
- **SharePoint Publishing**: Direct upload to document libraries
- **Teams Integration**: Post content to channels
- **Microsoft Graph API**: Full Microsoft 365 integration
- **Azure Services**: OpenAI, AI Search, App Service ready

---

## 🏗️ Architecture

### Multi-Agent Workflow

```
User Prompt → Planning Agent → Research Agent (RAG) → Drafting Agent → Editing Agent → Final Content
```

### Tech Stack

**Backend:**
- Python 3.11 + FastAPI
- Azure OpenAI (GPT-4o)
- Azure AI Search (RAG)
- Microsoft Graph API
- Pydantic for validation
- pytest for testing

**Frontend:**
- React + TypeScript
- Modern component architecture
- Responsive SaaS UI

### Project Structure

```
backend/app/
├── main.py                 # FastAPI application
├── core/                   # Configuration & logging
├── models/                 # Domain models
├── integrations/           # Azure services
├── services/               # Business logic
├── agents/                 # AI agents
├── api/                    # API routes
└── tests/                  # Test suite

frontend/
├── src/
│   ├── components/         # React components
│   ├── pages/              # Application pages
│   └── lib/                # Utilities
└── public/
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Azure Account** with:
  - Azure OpenAI Service
  - Azure AI Search
  - Microsoft Entra (Azure AD) App Registration

### 1. Backend Setup

```bash
cd backend/app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your Azure credentials

# Run tests
pytest

# Start development server
uvicorn main:app --reload
```

Backend available at: **http://localhost:8000**
- API Docs: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend available at: **http://localhost:5173**

---

## ⚙️ Configuration

### Environment Variables

Edit `backend/.env` with your Azure credentials:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Azure AI Search
AI_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AI_SEARCH_API_KEY=your-admin-key
AI_SEARCH_INDEX_NAME=contentforge-documents

# Microsoft Graph
GRAPH_TENANT_ID=your-tenant-id
GRAPH_CLIENT_ID=your-client-id
GRAPH_CLIENT_SECRET=your-client-secret
```

---

## 📖 API Usage

### Generate Content

```bash
POST /api/v1/content/generate
```

```json
{
  "prompt": "Create a comprehensive report on AI ethics in healthcare",
  "content_type": "report",
  "citation_format": "APA",
  "max_words": 3000,
  "include_citations": true,
  "tags": ["AI", "healthcare", "ethics"]
}
```

### Publish to SharePoint

```bash
POST /api/v1/publish/sharepoint
```

```json
{
  "file_name": "AI_Ethics_Report.docx",
  "content": "Report content...",
  "folder_path": "Reports/2024"
}
```

Full API documentation: **http://localhost:8000/docs**

---

## 🧪 Testing

### Backend Tests

```bash
cd backend/app

# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific tests
pytest tests/test_models_unit.py
```

### Frontend Tests

```bash
cd frontend

npm test
npm test -- --coverage
```

---

## 🚢 Deployment

### Azure App Service

```bash
# Build and deploy
docker build -t contentforge:latest -f backend/Dockerfile .
az acr build --registry your-registry --image contentforge:latest .
az webapp create --resource-group your-rg --name contentforge \
  --deployment-container-image-name your-registry.azurecr.io/contentforge:latest
```

---

## 📚 Documentation

### Key Components

#### Multi-Agent System

1. **Planning Agent**: Decomposes prompts into structured plans
2. **Research Agent**: Retrieves relevant documents using RAG
3. **Drafting Agent**: Generates content sections
4. **Editing Agent**: Refines and fact-checks output

#### Responsible AI Features

- **Automatic Citations**: All claims are sourced
- **Anti-Hallucination**: Content grounded in enterprise docs
- **Transparency**: Full execution history available
- **Source Verification**: Fact-checking against citations

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and test (`pytest` and `npm test`)
4. Commit (`git commit -m 'Add amazing feature'`)
5. Push (`git push origin feature/amazing-feature`)
6. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - LLM
- [Azure AI Search](https://azure.microsoft.com/en-us/products/ai-services/ai-search) - RAG
- [Microsoft Graph](https://developer.microsoft.com/en-us/graph) - Microsoft 365 integration
- [React](https://react.dev/) - Frontend framework

---

<div align="center">

**Built for Enterprise Content Teams**

</div>
