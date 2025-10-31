- Tickers to target first: AAPL, MSFT, AMZN, TSLA, NVDA
- Price schema columns: date, open, high, low, close, volume, ticker
- News schema columns: published_at, source, title, url, summary, sentiment, tickers
- Source price data from Vertex AI Feature Store or BigQuery external table
- Ingest news via RSS/APIs with daily pull cadence and deduping
- Store price parquet files under gs://<your-bucket>/prices/
- Store news parquet or JSONL under gs://<your-bucket>/news/
- Ensure consistent timezone normalization to UTC before ingest

