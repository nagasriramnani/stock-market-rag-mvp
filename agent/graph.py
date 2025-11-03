"""LangGraph agent orchestration."""
from langgraph.graph import StateGraph, END
from agent.state import RunState
from agent.tools.tavily_client import fetch_news_for_tickers
from agent.tools.rss_client import fetch_rss_fallback
from agent.tools.alpha_vantage import fetch_prices_snapshot
from agent.analysis.dedupe import dedupe_by_url
from agent.analysis.nlp import score_articles
from agent.analysis.finance import score_impact
from agent.reporting.render import render_and_store_report
from memory.vector_store import upsert_embeddings_for_articles
from memory.kv_store import create_run, update_run_status
import structlog

logger = structlog.get_logger()


def plan(state: RunState) -> RunState:
    """Planning node."""
    state.notes.append("plan: fetch news & prices")
    if not state.run_id:
        state.run_id = create_run(state.tickers, state.time_window_hours)
    return state


def news(state: RunState) -> RunState:
    """Fetch news articles."""
    try:
        articles = fetch_news_for_tickers(state.tickers, state.time_window_hours, state.run_id)
        # Fallback to RSS if Tavily returns few results
        if len(articles) < 5:
            rss_articles = fetch_rss_fallback(state.tickers, state.time_window_hours)
            articles.extend(rss_articles)
        state.articles = dedupe_by_url(articles)
        state.notes.append(f"news: fetched {len(state.articles)} articles")
        logger.info("News fetch completed", count=len(state.articles), run_id=state.run_id)
    except Exception as e:
        error_msg = f"news error: {str(e)}"
        state.errors.append(error_msg)
        logger.error("News fetch failed", error=str(e), run_id=state.run_id, exc_info=True)
    return state


def prices(state: RunState) -> RunState:
    """Fetch price data."""
    try:
        state.prices = fetch_prices_snapshot(state.tickers, state.run_id)
        state.notes.append(f"prices: fetched {len(state.prices)} snapshots")
        logger.info("Price fetch completed", count=len(state.prices), run_id=state.run_id)
    except Exception as e:
        error_msg = f"prices error: {str(e)}"
        state.errors.append(error_msg)
        logger.error("Price fetch failed", error=str(e), run_id=state.run_id, exc_info=True)
    return state


def analyze(state: RunState) -> RunState:
    """Analyze articles."""
    try:
        state.articles = score_articles(state.articles, state.tickers)
        state.articles = score_impact(state.articles, state.prices)
        upsert_embeddings_for_articles(state.articles, state.run_id)
        state.notes.append(f"analyze: scored {len(state.articles)} articles")
        logger.info("Analysis completed", count=len(state.articles), run_id=state.run_id)
    except Exception as e:
        error_msg = f"analyze error: {str(e)}"
        state.errors.append(error_msg)
        logger.error("Analysis failed", error=str(e), run_id=state.run_id, exc_info=True)
    return state


def report(state: RunState) -> RunState:
    """Generate and store report."""
    try:
        path = render_and_store_report(state)
        state.artifacts.append(path)
        state.notes.append(f"report: generated {path}")
    except Exception as e:
        error_msg = f"report error: {str(e)}"
        state.errors.append(error_msg)
        logger.error("Report generation failed", error=str(e))
        # Don't fail the whole run if report generation fails
        # Continue anyway - articles and prices are already collected
    return state


# Build graph
graph = StateGraph(RunState)
graph.add_node("plan", plan)
graph.add_node("news", news)
graph.add_node("prices", prices)
graph.add_node("analyze", analyze)
graph.add_node("report", report)

graph.set_entry_point("plan")
graph.add_edge("plan", "news")
graph.add_edge("news", "prices")
graph.add_edge("prices", "analyze")
graph.add_edge("analyze", "report")
graph.add_edge("report", END)

app = graph.compile()

