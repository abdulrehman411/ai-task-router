/**
 * Firebase Cloud Functions for AI Task Router Backend
 * 
 * NOTE: This file may show TypeScript lint errors in development environments
 * without Node.js installed. When deployed to Firebase, all dependencies
 * will be properly resolved and the code will compile without issues.
 * 
 * To test locally:
 * 1. cd functions
 * 2. npm install
 * 3. npm run build
 * 4. npm run serve
 */

import * as functions from "firebase-functions";
import * as admin from "firebase-admin";
import * as cors from "cors";
import * as https from "https";
import * as http from "http";
import { TaskSpec, FinalPackage } from "./schemas";
import { executePipeline } from "./graph";

// Initialize Firebase Admin
admin.initializeApp();

// CORS configuration
const corsMiddleware = cors({origin: true});

// Health check endpoint
export const health = functions.https.onRequest((request, response) => {
  corsMiddleware(request, response, () => {
    try {
      response.status(200).json({
        status: "healthy",
        timestamp: new Date().toISOString(),
        service: "ai-task-router-backend"
      });
    } catch (error: any) {
      response.status(500).json({
        status: "unhealthy",
        error: error?.message || 'Unknown error'
      });
    }
  });
});

// Main task processing endpoint
export const generate = functions.https.onRequest((request, response) => {
  corsMiddleware(request, response, async () => {
    // Only allow POST requests
    if (request.method !== 'POST') {
      response.status(405).json({ error: 'Method not allowed' });
      return;
    }

    try {
      // Validate request body
      const taskSpec: TaskSpec = request.body;
      
      if (!taskSpec?.user_query) {
        response.status(400).json({ error: 'user_query is required' });
        return;
      }

      // Execute the AI pipeline
      const result: FinalPackage = await executePipeline(taskSpec);
      
      response.status(200).json(result);
    } catch (error: any) {
      console.error('Error processing task:', error);
      response.status(500).json({
        error: 'Internal server error',
        message: error?.message || 'Unknown error'
      });
    }
  });
});

// PDF text extraction endpoint
export const extractPdf = functions.https.onRequest((request, response) => {
  corsMiddleware(request, response, async () => {
    if (request.method !== 'POST') {
      response.status(405).json({ error: 'Method not allowed' });
      return;
    }

    try {
      const { url } = request.body;
      
      if (!url) {
        response.status(400).json({ error: 'URL is required' });
        return;
      }

      // Extract PDF text (you'll need to implement this in Node.js)
      const text = await extractPdfText(url);
      
      response.status(200).json({ text });
    } catch (error: any) {
      console.error('Error extracting PDF:', error);
      response.status(500).json({
        error: 'PDF extraction failed',
        message: error?.message || 'Unknown error'
      });
    }
  });
});

// URL content fetching endpoint
export const fetchUrl = functions.https.onRequest((request, response) => {
  corsMiddleware(request, response, async () => {
    if (request.method !== 'POST') {
      response.status(405).json({ error: 'Method not allowed' });
      return;
    }

    try {
      const { url } = request.body;
      
      if (!url) {
        response.status(400).json({ error: 'URL is required' });
        return;
      }

      // Fetch URL content
      const text = await fetchUrlContent(url);
      
      response.status(200).json({ text });
    } catch (error: any) {
      console.error('Error fetching URL:', error);
      response.status(500).json({
        error: 'URL fetch failed',
        message: error?.message || 'Unknown error'
      });
    }
  });
});

// Helper functions (to be implemented)
async function extractPdfText(url: string): Promise<string> {
  // Implement PDF extraction using Node.js libraries
  // For now, return a placeholder
  throw new Error('PDF extraction not yet implemented in Firebase Functions');
}

async function fetchUrlContent(url: string): Promise<string> {
  // Implement URL content fetching
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    
    client.get(url, (res: any) => {
      let data = '';
      
      res.on('data', (chunk: any) => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve(data);
      });
    }).on('error', (err: any) => {
      reject(err);
    });
  });
}
