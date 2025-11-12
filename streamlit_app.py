"""AI Task Router - Streamlit Cloud Deployment Entry Point."""
import streamlit as st
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the main UI app
from ui.app import main

if __name__ == "__main__":
    main()
