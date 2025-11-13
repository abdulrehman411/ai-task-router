"""AI Task Router - Modern UI with Dark/Light Mode."""
import streamlit as st
import requests
import json
import sys
import os
import io
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas import TaskSpec, FinalPackage

# Page configuration
st.set_page_config(
    page_title="AI Task Router - Firebase Powered",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'task_history' not in st.session_state:
    st.session_state.task_history = []
if 'current_result' not in st.session_state:
    st.session_state.current_result = None
if 'uploaded_pdf_text' not in st.session_state:
    st.session_state.uploaded_pdf_text = None
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# API Configuration
# Firebase Functions URL - replace with your actual Firebase project URL
FIREBASE_PROJECT_URL = os.getenv("FIREBASE_PROJECT_URL", "https://us-central1-ai-task-router.cloudfunctions.net")
DEFAULT_API_URL = f"{FIREBASE_PROJECT_URL}/generate"
HEALTH_CHECK_URL = f"{FIREBASE_PROJECT_URL}/health"

def check_backend_health(api_url: str = HEALTH_CHECK_URL) -> tuple[bool, str]:
    """Check if Firebase backend is running and healthy."""
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return True, "Firebase backend is healthy"
        else:
            return False, f"Backend returned status {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Firebase backend is not responding (timeout)"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Firebase backend"
    except requests.exceptions.RequestException as e:
        return False, f"Firebase connection error: {str(e)}"

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from uploaded PDF file."""
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_parts.append(page.get_text())
        
        doc.close()
        
        full_text = '\n'.join(text_parts)
        lines = [line.strip() for line in full_text.split('\n')]
        text = ' '.join(line for line in lines if line)
        
        max_length = 50000
        if len(text) > max_length:
            text = text[:max_length] + "... [truncated]"
        
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def get_css(dark_mode: bool) -> str:
    """Get CSS based on theme mode."""
    if dark_mode:
        return """
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dark Mode Styles */
    .stApp {
        background: #000000;
        color: #ffffff;
    }
    
    /* Main Container */
    .main-wrapper {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Header */
    .header-section {
        text-align: center;
        padding: 3rem 0 2rem 0;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #a0a0a0;
        font-weight: 300;
    }
    
    /* Theme Toggle */
    .theme-toggle {
        position: fixed;
        top: 120px;
        right: 20px;
        z-index: 1000;
    }
    
    /* Input Card */
    .input-card {
        background: #1a1a1a;
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid #333333;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    /* Output Card */
    .output-card {
        background: #1a1a1a;
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid #333333;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    .output-content {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #e0e0e0;
        white-space: pre-wrap;
    }
    
    /* Process Flow */
    .process-flow {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0;
        padding: 1.5rem;
        background: #1a1a1a;
        border-radius: 12px;
        border: 1px solid #333333;
    }
    
    .process-step {
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        min-width: 120px;
        text-align: center;
    }
    
    .step-label {
        font-weight: 700;
        font-size: 0.85rem;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .step-arrow {
        color: #667eea;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:not([kind="primary"]) {
        background: #2a2a2a;
        color: #667eea;
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:not([kind="primary"]):hover {
        background: #667eea;
        color: #ffffff;
    }
    
    /* Success Banner */
    .success-banner {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 2rem 0;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Example Card */
    .example-card {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #333333;
        transition: all 0.3s;
    }
    
    .example-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    /* History Item */
    .history-item {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s;
    }
    
    .history-item:hover {
        transform: translateX(5px);
        border-left-color: #764ba2;
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    p, div, span, label, .stMarkdown {
        color: #e0e0e0 !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        color: #ffffff !important;
        background-color: #2a2a2a !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Select boxes */
    .stSelectbox label {
        color: #e0e0e0 !important;
        font-weight: 600;
    }
    
    /* Info boxes */
    .stInfo {
        background: #1a1a1a;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
    }
    
    /* Code blocks */
    .stCode {
        background-color: #0a0a0a;
        color: #e0e0e0;
        border: 1px solid #333333;
        border-radius: 8px;
    }
    
    /* Captions */
    .stCaption {
        color: #a0a0a0 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666666;
        margin-top: 3rem;
        border-top: 1px solid #333333;
    }
    </style>
    """
    else:
        return """
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Light Mode Styles */
    .stApp {
        background: #f5f5f5;
        color: #1f2937;
    }
    
    /* Main Container */
    .main-wrapper {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Header */
    .header-section {
        text-align: center;
        padding: 3rem 0 2rem 0;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        font-weight: 300;
    }
    
    /* Theme Toggle */
    .theme-toggle {
        position: fixed;
        top: 120px;
        right: 20px;
        z-index: 1000;
    }
    
    /* Input Card */
    .input-card {
        background: #ffffff;
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Output Card */
    .output-card {
        background: #ffffff;
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin: 2rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .output-content {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #1e293b;
        white-space: pre-wrap;
    }
    
    /* Process Flow */
    .process-flow {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0;
        padding: 1.5rem;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
    
    .process-step {
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        min-width: 120px;
        text-align: center;
    }
    
    .step-label {
        font-weight: 700;
        font-size: 0.85rem;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .step-arrow {
        color: #667eea;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:not([kind="primary"]) {
        background: #ffffff;
        color: #667eea;
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:not([kind="primary"]):hover {
        background: #667eea;
        color: #ffffff;
    }
    
    /* Success Banner */
    .success-banner {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 2rem 0;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Example Card */
    .example-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #e5e7eb;
        transition: all 0.3s;
    }
    
    .example-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* History Item */
    .history-item {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s;
    }
    
    .history-item:hover {
        transform: translateX(5px);
        border-left-color: #764ba2;
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #1f2937 !important;
    }
    
    p, div, span, label, .stMarkdown {
        color: #374151 !important;
    }
    
    /* Input fields - Rounded corners, proper styling */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        color: #1f2937 !important;
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    /* Placeholder text styling */
    .stTextInput>div>div>input::placeholder,
    .stTextArea>div>div>textarea::placeholder {
        color: #9ca3af !important;
        opacity: 1 !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }
    
    /* File Uploader - Drag and drop styling */
    .stFileUploader {
        border: 2px dashed #d1d5db !important;
        border-radius: 12px !important;
        background-color: #f9fafb !important;
        padding: 2rem !important;
        text-align: center !important;
        transition: all 0.3s !important;
        min-height: 150px !important;
    }
    
    .stFileUploader:hover {
        border-color: #667eea !important;
        background-color: #f3f4f6 !important;
    }
    
    .stFileUploader label {
        color: #374151 !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* File uploader drop zone container */
    .stFileUploader > div {
        border: 2px dashed #d1d5db !important;
        background-color: #f9fafb !important;
        padding: 2rem !important;
    }
    
    /* File uploader inner div */
    .stFileUploader > div > div {
        border: none !important;
        background: transparent !important;
    }
    
    /* File uploader button - light style */
    .stFileUploader button,
    .stFileUploader button[type="button"] {
        background-color: #667eea !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.625rem 1.25rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-top: 0.5rem !important;
        transition: all 0.3s !important;
    }
    
    .stFileUploader button:hover,
    .stFileUploader button[type="button"]:hover {
        background-color: #5a67d8 !important;
        transform: translateY(-1px) !important;
    }
    
    /* File uploader text */
    .stFileUploader small,
    .stFileUploader p {
        color: #6b7280 !important;
        font-size: 0.875rem !important;
    }
    
    /* Select boxes - Light styling in light mode */
    .stSelectbox label {
        color: #374151 !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }
    
    /* BaseWeb Select - Target all possible selectors */
    .stSelectbox [data-baseweb="select"],
    .stSelectbox div[data-baseweb="select"],
    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
    }
    
    /* Select value container */
    .stSelectbox [data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #374151 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        min-height: 44px !important;
    }
    
    /* Select value text */
    .stSelectbox [data-baseweb="select"] > div > div,
    div[data-baseweb="select"] > div > div {
        color: #374151 !important;
        font-weight: 500 !important;
    }
    
    /* Select arrow icon */
    .stSelectbox svg,
    div[data-baseweb="select"] svg {
        color: #374151 !important;
    }
    
    /* Selectbox dropdown popover */
    div[data-baseweb="popover"],
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1) !important;
    }
    
    /* Dropdown list */
    ul[role="listbox"],
    [role="listbox"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 0.5rem 0 !important;
    }
    
    /* Dropdown options */
    li[role="option"],
    [role="option"] {
        background-color: #ffffff !important;
        color: #374151 !important;
        padding: 0.75rem 1rem !important;
        border-radius: 8px !important;
        margin: 0.25rem 0.5rem !important;
    }
    
    li[role="option"]:hover,
    [role="option"]:hover {
        background-color: #f3f4f6 !important;
    }
    
    li[role="option"][aria-selected="true"],
    [role="option"][aria-selected="true"] {
        background-color: #667eea !important;
        color: #ffffff !important;
    }
    
    /* Additional dropdown styling for better coverage */
    .stSelectbox .css-1d391kg,
    .stSelectbox .css-1wa3eu0,
    .stSelectbox .css-1lcbmhc {
        background-color: #ffffff !important;
        color: #374151 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
    }
    
    .stSelectbox .css-1d391kg:hover,
    .stSelectbox .css-1wa3eu0:hover,
    .stSelectbox .css-1lcbmhc:hover {
        border-color: #667eea !important;
    }
    
    /* Info boxes */
    .stInfo {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
    }
    
    /* Code blocks */
    .stCode {
        background-color: #f9fafb;
        color: #1f2937;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }
    
    /* Captions */
    .stCaption {
        color: #6b7280 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #6b7280;
        margin-top: 3rem;
        border-top: 1px solid #e5e7eb;
    }
    </style>
    """

def call_api(task_spec: TaskSpec, api_url: str = DEFAULT_API_URL, pdf_text: Optional[str] = None) -> FinalPackage:
    """Call the API endpoint."""
    try:
        if pdf_text:
            task_spec.user_query = f"{task_spec.user_query}\n\n[PDF Content]: {pdf_text[:5000]}"
        
        response = requests.post(
            f"{api_url}/generate",
            json=task_spec.model_dump(),
            timeout=120
        )
        response.raise_for_status()
        return FinalPackage(**response.json())
    except requests.exceptions.Timeout:
        raise Exception("The request took too long. Please try a simpler task or try again later.")
    except requests.exceptions.ConnectionError:
        raise Exception("Unable to connect to the service. Please check your connection or contact support.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"An error occurred while processing your request. Please try again.")

def display_process_flow(agents: list):
    """Display the processing flow."""
    agent_labels = {
        "researcher": "RESEARCH",
        "summarizer": "SUMMARIZE",
        "writer": "WRITE",
        "coder": "CODE",
        "analyst": "ANALYZE"
    }
    
    flow_html = '<div class="process-flow">'
    for i, agent in enumerate(agents):
        label = agent_labels.get(agent, agent.upper())
        flow_html += f'''
        <div class="process-step">
            <div class="step-label">{label}</div>
        </div>
        '''
        if i < len(agents) - 1:
            flow_html += '<div class="step-arrow">→</div>'
    flow_html += '</div>'
    
    st.markdown(flow_html, unsafe_allow_html=True)

def save_to_history(task_spec: TaskSpec, result: FinalPackage):
    """Save task to history."""
    history_item = {
        "timestamp": datetime.now().isoformat(),
        "query": task_spec.user_query[:100],
        "output": result.final_output[:200],
        "result": result.model_dump()
    }
    st.session_state.task_history.insert(0, history_item)
    if len(st.session_state.task_history) > 5:
        st.session_state.task_history = st.session_state.task_history[:5]

def main():
    """Main application."""
    # Initialize session state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'task_history' not in st.session_state:
        st.session_state.task_history = []
    
    # Apply CSS based on theme
    st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)
    
    # Firebase Configuration Sidebar
    with st.sidebar:
        st.header("🔥 Firebase Configuration")
        
        # Firebase Project URL Configuration
        st.subheader("Backend Settings")
        firebase_url = st.text_input(
            "Firebase Project URL",
            value=FIREBASE_PROJECT_URL,
            help="Your Firebase Cloud Functions URL"
        )
        
        # Update API URLs based on Firebase URL
        api_url = f"{firebase_url}/generate"
        health_url = f"{firebase_url}/health"
        
        # Display current endpoints
        st.subheader("📡 API Endpoints")
        st.code(f"Health: {health_url}")
        st.code(f"Generate: {api_url}")
        
        st.divider()
        
        # Manual health check
        if st.button("🔄 Check Firebase Status", type="secondary"):
            with st.spinner("Checking Firebase backend..."):
                is_healthy, status_message = check_backend_health(health_url)
                if is_healthy:
                    st.success("✅ Firebase backend is healthy!")
                else:
                    st.error(f"❌ {status_message}")
        
        st.divider()
        
        # Firebase info
        st.subheader("ℹ️ Firebase Info")
        st.info("🔥 Connected to Firebase Cloud Functions")
        st.caption("Backend runs on serverless Firebase Functions")
    
    # Theme Toggle Button (Top Right)
    col_toggle, col_status, _ = st.columns([1, 2, 20])
    with col_toggle:
        if st.button("🌙" if not st.session_state.dark_mode else "☀️", key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    with col_status:
        # Check Firebase backend health
        is_healthy, status_message = check_backend_health(health_url)
        if is_healthy:
            st.success("🟢 Firebase Online")
        else:
            st.error("🔴 Firebase Offline")
            st.caption(status_message)
    
    # Header Section
    st.markdown("""
        <div class="header-section">
            <div class="main-title">AI Task Router</div>
            <div class="subtitle">Intelligent task processing powered by specialized AI agents</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Main Content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Input Section
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("### What would you like to accomplish?")
        
        with st.form("task_form", clear_on_submit=False):
            user_query = st.text_area(
                "Describe your task",
                placeholder="Example: Summarize this article and create a LinkedIn post...",
                height=120,
                label_visibility="collapsed"
            )
            
            # URL and PDF Upload
            col_url, col_pdf = st.columns([2, 1])
            with col_url:
                source_url = st.text_input(
                    "Source URL (optional)",
                    placeholder="https://example.com/article.pdf",
                    help="Add a URL or PDF link to analyze"
                )
            
            with col_pdf:
                uploaded_file = st.file_uploader(
                    "Upload PDF",
                    type=['pdf'],
                    help="Upload a PDF file to analyze",
                    label_visibility="visible"
                )
                
                if uploaded_file is not None:
                    try:
                        with st.spinner("Reading PDF..."):
                            pdf_text = extract_text_from_pdf(uploaded_file)
                            st.session_state.uploaded_pdf_text = pdf_text
                            st.success(f"✓ PDF loaded ({len(pdf_text)} characters)")
                    except Exception as e:
                        st.error(f"Error reading PDF: {str(e)}")
                        st.session_state.uploaded_pdf_text = None
                else:
                    st.session_state.uploaded_pdf_text = None
            
            col1, col2 = st.columns(2)
            with col1:
                output_style = st.selectbox(
                    "Output Style",
                    options=["concise", "technical", "friendly", "executive"],
                    index=0
                )
            
            with col2:
                output_length = st.selectbox(
                    "Output Length",
                    options=["short", "medium", "long"],
                    index=0
                )
            
            submitted = st.form_submit_button("PROCESS TASK", use_container_width=True, type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process Task
        if submitted:
            if not user_query.strip():
                st.error("Please enter a task description.")
            else:
                # Check Firebase backend health before processing
                is_healthy, status_message = check_backend_health(health_url)
                if not is_healthy:
                    st.error(f"❌ Firebase backend is not available: {status_message}")
                    st.warning("Please check your Firebase configuration or try again later.")
                    st.stop()
                
                pdf_text = None
                final_url = None
                
                if st.session_state.uploaded_pdf_text:
                    pdf_text = st.session_state.uploaded_pdf_text
                    st.info("Using uploaded PDF content")
                elif source_url and source_url.strip():
                    final_url = source_url.strip()
                    st.info("Using source URL")
                
                task_spec = TaskSpec(
                    user_query=user_query.strip(),
                    source_url=final_url,
                    desired_style=output_style,
                    desired_length=output_length
                )
                
                # Progress indicator
                progress_container = st.container()
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        status_text.markdown("**Analyzing your task...**")
                        progress_bar.progress(20)
                        
                        status_text.markdown("**Routing to specialized agents...**")
                        progress_bar.progress(40)
                        
                        status_text.markdown("**Processing with AI agents...**")
                        progress_bar.progress(60)
                        
                        result = call_api(task_spec, api_url=api_url, pdf_text=pdf_text)
                        
                        progress_bar.progress(80)
                        status_text.markdown("**Finalizing results...**")
                        
                        save_to_history(task_spec, result)
                        st.session_state.current_result = result.model_dump()
                        
                        progress_bar.progress(100)
                        progress_bar.empty()
                        status_text.empty()
                        
                        # Success message
                        st.markdown('<div class="success-banner">Task completed successfully!</div>', unsafe_allow_html=True)
                        
                        # Display process flow
                        st.markdown("### Processing Flow")
                        display_process_flow(result.route.selected_agents)
                        
                        # Display output
                        st.markdown("### Your Result")
                        st.markdown(f'''
                        <div class="output-card">
                            <div class="output-content">{result.final_output}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Action buttons
                        col_copy, col_download = st.columns(2)
                        with col_copy:
                            st.code(result.final_output, language=None)
                            st.caption("Click in the box above and press Cmd/Ctrl+C to copy")
                        with col_download:
                            st.download_button(
                                label="DOWNLOAD RESULT",
                                data=result.final_output,
                                file_name=f"task_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        st.balloons()
                        
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"**Error:** {str(e)}")
                        st.info("💡 **Tip:** Try simplifying your task or check if the source URL is accessible.")
        
        # Show current result if available
        elif st.session_state.current_result:
            result = FinalPackage(**st.session_state.current_result)
            
            st.markdown("### Previous Result")
            st.markdown(f'''
            <div class="output-card">
                <div class="output-content">{result.final_output}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            col_copy, col_download = st.columns(2)
            with col_copy:
                st.code(result.final_output, language=None)
            with col_download:
                st.download_button(
                    label="DOWNLOAD RESULT",
                    data=result.final_output,
                    file_name=f"task_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    
    with col_right:
        # Quick Examples
        st.markdown("### Quick Examples")
        examples = [
            {
                "title": "Content Summary",
                "query": "Summarize the benefits of AI in one paragraph",
                "style": "concise",
                "length": "short"
            },
            {
                "title": "Social Media Post",
                "query": "Create a LinkedIn post about machine learning",
                "style": "friendly",
                "length": "short"
            },
            {
                "title": "Code Generation",
                "query": "Write Python code to sort a list",
                "style": "technical"
            }
        ]
        
        for i, example in enumerate(examples):
            title_color = "#667eea" if not st.session_state.dark_mode else "#667eea"
            desc_color = "#6b7280" if not st.session_state.dark_mode else "#a0a0a0"
            
            st.markdown(f'''
            <div class="example-card">
                <strong style="color: {title_color}; font-size: 1.1rem;">{example['title']}</strong><br>
                <small style="color: {desc_color};">{example['query']}</small>
            </div>
            ''', unsafe_allow_html=True)
            if st.button(f"Use Example", key=f"ex_{i}", use_container_width=True):
                st.session_state.example_query = example['query']
                st.session_state.example_style = example.get('style', 'concise')
                st.session_state.example_length = example.get('length', 'short')
                st.rerun()
        
        st.markdown("---")
        
        # Task History
        if st.session_state.task_history:
            st.markdown("### Recent Tasks")
            for i, item in enumerate(st.session_state.task_history[:3]):
                timestamp = datetime.fromisoformat(item['timestamp']).strftime("%H:%M")
                time_color = "#667eea" if not st.session_state.dark_mode else "#667eea"
                desc_color = "#6b7280" if not st.session_state.dark_mode else "#a0a0a0"
                
                st.markdown(f'''
                <div class="history-item">
                    <strong style="color: {time_color};">{timestamp}</strong><br>
                    <small style="color: {desc_color};">{item['query']}...</small>
                </div>
                ''', unsafe_allow_html=True)
                
                if st.button(f"Load", key=f"hist_{i}", use_container_width=True):
                    st.session_state.current_result = item['result']
                    st.rerun()
        
        # Info Section
        st.markdown("---")
        st.markdown("### How It Works")
        st.info("""
        1. **Describe your task** - Tell us what you need
        
        2. **AI routes your task** - Our system selects the right agents
        
        3. **Get your result** - Receive polished output in seconds
        """)
        
        st.markdown("### Capabilities")
        st.caption("""
        • Research & Summarize
        • Content Writing
        • Code Generation
        • Data Analysis
        """)
    
    # Footer
    st.markdown("""
        <div class="footer">
            © 2024 AI Task Router. All rights reserved.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
