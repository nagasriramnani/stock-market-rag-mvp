"""Tests for reporting module."""
import pytest
from agent.state import RunState, Article, PriceSnapshot
from agent.analysis.nlp import score_articles
from agent.analysis.finance import score_impact


def test_score_articles():
    """Test article relevance scoring."""
    articles = [
        Article(
            ticker="AAPL",
            title="Apple Stock Surges",
            url="https://example.com/1",
            summary="Apple stock price increases",
        ),
    ]
    
    scored = score_articles(articles, ["AAPL"])
    assert len(scored) == 1
    assert scored[0].relevance is not None
    assert scored[0].relevance >= 0


def test_score_impact():
    """Test impact scoring."""
    articles = [
        Article(
            ticker="AAPL",
            title="Apple Earnings Beat",
            url="https://example.com/1",
            summary="Apple beats earnings expectations",
            relevance=0.5,
        ),
    ]
    prices = [
        PriceSnapshot(
            ticker="AAPL",
            as_of=None,
            close=150.0,
            d1_change=2.5,
        ),
    ]
    
    scored = score_impact(articles, prices)
    assert len(scored) == 1
    assert scored[0].impact is not None
    assert scored[0].sentiment is not None

