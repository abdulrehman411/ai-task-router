#!/usr/bin/env python3
"""Example script to test the API."""
import requests
import json
from app.schemas import TaskSpec

API_URL = "http://localhost:8000"

def test_simple_summary():
    """Test a simple summary request."""
    print("Testing simple summary...")
    task = TaskSpec(
        user_query="Summarize the benefits of artificial intelligence in one paragraph",
        desired_style="concise",
        desired_length="short"
    )
    
    response = requests.post(f"{API_URL}/generate", json=task.model_dump())
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"Route: {result['route']['selected_agents']}")
        print(f"Confidence: {result['route']['confidence']:.2f}")
        print(f"\nFinal Output:\n{result['final_output']}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_url_research():
    """Test URL research and writing."""
    print("Testing URL research + writing...")
    task = TaskSpec(
        user_query="Read this page and write a brief summary",
        source_url="https://example.com",
        desired_style="friendly",
        desired_length="short"
    )
    
    response = requests.post(f"{API_URL}/generate", json=task.model_dump())
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"Route: {result['route']['selected_agents']}")
        print(f"Steps: {len(result['steps'])} agents executed")
        print(f"\nFinal Output:\n{result['final_output']}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_code_generation():
    """Test code generation."""
    print("Testing code generation...")
    task = TaskSpec(
        user_query="Write Python code to reverse a string",
        desired_style="technical"
    )
    
    response = requests.post(f"{API_URL}/generate", json=task.model_dump())
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"\nFinal Output:\n{result['final_output']}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    import sys
    
    print("AI Task Router - Example Requests\n")
    print("Make sure the API server is running: python run.py\n")
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "summary":
            test_simple_summary()
        elif test_name == "url":
            test_url_research()
        elif test_name == "code":
            test_code_generation()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: summary, url, code")
    else:
        # Run all tests
        test_simple_summary()
        print("\n" + "="*50 + "\n")
        test_code_generation()

