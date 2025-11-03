"""Embedding provider abstraction: Hugging Face (local), OpenAI, or HF API."""
import os
import structlog
from typing import List, Optional
import numpy as np

logger = structlog.get_logger()

_provider = os.getenv("EMBED_PROVIDER", "hf").lower()
_hf_model_name = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Lazy-loaded providers
_hf_model = None
_openai_client = None
_hf_api_token = None


def _get_hf_local():
    """Get or initialize local Hugging Face model."""
    global _hf_model
    if _hf_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _hf_model = SentenceTransformer(_hf_model_name)
            logger.info("Loaded HF local model", model=_hf_model_name)
        except ImportError:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers torch")
    return _hf_model


def _get_openai():
    """Get or initialize OpenAI client."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set for OpenAI embeddings")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def generate_embeddings(texts: List[str], batch_size: int = 64) -> Optional[List[List[float]]]:
    """
    Generate embeddings based on EMBED_PROVIDER.
    
    Returns:
        List of embedding vectors, or None if generation failed
    """
    if not texts:
        return []
    
    try:
        if _provider == "hf":
            # Local Hugging Face
            model = _get_hf_local()
            embeddings = model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return embeddings.tolist()
        
        elif _provider == "openai":
            # OpenAI API
            client = _get_openai()
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts,
            )
            return [item.embedding for item in response.data]
        
        elif _provider == "hf_api":
            # Hugging Face Inference API
            import httpx
            global _hf_api_token
            if not _hf_api_token:
                _hf_api_token = os.getenv("HF_API_TOKEN")
                if not _hf_api_token:
                    raise ValueError("HF_API_TOKEN not set for HF API embeddings")
            
            url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{_hf_model_name}"
            headers = {"Authorization": f"Bearer {_hf_api_token}"}
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json={"inputs": texts}, headers=headers)
                response.raise_for_status()
                return response.json()
        
        else:
            logger.error("Unknown EMBED_PROVIDER", provider=_provider)
            return None
    
    except Exception as e:
        error_str = str(e)
        logger.warning(
            "Embedding generation failed",
            provider=_provider,
            error=error_str,
            text_count=len(texts),
        )
        return None


def get_embedding_dimension() -> int:
    """Get embedding dimension for current provider."""
    if _provider == "hf":
        return 384  # all-MiniLM-L6-v2
    elif _provider == "openai":
        return 1536  # text-embedding-3-small
    elif _provider == "hf_api":
        return 384  # Default HF API models
    return 384

