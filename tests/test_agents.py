"""Tests for agent implementations."""
import pytest
from app.schemas import TaskSpec, AgentResult
from app.agents import run_agent

def test_researcher_agent():
    """Test researcher agent returns non-empty content."""
    task = TaskSpec(
        user_query="Extract facts from this text",
        source_url="https://example.com"
    )
    context = {
        "source_text": "This is a test document with some facts. Fact 1: AI is transforming industries. Fact 2: Machine learning enables automation."
    }
    
    result = run_agent("researcher", task, context)
    
    assert isinstance(result, AgentResult)
    assert result.role == "researcher"
    assert len(result.content) > 0

def test_researcher_agent_no_source():
    """Test researcher handles missing source gracefully."""
    task = TaskSpec(user_query="Extract facts")
    context = {"source_text": ""}
    
    result = run_agent("researcher", task, context)
    
    assert isinstance(result, AgentResult)
    assert result.role == "researcher"
    assert len(result.warnings) > 0 or len(result.content) > 0

def test_summarizer_agent():
    """Test summarizer agent returns non-empty content."""
    task = TaskSpec(
        user_query="Summarize this",
        desired_style="concise",
        desired_length="short"
    )
    context = {
        "researcher_output": "Fact 1: AI is important. Fact 2: ML is useful. Fact 3: Automation helps.",
        "source_text": "Some source text here."
    }
    
    result = run_agent("summarizer", task, context)
    
    assert isinstance(result, AgentResult)
    assert result.role == "summarizer"
    assert len(result.content) > 0

def test_writer_agent():
    """Test writer agent returns non-empty content."""
    task = TaskSpec(
        user_query="Write a LinkedIn post",
        desired_style="friendly",
        desired_length="short"
    )
    context = {
        "summarizer_output": "AI is transforming industries through automation.",
        "researcher_output": "Some facts about AI."
    }
    
    result = run_agent("writer", task, context)
    
    assert isinstance(result, AgentResult)
    assert result.role == "writer"
    assert len(result.content) > 0

def test_coder_agent():
    """Test coder agent returns non-empty content."""
    task = TaskSpec(user_query="Write Python code to reverse a string")
    context = {}
    
    result = run_agent("coder", task, context)
    
    assert isinstance(result, AgentResult)
    assert result.role == "coder"
    assert len(result.content) > 0

def test_analyst_agent():
    """Test analyst agent returns non-empty content."""
    task = TaskSpec(user_query="Analyze this data")
    context = {
        "source_text": "Sales: Q1=100, Q2=150, Q3=200, Q4=250. Growth rate: 25% per quarter."
    }
    
    result = run_agent("analyst", task, context)
    
    assert isinstance(result, AgentResult)
    assert result.role == "analyst"
    assert len(result.content) > 0

def test_unknown_agent():
    """Test that unknown agent role returns error result."""
    task = TaskSpec(user_query="Test")
    context = {}
    
    result = run_agent("unknown_role", task, context)
    
    assert isinstance(result, AgentResult)
    assert len(result.warnings) > 0

