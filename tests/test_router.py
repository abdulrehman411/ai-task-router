"""Tests for the router agent."""
import pytest
from app.schemas import TaskSpec
from app.agents import router, heuristic_route

def test_heuristic_route_with_url():
    """Test that URLs trigger researcher."""
    task = TaskSpec(
        user_query="Tell me about this page",
        source_url="https://example.com"
    )
    route = heuristic_route(task)
    assert "researcher" in route

def test_heuristic_route_summarize():
    """Test that summarize keywords trigger summarizer."""
    task = TaskSpec(user_query="Summarize this document")
    route = heuristic_route(task)
    assert "summarizer" in route

def test_heuristic_route_write():
    """Test that write keywords trigger writer."""
    task = TaskSpec(user_query="Write a LinkedIn post about AI")
    route = heuristic_route(task)
    assert "writer" in route

def test_heuristic_route_code():
    """Test that code keywords trigger coder."""
    task = TaskSpec(user_query="Write Python code to sort a list")
    route = heuristic_route(task)
    assert "coder" in route

def test_heuristic_route_analyst():
    """Test that analyst keywords trigger analyst."""
    task = TaskSpec(user_query="Analyze this CSV data")
    route = heuristic_route(task)
    assert "analyst" in route

def test_heuristic_route_default():
    """Test that unknown queries default to summarizer."""
    task = TaskSpec(user_query="What is the weather?")
    route = heuristic_route(task)
    assert len(route) > 0
    assert "summarizer" in route

def test_router_returns_valid_decision():
    """Test that router returns a valid RouteDecision."""
    task = TaskSpec(user_query="Summarize this article")
    decision = router(task)
    
    assert decision is not None
    assert len(decision.selected_agents) > 0
    assert 0 <= decision.confidence <= 1
    assert len(decision.rationale) > 0

def test_router_researcher_first_with_url():
    """Test that researcher comes first when URL is present."""
    task = TaskSpec(
        user_query="Summarize and write a post",
        source_url="https://example.com"
    )
    decision = router(task)
    
    if "researcher" in decision.selected_agents:
        assert decision.selected_agents[0] == "researcher"

