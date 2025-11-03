# AI Stock Research Agent

Autonomous AI agent that monitors selected tickers, ingests & ranks news, analyzes market context, and generates investor-style briefs with citations. Features a futuristic web dashboard with beautiful report viewer.

**Repository**: [https://github.com/nagasriramnani/stock-market-rag-mvp](https://github.com/nagasriramnani/stock-market-rag-mvp)

## 🎯 Features

- **Autonomous Monitoring**: Continuous monitoring of selected stock tickers
- **News Aggregation**: Tavily API + RSS fallback for comprehensive news coverage
- **Market Analysis**: Alpha Vantage integration for real-time market data
- **Intelligent Ranking**: TF-IDF relevance, sentiment analysis, impact scoring
- **Vector Memory**: Supabase pgvector for semantic search and memory
- **Beautiful Report Viewer**: Rich markdown rendering with TOC, syntax highlighting, print-ready layout
- **Futuristic Dashboard**: Neon/glass aesthetic with glassmorphism, smooth animations
- **Production Ready**: Docker, CI/CD, comprehensive tests, structured logging

## 🏗️ Project Structure

```
ai-stock-agent/
├── apps/
│   ├── api/                    # FastAPI backend service
│   │   └── main.py            # API endpoints, CORS, validation
│   └── web/                   # Next.js frontend dashboard
│       ├── app/               # Next.js App Router pages
│       │   ├── page.tsx       # Home page
│       │   ├── run/           # Run analysis page
│       │   └── reports/       # Reports list & viewer
│       ├── components/        # React components
│       │   ├── ui/            # shadcn/ui components
│       │   ├── ReportShell.tsx # Report viewer layout
│       │   ├── Outline.tsx    # Table of contents
│       │   └── Prose.tsx       # Markdown prose wrapper
│       └── lib/
│           ├── mdx.tsx        # Markdown → React pipeline
│           └── supabase.ts   # Supabase client
├── agent/
│   ├── graph.py              # LangGraph orchestration
│   ├── state.py              # Pydantic state models
│   ├── tools/                # External API clients
│   │   ├── tavily_client.py  # News search with retries
│   │   ├── alpha_vantage.py  # Price data with retries
│   │   ├── rss_client.py     # RSS fallback
│   │   └── llm_client.py     # OpenAI LLM
│   ├── analysis/              # Analysis modules
│   │   ├── nlp.py            # TF-IDF relevance scoring
│   │   ├── finance.py        # Impact scoring
│   │   └── dedupe.py         # URL deduplication
│   └── reporting/             # Report generation
│       ├── render.py         # Markdown/PDF rendering
│       └── template.md.j2    # Jinja2 report template
├── memory/                    # Supabase integration
│   ├── kv_store.py           # Run tracking
│   ├── vector_store.py        # Embeddings & vector search
│   └── embedding_provider.py # Embedding provider abstraction
├── infra/                     # Infrastructure
│   ├── migrations/           # Database migrations
│   │   ├── 001_init.sql      # Tables & schema
│   │   ├── 002_indexes.sql   # Performance indexes
│   │   ├── 003_embeddings_hf.sql # HF embeddings table
│   │   └── 004_fix_errors_default.sql # Fix NULL defaults
│   ├── docker/               # Dockerfiles
│   └── compose.yaml          # Docker Compose
├── scripts/                   # Utility scripts
│   ├── run_once.py           # CLI runner
│   └── seed_demo.py          # Demo data
├── tests/                     # Test suite
├── pyproject.toml            # Python dependencies
├── Makefile                  # Build commands
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** (required, not 3.12+ due to compatibility)
- **Node.js 18+** (for Next.js dashboard)
- **Supabase Account** (free tier works)
  - Postgres database with pgvector extension
  - Storage bucket for reports

### Step 1: Clone & Install

```bash
# Clone repository
git clone <your-repo-url>
cd "AI Agent System with Multi-Tool Integration"

# Install Python dependencies
pip install -e .

# Install web dependencies
cd apps/web
npm install
cd ../..
```

### Step 2: Set Up Supabase

1. **Create Supabase Project**:
   - Go to https://supabase.com
   - Create new project
   - Note your project URL and API keys

2. **Apply Database Migrations**:
   - In Supabase Dashboard → SQL Editor
   - Run migrations in order:
     ```sql
     -- Run 001_init.sql
     -- Run 002_indexes.sql
     -- Run 003_embeddings_hf.sql
     -- Run 004_fix_errors_default.sql
     ```

3. **Create Storage Bucket**:
   - Go to Storage → Create bucket
   - Name: `reports`
   - Set to **Private**
   - Enable service role write access

### Step 3: Configure Environment

Create `.env` file in project root:

```bash
# OpenAI (for LLM, optional if only using HF embeddings)
OPENAI_API_KEY=sk-proj-...

# Tavily (news search)
TAVILY_API_KEY=tvly-dev-...

# Alpha Vantage (market data)
ALPHAVANTAGE_API_KEY=DCO5EE2Z64PRWCUX

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DB_URL=postgresql://postgres:PASSWORD%40ENCODED@db.your-project.supabase.co:5432/postgres

# Embedding Provider (default: hf = local Hugging Face)
EMBED_PROVIDER=hf
HF_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
# HF_API_TOKEN=your-token  # Only if using hf_api provider

# HTTP Configuration
HTTP_TIMEOUT_SEC=40
NEWS_MAX_RESULTS=5
NEWS_SEARCH_DEPTH=basic

# Reporting
REPORT_BUCKET=reports
REPORT_PDF_ENABLED=false  # Set to true to enable PDF generation

# Optional: Observability
# SENTRY_DSN=your-sentry-dsn
```

**Important**: Percent-encode special characters in `SUPABASE_DB_URL` password:
- `@` → `%40`
- `#` → `%23`
- `%` → `%25`

Create `apps/web/.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_REPORT_BUCKET=reports
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 4: Start Servers

**Terminal 1 - API Server:**
```bash
set PYTHONPATH=.
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Web Server:**
```bash
cd apps/web
npm run dev
```

### Step 5: Access Application

- **API Docs**: http://localhost:8000/docs
- **Web Dashboard**: http://localhost:3000
- **Reports Viewer**: http://localhost:3000/reports

## 📖 Usage Guide

### Running an Analysis

**Via Web Dashboard:**
1. Go to http://localhost:3000/run
2. Enter tickers (comma-separated): `AAPL, MSFT, NVDA`
3. Set time window (hours): `24`
4. Click "Start Analysis"
5. Wait for completion (30-60 seconds)
6. View results in Reports page

**Via API:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "MSFT"], "hours": 24}'
```

**Via CLI:**
```bash
python scripts/run_once.py AAPL,MSFT,NVDA 24
```

### Viewing Reports

1. **List Reports**: http://localhost:3000/reports
2. **View Report**: Click "View Report" on any card
3. **Features**:
   - **Table of Contents**: Click items to scroll to sections
   - **Print**: Click Print button (or Ctrl+P) for A4 layout
   - **Download**: Click PDF/Markdown to download source
   - **Share**: Click Share to copy link or use Web Share API

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/run` | POST | Trigger analysis (sync) |
| `/runs/{id}` | GET | Get run status |
| `/reports` | GET | List reports (with `?date=` or `?path=` filters) |

