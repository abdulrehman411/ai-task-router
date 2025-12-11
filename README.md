# AI Task Router

**Version 1.0.0** | Production Ready

A production-ready multi-agent task routing system that intelligently dispatches user requests to specialized AI agents (Researcher, Summarizer, Writer, Coder, Analyst) using LangGraph orchestration.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

## 🚀 Features

- **Intelligent Routing**: Heuristic-based + LLM-powered routing decisions
- **5 Specialist Agents**: Researcher, Summarizer, Writer, Coder, Analyst
- **LangGraph Orchestration**: Robust workflow management with state tracking
- **FastAPI Backend**: RESTful API with Pydantic validation
- **Professional Streamlit UI**: Modern, production-ready web interface
- **Task History & Analytics**: Track and analyze task execution patterns
- **Export & Share**: Download results as TXT or JSON
- **URL/PDF Support**: Automatic content extraction from URLs and PDFs
- **Trace & Transparency**: Full routing trace with agent outputs
- **Production Ready**: Dockerized, tested, and deployable

## 📋 Architecture

```
[Streamlit UI] 
    ↓
[User Request] 
    ↓
[FastAPI /generate]
    ↓
[LangGraph Router]
    ↓
[Specialist Agents] → [Merger/QA] → [Formatter]
    ↓
[JSON Response] → [Streamlit UI Display]
```

## 🛠️ Tech Stack

- **Python 3.11+**
- **LangChain + LangGraph**: Agent orchestration
- **FastAPI**: REST API framework
- **Pydantic v2**: Data validation
- **OpenAI GPT-4o-mini**: LLM backend
- **Docker**: Containerization

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- OpenAI API key

### Local Setup

1. **Clone the repository**
   ```bash
   cd AI-Task-Router
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run the API server**
   ```bash
   python3 run.py
   ```

   The API will be available at `http://localhost:8000`

6. **Run the Streamlit UI** (in a new terminal)
   ```bash
   python3 run_ui.py
   ```
   
   Or directly:
   ```bash
   streamlit run ui/app.py
   ```
   
   The UI will be available at `http://localhost:8501`

7. **Test the API**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Generate example
   curl -X POST http://localhost:8000/generate \
     -H "Content-Type: application/json" \
     -d '{
       "user_query": "Summarize the benefits of AI in one sentence",
       "desired_style": "concise",
       "desired_length": "short"
     }'
   ```

## 🐳 Docker Deployment

### Build and Run Locally

```bash
# Build the image
docker build -t ai-task-router .

# Run the container
docker run -p 8000:8000 --env-file .env ai-task-router
```

### Deploy to Cloud

#### Render

1. Create a new Web Service
2. Connect your repository
3. Set build command: `docker build -t ai-task-router .`
4. Set start command: (uses Dockerfile CMD)
5. Add environment variable: `OPENAI_API_KEY=your_key`

#### Railway

1. Create new project from GitHub
2. Add environment variable: `OPENAI_API_KEY`
3. Railway will auto-detect Dockerfile

#### Fly.io

```bash
fly launch
fly secrets set OPENAI_API_KEY=your_key
fly deploy
```

## 📖 API Documentation

### Endpoints

#### `GET /`
Root endpoint with API information.

#### `GET /health`
Health check endpoint.

#### `POST /generate`
Main endpoint for task generation.

**Request Body:**
```json
{
  "user_query": "Summarize this PDF and draft a 150-word LinkedIn post",
  "source_url": "https://example.com/document.pdf",
  "desired_style": "friendly",
  "desired_length": "short"
}
```

**Response:**
```json
{
  "route": {
    "selected_agents": ["researcher", "summarizer", "writer"],
    "rationale": "URL present requires researcher, summary requested, and writing task",
    "confidence": 0.85
  },
  "steps": [
    {
      "role": "researcher",
      "content": "Fact sheet with citations...",
      "citations": ["https://example.com/document.pdf"],
      "warnings": []
    },
    {
      "role": "summarizer",
      "content": "Summary of key points...",
      "citations": [],
      "warnings": []
    },
    {
      "role": "writer",
      "content": "Polished LinkedIn post...",
      "citations": [],
      "warnings": []
    }
  ],
  "final_output": "Final merged output...",
  "tokens_used": null
}
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies (included in requirements.txt)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_router.py
```

## 📁 Project Structure

```
ai-task-router/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── schemas.py         # Pydantic models
│   ├── prompts.py         # Prompt templates
│   ├── tools.py           # URL/PDF fetching utilities
│   ├── agents.py          # Agent implementations
│   ├── graph.py           # LangGraph workflow
│   └── api.py             # FastAPI application
├── tests/
│   ├── test_router.py     # Router tests
│   ├── test_agents.py     # Agent tests
│   ├── test_api.py        # API tests
│   └── test_tools.py      # Utility tests
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env.example          # Environment template
└── README.md             # This file
```

## 🎯 Usage Examples

### Example 1: Simple Summary

```python
import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "user_query": "Summarize the benefits of AI",
        "desired_style": "concise",
        "desired_length": "short"
    }
)

