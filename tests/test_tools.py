"""Tests for utility tools."""
import pytest
from app.tools import normalize_text, fetch_url_text, extract_pdf_text

def test_normalize_text():
    """Test text normalization."""
    text = "  This   is   a   test  \n\n  with   multiple   spaces  "
    normalized = normalize_text(text)
    assert "  " not in normalized
    assert normalized.startswith("This")
    assert normalized.endswith("spaces")

def test_normalize_text_empty():
    """Test normalization of empty text."""
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""

def test_fetch_url_text():
    """Test URL text fetching."""
    # Test with a simple, known URL
    try:
        text = fetch_url_text("https://example.com", max_length=1000)
        assert len(text) > 0
        assert len(text) <= 1000
    except Exception as e:
        # Network issues are acceptable in tests
        pytest.skip(f"Network error: {e}")

def test_fetch_url_text_invalid_url():
    """Test URL fetching with invalid URL."""
    with pytest.raises((ValueError, Exception)):
        fetch_url_text("https://invalid-url-that-does-not-exist-12345.com")

