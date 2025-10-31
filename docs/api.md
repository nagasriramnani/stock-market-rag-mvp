- POST /predict returns {direction_prob, predicted_label, features_used}
- POST /ask-rag returns {answer, citations[]} with optional followup prompts
- GET /healthz reports service readiness and dependency checks
- GET /metrics exposes Prometheus counters, latency histograms, error rates
- Auth handled via Google IAM or API keys stored in Secret Manager
- Request payload validation with Pydantic schemas and 32KB max size
- Rate limiting per API key (e.g., 60 requests/minute baseline)
- Log structured JSON with trace_id, ticker, latency, status_code
- Include correlation ids to link prediction and RAG responses

