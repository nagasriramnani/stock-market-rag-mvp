"""Smoke tests for LangGraph agent."""
import pytest
from agent.state import RunState
from agent.graph import app


def test_graph_runs_smoke():
    """Basic smoke test for agent graph execution."""
    state = RunState(tickers=["AAPL", "MSFT"], time_window_hours=24)
    
    # Note: This will make real API calls if keys are set
    # In CI, should mock or skip if keys not available
    try:
        result = app.invoke(state)
        assert isinstance(result.artifacts, list)
        assert isinstance(result.notes, list)
        assert isinstance(result.errors, list)
    except Exception as e:
        # If API keys aren't set, that's expected in CI
        if "not set" in str(e) or "API" in str(e):
            pytest.skip("API keys not configured")
        raise

