- Primary logs: Cloud Run stdout/stderr, Vertex pipelines, scheduler jobs
- Monitor error rate thresholds per service (<2% 5m rolling window)
- Track ingestion scheduler success/failure counts and retries
- Alerts when p95 latency exceeds 500ms during low traffic periods
- Establish on-call rotation with PagerDuty or Google Chat alerts
- Capture RAG retrieval misses and fallback rates for diagnostics
- Maintain runbooks for ingestion failures and model drift incidents
- Weekly review of cost reports and quota consumption
- Backup embeddings and configs to versioned Cloud Storage folders