## 🔧 Configuration

### Embedding Providers

Choose based on your needs:

| Provider | Config | Pros | Cons |
|----------|--------|------|------|
| **Hugging Face Local** (default) | `EMBED_PROVIDER=hf` | Fast, free, no API costs | Requires ~90MB model download |
| **OpenAI** | `EMBED_PROVIDER=openai` | High quality, 1536-dim | Requires API key, costs money |
| **HF Inference API** | `EMBED_PROVIDER=hf_api` | Serverless-friendly | Requires API token, network latency |

### HTTP Retries

Automatic retries with exponential backoff:
- **Tavily**: 3 attempts (2s, 4s, 8s delays)
- **Alpha Vantage**: 3 attempts + special 429 handling (15s delay)
- **Timeout**: Configurable via `HTTP_TIMEOUT_SEC` (default: 40s)

### PDF Generation

- **Enabled**: `REPORT_PDF_ENABLED=true` (requires WeasyPrint, GTK+ on Windows)
- **Disabled**: `REPORT_PDF_ENABLED=false` (default, Markdown only)

## 🗂️ Files to Keep

### Essential Files (DO NOT DELETE)

**Core Application:**
- `apps/api/main.py` - API server
- `apps/web/app/**/*.tsx` - Next.js pages
- `apps/web/components/**/*.tsx` - React components
- `apps/web/lib/**/*.tsx` - Utilities
- `agent/**/*.py` - Agent logic
- `memory/**/*.py` - Database integration
- `scripts/run_once.py` - CLI runner

**Configuration:**
- `pyproject.toml` - Python dependencies
- `apps/web/package.json` - Node dependencies
- `apps/web/tailwind.config.ts` - Tailwind config
- `apps/web/tsconfig.json` - TypeScript config
- `apps/web/next.config.js` - Next.js config

**Infrastructure:**
- `infra/migrations/*.sql` - Database migrations
- `infra/docker/*` - Dockerfiles
- `infra/compose.yaml` - Docker Compose

**Documentation:**
- `README.md` - This file
- `LICENSE` - License file
- `Makefile` - Build commands

**Tests:**
- `tests/**/*.py` - Test suite

### Files to Ignore (Auto-generated)

These are in `.gitignore` and should not be committed:

- `__pycache__/` - Python cache
- `node_modules/` - Node dependencies
- `.next/` - Next.js build
- `.env` - Environment variables (secrets)
- `*.log` - Log files
- `.pytest_cache/` - Test cache

### Files Already Deleted

