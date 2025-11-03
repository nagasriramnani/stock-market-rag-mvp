-- Hugging Face embeddings table (384-dimensional vectors for all-MiniLM-L6-v2)
create table if not exists embeddings_hf (
  article_id uuid primary key references articles(id) on delete cascade,
  embedding vector(384)
);

-- Index for fast similarity search
create index if not exists idx_embeddings_hf_vec on embeddings_hf using hnsw (embedding vector_l2_ops);

