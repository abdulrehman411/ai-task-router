"""Utility tools for fetching and processing content."""
import requests
import trafilatura
import fitz  # PyMuPDF
from typing import Optional
from app.config import Config

def normalize_text(text: str) -> str:
    """Normalize text by stripping and collapsing whitespace."""
    if not text:
        return ""
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n')]
    text = ' '.join(line for line in lines if line)
    # Collapse multiple spaces
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text.strip()

def fetch_url_text(url: str, max_length: int = None) -> str:
    """
    Fetch and extract text content from a URL.
    
    Args:
        url: The URL to fetch
        max_length: Maximum character length (defaults to config)
    
    Returns:
        Extracted text content
    """
    if max_length is None:
        max_length = Config.MAX_SOURCE_TEXT_LENGTH
    
    try:
        # Fetch the URL
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Extract text using trafilatura
        extracted = trafilatura.extract(response.text)
        
        if not extracted:
            # Fallback: try to get at least some text
            extracted = response.text[:max_length]
        
        # Normalize and truncate
        text = normalize_text(extracted)
        if len(text) > max_length:
            text = text[:max_length] + "... [truncated]"
        
        return text
    
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL {url}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error extracting text from URL {url}: {str(e)}")

def extract_pdf_text(url: str, max_length: int = None) -> str:
    """
    Download PDF from URL and extract text content.
    
    Args:
        url: The URL of the PDF file
        max_length: Maximum character length (defaults to config)
    
    Returns:
        Extracted text content from PDF
    """
    if max_length is None:
        max_length = Config.MAX_SOURCE_TEXT_LENGTH
    
    try:
        # Download PDF
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Extract text using PyMuPDF
        pdf_bytes = response.content
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_parts.append(page.get_text())
        
        doc.close()
        
        # Combine and normalize
        full_text = '\n'.join(text_parts)
        text = normalize_text(full_text)
        
        if len(text) > max_length:
            text = text[:max_length] + "... [truncated]"
        
        return text
    
    except requests.RequestException as e:
        raise ValueError(f"Failed to download PDF from {url}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF {url}: {str(e)}")

def fetch_url_or_pdf(url: str) -> str:
    """
    Automatically detect if URL is PDF or HTML and fetch accordingly.
    
    Args:
        url: The URL to fetch
    
    Returns:
        Extracted text content
    """
    url_lower = url.lower()
    
    if url_lower.endswith('.pdf') or 'application/pdf' in url_lower:
        return extract_pdf_text(url)
    else:
        return fetch_url_text(url)

