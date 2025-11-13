# Firebase Deployment Guide

## Overview
This guide shows how to deploy the AI Task Router backend on Firebase Cloud Functions and frontend on Streamlit Cloud.

## Prerequisites
- Node.js 18+ installed
- Firebase CLI installed: `npm install -g firebase-tools`
- Google Cloud account with billing enabled
- Firebase project created

## Step 1: Set up Firebase Project

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add project"
   - Name your project (e.g., "ai-task-router")
   - Enable Google Analytics (optional)

2. **Initialize Firebase in your project**
   ```bash
   cd firebase
   firebase login
   firebase use ai-task-router  # Replace with your project ID
   ```

3. **Install dependencies**
   ```bash
   cd functions
   npm install
   ```

## Step 2: Configure Firebase Functions

1. **Update project ID in .firebaserc**
   ```json
   {
     "projects": {
       "default": "your-actual-project-id"
     }
   }
   ```

2. **Set environment variables** (optional)
   ```bash
   firebase functions:config set openai.api_key="your-openai-key"
   ```

## Step 3: Deploy Backend to Firebase

1. **Build and deploy functions**
   ```bash
   cd firebase/functions
   npm run build
   firebase deploy --only functions
   ```

2. **Get your Firebase Functions URL**
   After deployment, Firebase will show your URLs:
   ```
   ✔ functions[health(us-central1)]: https://us-central1-your-project.cloudfunctions.net/health
   ✔ functions[generate(us-central1)]: https://us-central1-your-project.cloudfunctions.net/generate
   ```

## Step 4: Update Streamlit Frontend

1. **Update Firebase URL in ui/app.py**
   ```python
   FIREBASE_PROJECT_URL = os.getenv("FIREBASE_PROJECT_URL", "https://us-central1-your-project.cloudfunctions.net")
   ```

2. **Set environment variable in Streamlit Cloud**
   - Go to your Streamlit app settings
   - Add secret: `FIREBASE_PROJECT_URL = "https://us-central1-your-project.cloudfunctions.net"`

## Step 5: Deploy Frontend to Streamlit Cloud

1. **Push updated code to GitHub**
   ```bash
   git add .
   git commit -m "Configure Firebase backend integration"
   git push origin main
   ```

2. **Deploy to Streamlit**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file to `streamlit_app.py`
   - Add environment variables
   - Click "Deploy"

## Firebase Functions Structure

### Available Endpoints

1. **Health Check**: `https://us-central1-{project}.cloudfunctions.net/health`
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-01-01T00:00:00.000Z",
     "service": "ai-task-router-backend"
   }
   ```

2. **Task Processing**: `https://us-central1-{project}.cloudfunctions.net/generate`
   ```json
   POST /generate
   {
     "user_query": "Your task description",
     "source_url": "https://example.com",
     "desired_style": "professional",
     "desired_length": "medium"
   }
   ```

3. **PDF Extraction**: `https://us-central1-{project}.cloudfunctions.net/extractPdf`
   ```json
   POST /extractPdf
   {
     "url": "https://example.com/document.pdf"
   }
   ```

4. **URL Content Fetch**: `https://us-central1-{project}.cloudfunctions.net/fetchUrl`
   ```json
   POST /fetchUrl
   {
     "url": "https://example.com"
   }
   ```

## Testing

1. **Test locally with Firebase emulator**
   ```bash
   cd firebase/functions
   npm run serve
   ```

2. **Test deployed functions**
   ```bash
   curl https://us-central1-your-project.cloudfunctions.net/health
   ```

## Monitoring

1. **View logs**
   ```bash
   firebase functions:log
   ```

2. **Monitor in Firebase Console**
   - Go to Functions → Dashboard
   - View execution metrics and errors

## Cost Optimization

- Firebase Functions include a free tier (125,000 invocations/month)
- Configure memory and timeout appropriately
- Use Cloud Functions triggers for scheduled tasks
- Monitor usage in Google Cloud Console

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Functions include CORS middleware
   - Ensure your frontend URL is allowed

2. **Cold Starts**
   - First request may be slower
   - Consider using minimum instances for production

3. **Memory Limits**
   - Default is 256MB
   - Increase if needed for AI processing

4. **Timeout Issues**
   - Default timeout is 60 seconds
   - Increase for complex tasks

### Debugging

1. **Check function logs**
   ```bash
   firebase functions:log --only generate
   ```

2. **Test with curl**
   ```bash
   curl -X POST https://us-central1-your-project.cloudfunctions.net/generate \
     -H "Content-Type: application/json" \
     -d '{"user_query": "test query"}'
   ```

## Security

1. **API Keys**: Store in Firebase Functions config
2. **Authentication**: Implement if needed
3. **Rate Limiting**: Consider implementing usage limits
4. **Input Validation**: Functions validate input parameters

## Scaling

- Firebase Functions auto-scale automatically
- Configure regions for optimal performance
- Use Cloud Load Balancing for global distribution
- Consider Cloud Run for larger workloads
