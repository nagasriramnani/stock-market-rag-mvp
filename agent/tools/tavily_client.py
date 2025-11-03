"""Tavily API client for news search with retries and timeouts."""
import os
import time
import httpx
import structlog
from typing import List
from datetime import datetime, timedelta
from agent.state import Article

logger = structlog.get_logger()

_timeout = float(os.getenv("HTTP_TIMEOUT_SEC", "40"))
_max_results = int(os.getenv("NEWS_MAX_RESULTS", "5"))
_search_depth = os.getenv("NEWS_SEARCH_DEPTH", "basic")


def _retry_request(func, max_attempts=3, run_id=None):
    """Retry HTTP request with exponential backoff."""
    delays = [2, 4, 8]
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except (httpx.HTTPError, httpx.ReadTimeout) as e:
            last_error = e
            if attempt < max_attempts - 1:
                delay = delays[attempt]
                logger.warning(
                    "HTTP request failed, retrying",
                    attempt=attempt + 1,
                    delay=delay,
                    error=str(e)[:100],
                    run_id=run_id,
                )
                time.sleep(delay)
            else:
                logger.error("HTTP request failed after retries", error=str(e), run_id=run_id)
        except Exception as e:
            logger.error("Unexpected error in HTTP request", error=str(e), run_id=run_id)
            raise
    
    raise last_error


def fetch_news_for_tickers(tickers: List[str], time_window_hours: int = 24, run_id: str = None) -> List[Article]:
    """Fetch news articles for given tickers using Tavily API with retries."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY not set, returning empty results", run_id=run_id)
        return []

    articles = []
    cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)

    with httpx.Client(timeout=_timeout) as client:
        for ticker in tickers:
            try:
                query = f"{ticker} stock news"
                
                def _make_request():
                    return client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": api_key,
                            "query": query,
                            "search_depth": _search_depth,
                            "include_answer": True,
                            "include_raw_content": False,
                            "max_results": _max_results,
                        },
                        headers={"Content-Type": "application/json"},
                    )
                
                response = _retry_request(_make_request, run_id=run_id)
                response.raise_for_status()
                data = response.json()

                for result in data.get("results", []):
                    try:
                        published_at = None
                        if result.get("published_date"):
                            try:
                                published_at = datetime.fromisoformat(
                                    result["published_date"].replace("Z", "+00:00")
                                )
                            except (ValueError, AttributeError):
                                pass

                        if published_at and published_at < cutoff:
                            continue

                        article = Article(
                            ticker=ticker,
                            title=result.get("title", ""),
                            url=result.get("url", ""),
                            source=result.get("source", ""),
                            published_at=published_at,
                            summary=result.get("content", ""),
                            raw=result,
                        )
                        articles.append(article)
                    except Exception as e:
                        logger.warning("Failed to parse article", ticker=ticker, error=str(e))
                        continue

                logger.info(
                    "Fetched Tavily results",
                    ticker=ticker,
                    count=len(data.get("results", [])),
                    run_id=run_id,
                )
            except Exception as e:
                logger.error("Tavily API error", ticker=ticker, error=str(e), run_id=run_id)
                continue

    return articles