- `FIX_*.md` - Temporary fix guides (issues resolved)
- `REPORT_VIEWER_SETUP.md` - Setup info (now in README)
- `START_SERVERS.md` - Server instructions (now in README)
- `*.png` - Screenshots (not needed)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_graph.py

# Run with coverage
pytest --cov=agent --cov=memory
```

## 🐳 Docker Deployment

```bash
# Build images
make docker-build

# Start services
make docker-up

# Stop services
make docker-down
```

## 🔧 Troubleshooting

### Build Errors

**"Cannot find module '@tailwindcss/typography'"**
```bash
cd apps/web
npm install
```

**"Expected '>', got 'href'" (JSX syntax error)**
- Ensure `mdx.tsx` uses `.tsx` extension (not `.ts`)
- Check that `remark-rehype` is in pipeline

### Runtime Errors

**"SUPABASE_URL must be set"**
- Verify `.env` file exists in project root
- Check that all required variables are set
- Ensure password in `SUPABASE_DB_URL` is percent-encoded

**"Could not find table 'embeddings_hf'"**
- Run migration `003_embeddings_hf.sql` in Supabase SQL Editor

**"'dict' object has no attribute 'errors'"**
- API code handles both dict and RunState (already fixed)
- Run migration `004_fix_errors_default.sql` to prevent NULL errors

**"OpenAI quota exceeded"**
- Runs continue even if embeddings fail (graceful degradation)
- Switch to `EMBED_PROVIDER=hf` for local embeddings

**Content not rendering / Clicks not working**
- Check browser console (F12) for errors
- Verify markdown is being fetched (Network tab)
- Ensure `remark-rehype` is in `mdx.tsx` pipeline

### Database Issues

**Connection fails**
- Verify `SUPABASE_DB_URL` password encoding (`@` → `%40`)
- Check Supabase project is active
- Verify network allows connections to Supabase

**Migrations fail**
- Run migrations in order: 001 → 002 → 003 → 004
- Check pgvector extension is enabled
- Verify service role key has proper permissions

## 📊 Tech Stack

### Backend
- **Python 3.11** - Runtime
- **LangGraph** - Agent orchestration
- **FastAPI** - REST API
- **OpenAI GPT-4o** - LLM
- **Hugging Face** - Local embeddings (default)
- **Supabase** - Database, storage, auth
- **pgvector** - Vector similarity search
- **httpx** - HTTP client with retries
- **structlog** - Structured logging

### Frontend
- **Next.js 14** - React framework (App Router)
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **21st.dev** - Futuristic components
- **remark/rehype** - Markdown processing
- **Shiki** - Syntax highlighting

### Infrastructure
- **Docker** - Containerization
- **PostgreSQL** - Database (via Supabase)
- **GitHub Actions** - CI/CD (optional)

## 📝 Environment Variables Reference

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `TAVILY_API_KEY` | Tavily API key | `tvly-dev-...` |
| `ALPHAVANTAGE_API_KEY` | Alpha Vantage API key | `DCO5EE2Z64PRWCUX` |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGciOiJIUzI1NiIs...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (backend only) | `eyJhbGciOiJIUzI1NiIs...` |
| `SUPABASE_DB_URL` | Database connection string | `postgresql://postgres:...` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Required for LLM, optional for embeddings |
| `EMBED_PROVIDER` | `hf` | `hf`, `openai`, or `hf_api` |
| `HF_EMBED_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Hugging Face model |
| `HTTP_TIMEOUT_SEC` | `40` | HTTP request timeout |
| `NEWS_MAX_RESULTS` | `5` | Max results per ticker |
| `NEWS_SEARCH_DEPTH` | `basic` | Tavily search depth |
| `REPORT_BUCKET` | `reports` | Storage bucket name |
| `REPORT_PDF_ENABLED` | `false` | Enable PDF generation |
| `SENTRY_DSN` | - | Sentry error tracking |

## 🎨 UI Features

### Report Viewer

- **3-Column Layout**: TOC (left) / Content (center) / Actions (right)
- **Responsive**: Stacks on mobile, full layout on desktop
- **Interactive TOC**: Click to scroll, highlights active section
- **Syntax Highlighting**: Code blocks with Shiki (GitHub Dark theme)
- **Print Styles**: Optimized A4 layout (no chrome)
- **Smooth Scrolling**: Animated scroll to sections
- **External Links**: Auto-detects and opens in new tab

### Dashboard

- **Neon Aesthetic**: Brand color `#00D1FF`, glassmorphism effects
- **Spotlight Background**: Interactive mouse-following glow
- **Grid Overlay**: Subtle neon grid pattern
- **Micro-interactions**: Hover effects, transitions
- **Live Status**: Real-time run status polling
- **Error Handling**: Friendly error messages with retry

## 📄 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check this README's Troubleshooting section
2. Review browser console for errors
3. Check API server logs for backend errors
4. Verify all environment variables are set correctly

---

**Built with ❤️ using LangGraph, Next.js, and Supabase**
