- Primary vector collection: news (Day 1 launch scope)
- Roadmap collections: earnings_calls and filings once transcripts available
- Chunk documents into ~800-1000 token windows with 100 token overlap
- Ingestion captures metadata fields ticker, datetime, url, source
- Store embeddings in Vertex Matching Engine or Pinecone (TBD)
- Retrieval defaults to top_k = 8 with rerank fallback if latency permits
- Cache frequent queries per ticker to reduce repeated vector hits
- Log retrieval scores for offline evaluation and threshold tuning
- Periodically refresh summary embeddings after major events

