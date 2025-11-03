"""Tests for agent tools."""
import pytest
from agent.analysis.dedupe import dedupe_by_url
from agent.state import Article


def test_dedupe_by_url():
    """Test URL deduplication."""
    articles = [
        Article(ticker="AAPL", title="Test", url="https://example.com/1"),
        Article(ticker="AAPL", title="Test 2", url="https://example.com/1"),  # Duplicate
        Article(ticker="MSFT", title="Test 3", url="https://example.com/2"),
    ]
    
    unique = dedupe_by_url(articles)
    assert len(unique) == 2
    assert unique[0].url == "https://example.com/1"
    assert unique[1].url == "https://example.com/2"

