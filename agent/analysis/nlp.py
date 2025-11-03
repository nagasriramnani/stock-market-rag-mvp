"""NLP analysis: relevance scoring via TF-IDF."""
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from agent.state import Article

def score_articles(articles: List[Article], tickers: List[str]) -> List[Article]:
    """Score article relevance using TF-IDF baseline."""
    if not articles:
        return articles

    # Combine title + summary for vectorization
    texts = []
    for article in articles:
        text = f"{article.title} {article.summary or ''}"
        texts.append(text.lower())

    # TF-IDF on ticker-related terms
    ticker_terms = [t.lower() for t in tickers]
    ticker_terms.extend(["stock", "shares", "earnings", "revenue", "growth", "price", "market"])

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=100,
        vocabulary=ticker_terms,
        min_df=1,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        # Simple relevance = sum of ticker term scores
        for i, article in enumerate(articles):
            scores = tfidf_matrix[i].toarray()[0]
            article.relevance = float(scores.sum()) if len(scores) > 0 else 0.0
    except ValueError:
        # Fallback: simple keyword count
        for article in articles:
            text_lower = f"{article.title} {article.summary or ''}".lower()
            count = sum(1 for term in ticker_terms if term in text_lower)
            article.relevance = float(count) / len(ticker_terms) if ticker_terms else 0.0

    return articles