result = response.json()
print(result["final_output"])
```

### Example 2: URL Research + Writing

```python
response = requests.post(
    "http://localhost:8000/generate",
    json={
        "user_query": "Read this article and write a LinkedIn post",
        "source_url": "https://example.com/article",
        "desired_style": "friendly",
        "desired_length": "short"
    }
)

result = response.json()
print(f"Route: {result['route']['selected_agents']}")
print(f"Output: {result['final_output']}")
```

### Example 3: Code Generation

```python
response = requests.post(
    "http://localhost:8000/generate",
    json={
        "user_query": "Write Python code to reverse a string",
        "desired_style": "technical"
    }
)

result = response.json()
print(result["final_output"])
```

## 🔧 Configuration

Environment variables (in `.env`):

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MODEL_NAME`: Model to use (default: `gpt-4o-mini`)
- `TEMPERATURE`: LLM temperature (default: `0.0`)
- `MAX_TOKENS`: Max tokens per request (default: `2000`)
- `PORT`: API server port (default: `8000`)

## 🚦 Routing Logic

The router uses a two-stage approach:

1. **Heuristics**: Fast rule-based selection
   - URL present → Researcher
   - "summarize" keywords → Summarizer
   - "write/draft/post" → Writer
   - "code/python/regex" → Coder
   - "csv/table/metrics" → Analyst

2. **LLM Refinement**: Adjusts order and confidence

## 🛡️ Guardrails

- **Output Length Limits**: Max 3k characters for final output
- **Source Text Limits**: Max 50k characters for fetched content
- **Citation Validation**: Researcher-only citations, no hallucinated sources
- **Error Handling**: Graceful fallbacks at each stage

## 📊 Performance

- Typical request latency: **5-10 seconds** (with gpt-4o-mini)
- Supports concurrent requests (FastAPI async)
- Efficient state management with LangGraph

## 🎨 Streamlit UI Features

The production-ready Streamlit UI provides a comprehensive interface:

### Core Features
- **Task Input Form**: Query input, optional URL, style/length selection
- **Professional Route Visualization**: Text-based agent labels with confidence scores
- **Final Output Display**: Prominent display with copy and download options
- **Agent Outputs**: Expandable panels for each agent's contribution
- **Execution Trace**: JSON viewer and download for full trace

### Advanced Features
- **Task History**: Automatic saving of recent tasks with quick reload
- **Analytics Dashboard**: Usage statistics, agent distribution, and insights
- **Export Capabilities**: Download results as TXT or JSON
- **Connection Testing**: Built-in API health check
- **Multi-Tab Interface**: Organized workflow with Input, Results, and Analytics tabs
- **Example Queries**: Pre-filled examples to get started quickly
- **Progress Indicators**: Real-time processing feedback

## 🔮 Future Enhancements

- [ ] LangSmith tracing integration
- [ ] Vector store for multi-page sources
- [ ] Critic agent for quality scoring
- [ ] Few-shot classifier for routing
- [ ] Token usage tracking


## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ using LangChain, LangGraph, and FastAPI**

