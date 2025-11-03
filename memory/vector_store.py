"""Vector store: pgvector embeddings with provider abstraction."""
import os
import structlog
from typing import List, Optional
from supabase import create_client
from agent.state import Article
from memory.embedding_provider import generate_embeddings, get_embedding_dimension

logger = structlog.get_logger()

_provider = os.getenv("EMBED_PROVIDER", "hf").lower()


def _get_supabase_client():
    """Lazy initialization of Supabase client."""
    SB_URL = os.getenv("SUPABASE_URL")
    SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not SB_URL or not SB_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    
    return create_client(SB_URL, SB_KEY)


def upsert_embeddings_for_articles(articles: List[Article], run_id: Optional[str] = None):
    """
    Generate embeddings and upsert to Supabase.
    
    Uses batch processing for efficiency. On any error (429/timeout/etc),
    logs warning, skips embeddings, continues run.
    """
    if not articles:
        return

    sb = _get_supabase_client()
    
    # Batch process articles
    articles_to_embed = []
    article_map = {}  # text -> article_id mapping
    
    for article in articles:
        try:
            text = f"{article.title}\n{article.summary or ''}"
            if not text.strip():
                continue

            # Insert/update article first
            existing = sb.table("articles").select("id").eq("url", article.url).limit(1).execute()

            article_id = None
            if existing.data:
                article_id = existing.data[0]["id"]
                sb.table("articles").update({
                    "title": article.title,
                    "summary": article.summary,
                    "sentiment": article.sentiment,
                    "relevance": article.relevance,
                    "impact": article.impact,
                    "source": article.source,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                }).eq("id", article_id).execute()
            else:
                result = sb.table("articles").insert({
                    "ticker": article.ticker,
                    "title": article.title,
                    "url": article.url,
                    "source": article.source,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "summary": article.summary,
                    "sentiment": article.sentiment,
                    "relevance": article.relevance,
                    "impact": article.impact,
                    "raw": article.raw,
                }).execute()
                if result.data:
                    article_id = result.data[0]["id"]

            if article_id:
                articles_to_embed.append(text[:8000])  # Limit length
                article_map[text[:8000]] = article_id
        except Exception as e:
            logger.warning("Failed to save article", url=article.url, error=str(e), run_id=run_id)
            continue

    if not articles_to_embed:
        return

    # Generate embeddings in batch
    embeddings = generate_embeddings(articles_to_embed, batch_size=64)
    
    if embeddings is None:
        logger.warning("Embedding generation failed, continuing without embeddings", run_id=run_id)
        return

    # Upsert embeddings to appropriate table
    embed_table = "embeddings_hf" if _provider == "hf" else "embeddings"
    
    for text, embedding in zip(articles_to_embed, embeddings):
        try:
            article_id = article_map.get(text)
            if not article_id:
                continue
            
            sb.table(embed_table).upsert({
                "article_id": article_id,
                "embedding": embedding,
            }, on_conflict="article_id").execute()
            
            logger.debug(
                "Upserted embedding",
                article_id=article_id,
                provider=_provider,
                dim=len(embedding),
                run_id=run_id,
            )
        except Exception as e:
            logger.warning(
                "Failed to upsert embedding",
                article_id=article_id,
                error=str(e),
                run_id=run_id,
            )
            continue

