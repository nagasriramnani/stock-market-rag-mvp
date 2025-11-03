"""RSS fallback for news aggregation."""
import feedparser
import structlog
from typing import List
from datetime import datetime, timedelta
from agent.state import Article

logger = structlog.get_logger()

# Common finance RSS feeds
RSS_FEEDS = [
    "https://feeds.finance.yahoo.com/rss/2.0/headline",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://feeds.marketwatch.com/marketwatch/topstories/",
]


def fetch_rss_fallback(tickers: List[str], time_window_hours: int = 24) -> List[Article]:
    """Fetch articles from RSS feeds as fallback."""
    articles = []
    cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)
    ticker_set = {t.upper() for t in tickers}

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:  # Limit per feed
                try:
                    title = entry.get("title", "")
                    content = entry.get("summary", "")

                    # Simple ticker matching in title/content
                    matched_ticker = None
                    for ticker in ticker_set:
                        if ticker in title.upper() or ticker in content.upper():
                            matched_ticker = ticker
                            break

                    if not matched_ticker:
                        continue

                    published_at = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        try:
                            published_at = datetime(*entry.published_parsed[:6])
                            if published_at < cutoff:
                                continue
                        except (ValueError, TypeError):
                            pass

                    article = Article(
                        ticker=matched_ticker,
                        title=title,
                        url=entry.get("link", ""),
                        source=feed_url,
                        published_at=published_at,
                        summary=content[:500] if content else None,
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning("Failed to parse RSS entry", error=str(e))
                    continue
        except Exception as e:
            logger.warning("Failed to fetch RSS feed", feed=feed_url, error=str(e))
            continue

    return articles

