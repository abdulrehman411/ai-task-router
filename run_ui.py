#!/usr/bin/env python3
"""Run the Streamlit UI."""
import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch Streamlit UI."""
    ui_path = Path(__file__).parent / "ui" / "app.py"
    
    if not ui_path.exists():
        print(f"Error: UI file not found at {ui_path}")
        sys.exit(1)
    
    # Check if API is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("⚠️  API server may not be running. Make sure to start it with: python3 run.py")
    except:
        print("⚠️  API server not detected. Make sure to start it with: python3 run.py")
        print("   The UI will still work but API calls will fail.")
    
    print(f"\n🚀 Starting Streamlit UI...")
    print(f"   UI will be available at: http://localhost:8501")
    print(f"   Make sure the API is running at: http://localhost:8000\n")
    
    # Run Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(ui_path),
        "--server.port", "8501",
        "--server.address", "localhost"
    ])

if __name__ == "__main__":
    main()

