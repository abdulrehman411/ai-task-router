# Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Community Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (sign up at [share.streamlit.io](https://share.streamlit.io))

### Step 1: Push to GitHub
1. Create a new repository on GitHub
2. Push your code to the repository:
```bash
git init
git add .
git commit -m "Initial deployment setup"
git branch -M main
git remote add origin https://github.com/yourusername/ai-task-router.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account
4. Select your repository
5. Set main file to: `streamlit_app.py`
6. Click "Deploy"

### Environment Variables
In your Streamlit Cloud app settings, add these secrets:

```toml
OPENAI_API_KEY = "your-openai-api-key"
API_URL = "https://your-backend-api-url.com"  # If using separate backend
```

### Deployment Files Created
- `streamlit_app.py` - Entry point for Streamlit Cloud
- `.streamlit/config.toml` - Streamlit configuration
- `setup.cfg` - Package configuration

### Notes
- The app will run in dark mode by default
- All UI improvements are included (positioned theme toggle, proper dropdown styling)
- PDF processing is supported via PyMuPDF
- No local API server needed for UI-only deployment

### Troubleshooting
If deployment fails:
1. Check that all requirements are in `requirements.txt`
2. Verify `streamlit_app.py` is the main file
3. Ensure all imports work correctly
4. Check Streamlit Cloud logs for specific errors
