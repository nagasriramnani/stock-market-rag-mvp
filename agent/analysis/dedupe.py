"""Deduplication by URL hash."""
import hashlib
from typing import List
from agent.state import Article

def dedupe_by_url(articles: List[Article]) -> List[Article]:
    """Remove duplicate articles by URL."""
    seen = set()
    unique = []
    for article in articles:
        url_hash = hashlib.md5(article.url.encode()).hexdigest()
        if url_hash not in seen:
            seen.add(url_hash)
            unique.append(article)
    return unique

