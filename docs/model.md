- Predict task: next-day price direction (up/down classification)
- Feature set: daily returns, rolling volatility, RSI, MACD, volume trend
- Include calendar features: day-of-week, month, trading session flags
- Integrate 24-72 hour aggregated sentiment signals from news embeddings
- Experiment with gradient boosted trees and Vertex AutoML tabular
- Use walk-forward expanding window for training/validation splits
- Production gate: deploy when directional hit-rate ≥55% over last 3 windows
- Monitor precision/recall and calibration drift monthly
- Retain model registry entries with metadata and feature schema hash

