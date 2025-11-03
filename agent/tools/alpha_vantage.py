"""Alpha Vantage API client for market data with retries and timeouts."""
import os
import time
import httpx
import structlog
from typing import List, Optional
from datetime import datetime
from agent.state import PriceSnapshot

logger = structlog.get_logger()

_timeout = float(os.getenv("HTTP_TIMEOUT_SEC", "40"))


def _retry_request(func, max_attempts=3, run_id=None, is_rate_limit=False):
    """Retry HTTP request with exponential backoff. Special handling for 429."""
    delays = [2, 4, 8]
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limit: wait longer, one retry
                if attempt == 0:
                    logger.warning("Rate limit hit (429), backing off", ticker=e.request.url.params.get("symbol", ""), run_id=run_id)
                    time.sleep(15)
                    continue
                last_error = e
                break
            last_error = e
            if attempt < max_attempts - 1:
                delay = delays[attempt]
                logger.warning("HTTP request failed, retrying", attempt=attempt + 1, delay=delay, status=e.response.status_code, run_id=run_id)
                time.sleep(delay)
            else:
                logger.error("HTTP request failed after retries", status=e.response.status_code, error=str(e), run_id=run_id)
        except (httpx.HTTPError, httpx.ReadTimeout) as e:
            last_error = e
            if attempt < max_attempts - 1:
                delay = delays[attempt]
                logger.warning("HTTP timeout/error, retrying", attempt=attempt + 1, delay=delay, error=str(e)[:100], run_id=run_id)
                time.sleep(delay)
            else:
                logger.error("HTTP request failed after retries", error=str(e), run_id=run_id)
        except Exception as e:
            logger.error("Unexpected error in HTTP request", error=str(e), run_id=run_id)
            raise
    
    if last_error:
        raise last_error


def fetch_prices_snapshot(tickers: List[str], run_id: str = None) -> List[PriceSnapshot]:
    """Fetch current price data for tickers from Alpha Vantage with retries."""
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        logger.warning("ALPHAVANTAGE_API_KEY not set, returning empty prices", run_id=run_id)
        return []

    prices = []
    as_of = datetime.utcnow()

    with httpx.Client(timeout=_timeout) as client:
        for ticker in tickers:
            try:
                def _make_request():
                    return client.get(
                        "https://www.alphavantage.co/query",
                        params={
                            "function": "GLOBAL_QUOTE",
                            "symbol": ticker,
                            "apikey": api_key,
                        },
                    )
                
                response = _retry_request(_make_request, run_id=run_id)
                response.raise_for_status()
                data = response.json()

                quote = data.get("Global Quote", {})
                if not quote:
                    logger.warning("No quote data", ticker=ticker)
                    continue

                try:
                    close = float(quote.get("05. price", 0))
                    open_price = float(quote.get("02. open", close))
                    high = float(quote.get("03. high", close))
                    low = float(quote.get("04. low", close))
                    volume = float(quote.get("06. volume", 0))
                    prev_close = float(quote.get("08. previous close", close))

                    d1_change = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0

                    # For d5_change and vol_z, we'd need historical data
                    # Stub for now - can be enhanced with TIME_SERIES_DAILY
                    snapshot = PriceSnapshot(
                        ticker=ticker,
                        as_of=as_of,
                        open=open_price,
                        close=close,
                        high=high,
                        low=low,
                        volume=volume,
                        d1_change=d1_change,
                        d5_change=None,
                        vol_z=None,
                    )
                    prices.append(snapshot)
                    logger.info("Fetched price", ticker=ticker, close=close, run_id=run_id)
                except (ValueError, KeyError) as e:
                    logger.warning("Failed to parse quote", ticker=ticker, error=str(e), run_id=run_id)
                    continue

                # Rate limit: free tier is 5 calls/min
                time.sleep(12)  # Conservative delay

            except Exception as e:
                logger.error("Alpha Vantage API error", ticker=ticker, error=str(e), run_id=run_id)
                continue

    return prices

