-- Articles indexes
create index if not exists idx_articles_ticker_pub on articles (ticker, published_at desc);
create index if not exists idx_articles_url on articles (url);
create index if not exists idx_articles_relevance on articles (relevance desc nulls last);
create index if not exists idx_articles_impact on articles (impact desc nulls last);

-- Prices indexes
create index if not exists idx_prices_ticker_asof on prices (ticker, as_of desc);
create index if not exists idx_prices_ticker on prices (ticker);

-- Reports indexes
create index if not exists idx_reports_date on reports (date_utc desc);
create index if not exists idx_reports_run_id on reports (run_id);

-- Runs indexes
create index if not exists idx_runs_started_at on runs (started_at desc);
create index if not exists idx_runs_status on runs (status);

-- Prompts/Completions indexes
create index if not exists idx_prompts_run_id on prompts (run_id);
create index if not exists idx_completions_run_id on completions (run_id);

-- Vector similarity search index (HNSW for fast approximate nearest neighbor)
create index if not exists idx_embeddings_vec on embeddings using hnsw (embedding vector_l2_ops);

