"""Pydantic state for LangGraph agent."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class Article(BaseModel):
    """News article model."""
    ticker: str
    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    sentiment: Optional[float] = None
    relevance: Optional[float] = None
    impact: Optional[float] = None
    raw: Optional[Dict[str, Any]] = None


class PriceSnapshot(BaseModel):
    """Price data snapshot."""
    ticker: str
    as_of: datetime
    open: Optional[float] = None
    close: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[float] = None
    d1_change: Optional[float] = None
    d5_change: Optional[float] = None
    vol_z: Optional[float] = None


class RunState(BaseModel):
    """State passed through LangGraph nodes."""
    tickers: List[str] = Field(default_factory=list)
    time_window_hours: int = 24
    articles: List[Article] = Field(default_factory=list)
    prices: List[PriceSnapshot] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
    run_id: Optional[str] = None

