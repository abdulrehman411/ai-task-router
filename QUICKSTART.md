# Quick Start Guide

Get the AI Task Router running in 5 minutes!

## Prerequisites

- Python 3.11 or higher (check with `python3 --version`)
  - Note: macOS may have Python 3.9 by default. Install Python 3.11+ via Homebrew: `brew install python@3.11`
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

## Setup Steps

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0.0
```

### 3. Start the Server

```bash
python3 run.py
```

Or using uvicorn directly:

```bash
uvicorn app.api:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the API

#### Using curl:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Summarize the benefits of AI in one sentence",
    "desired_style": "concise",
    "desired_length": "short"
  }'
```

#### Using the example script:

```bash
python3 example_request.py summary
```

#### Using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "user_query": "Write a brief summary of machine learning",
        "desired_style": "friendly",
        "desired_length": "short"
    }
)

print(response.json()["final_output"])
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `POST /generate` - Main endpoint for task generation

## Example Use Cases

### 1. Simple Summary
```json
{
  "user_query": "Summarize quantum computing",
  "desired_style": "concise",
  "desired_length": "short"
}
```

### 2. URL Research + Writing
```json
{
  "user_query": "Read this page and write a LinkedIn post",
  "source_url": "https://example.com/article",
  "desired_style": "friendly",
  "desired_length": "short"
}
```

### 3. Code Generation
```json
{
  "user_query": "Write Python code to sort a list",
  "desired_style": "technical"
}
```

### 4. Data Analysis
```json
{
  "user_query": "Analyze this CSV data and provide insights",
  "source_url": "https://example.com/data.csv"
}
```

## Troubleshooting

### "OPENAI_API_KEY must be set"
- Make sure you created a `.env` file
- Check that the API key is correct
- Restart the server after adding the key

### Import errors
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

### Port already in use
- Change the port in `.env`: `PORT=8001`
- Or kill the process using port 8000

## Next Steps

- Check the full [README.md](README.md) for detailed documentation
- Explore the API docs at `http://localhost:8000/docs`
- Run tests: `pytest`
- Deploy with Docker: `docker build -t ai-task-router .`

Happy routing! 🚀

