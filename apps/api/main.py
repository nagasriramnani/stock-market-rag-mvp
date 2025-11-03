"""FastAPI main application."""
import os
import re
import traceback
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import logging
import structlog
from dotenv import load_dotenv
from supabase import create_client
from agent.graph import app as agent_app
from agent.state import RunState
from memory.kv_store import update_run_status, _get_supabase_client

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Optional Sentry initialization
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
        )
        logger = structlog.get_logger()
        logger.info("Sentry initialized")
    except ImportError:
        pass

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()

app = FastAPI(
    title="AI Stock Research Agent API",
    description="Autonomous stock research with multi-tool integration",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    tickers: List[str] = Field(..., min_length=1, max_length=10)
    hours: Optional[int] = Field(default=24, ge=1, le=168)
    
    @field_validator("tickers")
    @classmethod
    def validate_tickers(cls, v: List[str]) -> List[str]:
        """Validate ticker format: [A-Z.\-]{1,6}"""
        ticker_regex = re.compile(r"^[A-Z.\-]{1,6}$")
        for ticker in v:
            if not ticker_regex.match(ticker.upper()):
                raise ValueError(f"Invalid ticker format: {ticker}. Must be 1-6 characters, A-Z, dots, or hyphens.")
        return [t.upper() for t in v]


class RunResponse(BaseModel):
    run_id: str
    artifacts: List[str]
    notes: List[str]
    errors: List[str]


class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    started_at: Optional[str]
    finished_at: Optional[str]
    errors: List[str] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)


class ReportItem(BaseModel):
    path: str
    signed_url_md: Optional[str] = None
    signed_url_pdf: Optional[str] = None
    date: str
    tickers: List[str]


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-stock-agent-api"}


@app.post("/run", response_model=RunResponse)
async def run_agent(request: RunRequest, sync: bool = Query(default=True)):
    """
    Trigger agent run.
    
    Returns run_id immediately if sync=false (future async mode).
    Currently synchronous: runs to completion before returning.
    """
    logger.info("Starting agent run", tickers=request.tickers, hours=request.hours)

    try:
        state = RunState(
            tickers=request.tickers,
            time_window_hours=request.hours or 24,
        )

        # Invoke agent graph
        result = agent_app.invoke(state)

        # Handle both dict and RunState object (LangGraph may return either)
        if isinstance(result, dict):
            errors = result.get("errors", [])
            run_id = result.get("run_id", "")
            artifacts = result.get("artifacts", [])
            notes = result.get("notes", [])
        else:
            # RunState object
            errors = result.errors if hasattr(result, 'errors') else []
            run_id = result.run_id if hasattr(result, 'run_id') else ""
            artifacts = result.artifacts if hasattr(result, 'artifacts') else []
            notes = result.notes if hasattr(result, 'notes') else []

        # Update run status
        status = "completed" if not errors else "failed"
        update_run_status(run_id, status, errors)

        logger.info("Agent run completed", run_id=run_id, status=status, artifacts_count=len(artifacts))

        return RunResponse(
            run_id=run_id,
            artifacts=artifacts,
            notes=notes,
            errors=errors,
        )
    except Exception as e:
        error_msg = str(e)
        logger.error("Agent run failed", error=error_msg, tickers=request.tickers, exc_info=True)
        logger.error("Traceback", traceback=traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {error_msg}")


@app.get("/runs/{run_id}", response_model=RunStatusResponse)
async def get_run_status(run_id: str):
    """Get run status and details."""
    # Validate UUID format
    try:
        import uuid
        uuid.UUID(run_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid run_id format: {run_id}")
    
    try:
        sb = _get_supabase_client()
        result = sb.table("runs").select("*").eq("id", run_id).limit(1).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
        
        run = result.data[0]
        
        # Coalesce None to empty list for arrays (PostgREST returns null for empty arrays)
        errors = run.get("errors") or []
        if errors is None:
            errors = []
        
        # Get artifacts from reports table
        reports = sb.table("reports").select("supabase_path").eq("run_id", run_id).execute()
        artifacts = [r["supabase_path"] for r in (reports.data or [])]
        if artifacts is None:
            artifacts = []
        
        return RunStatusResponse(
            run_id=run["id"],
            status=run.get("status", "unknown"),
            started_at=run.get("started_at"),
            finished_at=run.get("finished_at"),
            errors=errors,
            artifacts=artifacts,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch run status", run_id=run_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch run status: {str(e)}")


@app.get("/reports", response_model=List[ReportItem])
async def list_reports(
    date: Optional[str] = Query(None, description="Filter by date YYYY-MM-DD"),
    path: Optional[str] = Query(None, description="Get specific report by path"),
):
    """
    List reports with signed URLs (server-side via service role).
    
    Uses Fix A: Lists from reports table (more reliable than walking storage folders).
    Can filter by date or get specific report by path.
    """
    try:
        sb = _get_supabase_client()
        bucket = os.getenv("REPORT_BUCKET", "reports")
        
        # Query reports table for report paths (more reliable than walking storage)
        query = sb.table("reports").select("supabase_path, date_utc, tickers, created_at").order("created_at", desc=True).limit(200)
        
        if path:
            # Get specific report by path
            query = query.eq("supabase_path", path).limit(1)
        elif date:
            # Filter by date_utc column
            query = query.eq("date_utc", date)
        
        result = query.execute()
        reports_data = result.data or []
        
        if not reports_data:
            return []
        
        # Generate signed URLs for each report
        report_items = []
        for report in reports_data:
            path_val = report.get("supabase_path", "")
            if not path_val:
                continue
            
            # Get date and tickers from database (more reliable than parsing path)
            folder_date = report.get("date_utc", "")
            if isinstance(folder_date, str):
                # If date_utc is a string, use it directly
                date_str = folder_date
            else:
                # If it's a date object, format it
                date_str = str(folder_date)
            
            # Get tickers from database column (already an array)
            tickers = report.get("tickers", [])
            if not isinstance(tickers, list):
                tickers = []
            
            # Generate signed URL for Markdown
            signed_md = None
            try:
                md_res = sb.storage.from_(bucket).create_signed_url(path_val, 3600)
                # Handle both response formats: {"signedURL": "..."} or {"data": {"signedUrl": "..."}}
                if isinstance(md_res, dict):
                    signed_md = md_res.get("signedURL") or md_res.get("data", {}).get("signedUrl")
            except Exception as e:
                logger.warning("Failed to create signed URL for MD", path=path_val, error=str(e))
            
            # Check for PDF version (same path but .pdf extension)
            pdf_path = path_val.replace(".md", ".pdf")
            signed_pdf = None
            try:
                # Try to create signed URL for PDF (may not exist)
                pdf_res = sb.storage.from_(bucket).create_signed_url(pdf_path, 3600)
                if isinstance(pdf_res, dict):
                    signed_pdf = pdf_res.get("signedURL") or pdf_res.get("data", {}).get("signedUrl")
            except Exception:
                # PDF doesn't exist, that's fine
                pass
            
            report_items.append(ReportItem(
                path=path_val,
                signed_url_md=signed_md,
                signed_url_pdf=signed_pdf,
                date=date_str,
                tickers=tickers,
            ))
        
        return report_items
    
    except Exception as e:
        logger.error("Failed to list reports", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

