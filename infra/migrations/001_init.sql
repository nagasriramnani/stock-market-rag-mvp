-- Enable pgvector extension
create extension if not exists vector;

-- Runs table for tracking agent execution
create table if not exists runs (
  id uuid primary key default gen_random_uuid(),
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  tickers text[] not null,
  time_window_hours int not null,
  notes text[],
  errors text[],
  status text not null default 'running',
  trace_id text
);

-- Prompts audit table
create table if not exists prompts (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references runs(id) on delete cascade,
  provider text not null,
  model text not null,
  role text not null,
  content text not null,
  created_at timestamptz not null default now(),
  token_count int
);

-- Completions audit table
create table if not exists completions (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references runs(id) on delete cascade,
  provider text not null,
  model text not null,
  content text not null,
  created_at timestamptz not null default now(),
  token_count int,
  latency_ms int
);

-- Articles from news sources
create table if not exists articles (
  id uuid primary key default gen_random_uuid(),
  ticker text not null,
  title text not null,
  url text not null unique,
  source text,
  published_at timestamptz,
  summary text,
  sentiment numeric,
  relevance numeric,
  impact numeric,
  raw jsonb,
  inserted_at timestamptz not null default now()
);

-- Embeddings for vector search
create table if not exists embeddings (
  article_id uuid primary key references articles(id) on delete cascade,
  embedding vector(1536)
);

-- Price snapshots
create table if not exists prices (
  id uuid primary key default gen_random_uuid(),
  ticker text not null,
  as_of timestamptz not null,
  open numeric,
  close numeric,
  high numeric,
  low numeric,
  volume numeric,
  d1_change numeric,
  d5_change numeric,
  vol_z numeric
);

-- Generated reports metadata
create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references runs(id) on delete cascade,
  date_utc date not null,
  tickers text[] not null,
  supabase_path text not null,
  created_at timestamptz not null default now()
);

