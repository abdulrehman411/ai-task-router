# Firebase Functions Backend

## Setup Instructions

### Prerequisites
- Node.js 18+ installed
- Firebase CLI installed: `npm install -g firebase-tools`

### Installation

1. **Install dependencies**
   ```bash
   cd functions
   npm install
   ```

2. **Build TypeScript**
   ```bash
   npm run build
   ```

3. **Test locally**
   ```bash
   npm run serve
   ```

4. **Deploy to Firebase**
   ```bash
   npm run deploy
   ```

## Available Functions

- `health` - Health check endpoint
- `generate` - Main AI task processing
- `extractPdf` - PDF text extraction
- `fetchUrl` - URL content fetching

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `OPENAI_API_KEY` - Your OpenAI API key
- `FIREBASE_PROJECT_ID` - Your Firebase project ID

## TypeScript Configuration

The project uses TypeScript with relaxed settings to accommodate development environments without Node.js installed. When you deploy to Firebase, the proper types will be resolved automatically.
