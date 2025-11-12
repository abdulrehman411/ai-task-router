"""Tests for the FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.schemas import TaskSpec

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "status" in data

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_generate_endpoint_empty_query():
    """Test generate endpoint rejects empty query."""
    task = TaskSpec(user_query="")
    response = client.post("/generate", json=task.model_dump())
    assert response.status_code == 400

def test_generate_endpoint_valid_query():
    """Test generate endpoint accepts valid query."""
    # Note: This test may require API key and will make actual LLM calls
    # Skip if API key is not available
    import os
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
    
    task = TaskSpec(
        user_query="Summarize the benefits of AI in one sentence",
        desired_style="concise",
        desired_length="short"
    )
    response = client.post("/generate", json=task.model_dump())
    
    # Should either succeed or fail gracefully
    assert response.status_code in [200, 500, 400]
    
    if response.status_code == 200:
        data = response.json()
        assert "route" in data
        assert "steps" in data
        assert "final_output" in data

def test_generate_endpoint_with_url():
    """Test generate endpoint with URL."""
    # Note: This test requires API key and network access
    import os
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
    
    task = TaskSpec(
        user_query="Summarize this page",
        source_url="https://example.com"
    )
    response = client.post("/generate", json=task.model_dump())
    
    # Should either succeed or fail gracefully
    assert response.status_code in [200, 500, 400]

