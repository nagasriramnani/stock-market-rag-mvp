"""Finance analysis: sentiment and impact scoring."""
from typing import List
from agent.state import Article, PriceSnapshot

def simple_sentiment(text: str) -> float:
    """Simple sentiment score (-1 to 1)."""
    text_lower = text.lower()
    positive = sum(1 for word in ["up", "gain", "rise", "growth", "beat", "strong", "bullish", "positive"])
    negative = sum(1 for word in ["down", "fall", "drop", "loss", "miss", "weak", "bearish", "negative", "decline"])
    if positive + negative == 0:
        return 0.0
    return (positive - negative) / (positive + negative + 1)

def score_impact(articles: List[Article], prices: List[PriceSnapshot]) -> List[Article]:
    """Score article impact based on relevance, sentiment, and price context."""
    price_map = {p.ticker: p for p in prices}

    for article in articles:
        # Sentiment
        text = f"{article.title} {article.summary or ''}"
        article.sentiment = simple_sentiment(text)

        # Impact = relevance * |sentiment| * price_magnitude_factor
        relevance = article.relevance or 0.0
        sentiment_mag = abs(article.sentiment or 0.0)
        price = price_map.get(article.ticker)
        price_factor = 1.0
        if price and price.d1_change:
            # Higher price volatility increases impact potential
            price_factor = 1.0 + abs(price.d1_change) / 100.0

        article.impact = relevance * sentiment_mag * price_factor

    return articles

