"""KV store for run lifecycle."""
import os
import uuid
import structlog
from datetime import datetime
from typing import Optional
from supabase import create_client

logger = structlog.get_logger()

# Export for use in API
def _get_supabase_client():
    """Lazy initialization of Supabase client."""
    SB_URL = os.getenv("SUPABASE_URL")
    SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not SB_URL or not SB_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    
    return create_client(SB_URL, SB_KEY)


def create_run(tickers: list[str], time_window_hours: int) -> str:
    """Create a new run record and return run_id."""
    sb = _get_supabase_client()
    run_id = str(uuid.uuid4())
    result = sb.table("runs").insert({
        "id": run_id,
        "tickers": tickers,
        "time_window_hours": time_window_hours,
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
    }).execute()
    logger.info("Created run", run_id=run_id, tickers=tickers)
    return run_id


def update_run_status(run_id: str, status: str, errors: Optional[list[str]] = None):
    """Update run status."""
    sb = _get_supabase_client()
    update_data = {"status": status}
    if status in ("completed", "failed"):
        update_data["finished_at"] = datetime.utcnow().isoformat()
    if errors:
        update_data["errors"] = errors

    sb.table("runs").update(update_data).eq("id", run_id).execute()
    logger.info("Updated run status", run_id=run_id, status=status)

