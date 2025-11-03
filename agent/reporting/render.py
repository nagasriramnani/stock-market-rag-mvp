"""Render Markdown report and upload to Supabase Storage."""
import os
import io
import structlog
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
from supabase import create_client
from agent.state import RunState

# Optional PDF generation
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    # OSError occurs when WeasyPrint can't load system libraries (GTK+ on Windows)
    WEASYPRINT_AVAILABLE = False

logger = structlog.get_logger()

# Template environment
_template_dir = os.path.join(os.path.dirname(__file__))
env = Environment(loader=FileSystemLoader(searchpath=_template_dir))


def _get_supabase_client():
    """Lazy initialization of Supabase client."""
    SB_URL = os.getenv("SUPABASE_URL")
    SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not SB_URL:
        raise ValueError("SUPABASE_URL must be set in environment variables")
    if not SB_KEY:
        raise ValueError("SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY must be set in environment variables")
    
    return create_client(SB_URL, SB_KEY)


def render_and_store_report(state: RunState) -> str:
    """Render Markdown, convert to PDF, upload both to Supabase Storage."""
    sb = _get_supabase_client()
    BUCKET = os.getenv("REPORT_BUCKET", "reports")
    pdf_enabled = os.getenv("REPORT_PDF_ENABLED", "false").lower() == "true"
    
    date_str = datetime.utcnow().date().isoformat()

    # Sort articles by impact
    sorted_articles = sorted(
        state.articles,
        key=lambda a: a.impact or 0.0,
        reverse=True
    )[:20]  # Limit to top 20

    # Render Markdown
    try:
        md = env.get_template("template.md.j2").render(
            date=date_str,
            tickers=state.tickers,
            time_window_hours=state.time_window_hours,
            items=sorted_articles,
            prices=state.prices,
        )
    except Exception as e:
        logger.error("Template rendering failed", error=str(e), run_id=state.run_id, exc_info=True)
        raise

    # Upload Markdown first (always succeeds even if PDF fails)
    base_path = f"{date_str}/report_{'_'.join(sorted(state.tickers))}"
    md_path = f"{base_path}.md"
    
    try:
        sb.storage.from_(BUCKET).upload(
            md_path,
            md.encode('utf-8'),
            file_options={"content-type": "text/markdown", "upsert": "true"}
        )
        logger.info("Uploaded Markdown report", path=md_path, run_id=state.run_id)
        
        # Save report metadata to reports table
        try:
            sb.table("reports").insert({
                "run_id": state.run_id,
                "date_utc": date_str,
                "tickers": state.tickers,
                "supabase_path": md_path,
            }).execute()
            logger.info("Saved report metadata to database", path=md_path, run_id=state.run_id)
        except Exception as e:
            # Log but don't fail - report is already uploaded to storage
            logger.warning("Failed to save report metadata", path=md_path, error=str(e), run_id=state.run_id)
    except Exception as e:
        logger.error("Failed to upload Markdown", error=str(e), path=md_path, run_id=state.run_id)
        raise

    # Generate PDF only if enabled and WeasyPrint available
    pdf_bytes = None
    if pdf_enabled and WEASYPRINT_AVAILABLE:
        try:
            # Convert to HTML for PDF
            html_content = markdown(md, extensions=['extra', 'codehilite'])
            html_full = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; padding: 2rem; line-height: 1.6; }}
        h1 {{ color: #00D1FF; }}
        h2 {{ margin-top: 2rem; }}
        a {{ color: #00D1FF; }}
        code {{ background: #f5f5f5; padding: 0.2rem 0.4rem; border-radius: 0.25rem; }}
        pre {{ background: #f5f5f5; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }}
    </style>
</head>
<body class="dark">
{html_content}
</body>
</html>"""
            pdf_bytes = HTML(string=html_full).write_pdf()
            logger.info("Generated PDF", run_id=state.run_id)
        except Exception as e:
            logger.warning("PDF generation failed, continuing with Markdown only", error=str(e), run_id=state.run_id)
            pdf_bytes = None
    elif not pdf_enabled:
        logger.info("PDF generation disabled via REPORT_PDF_ENABLED=false", run_id=state.run_id)

    # Upload PDF if generated
    if pdf_bytes:
        pdf_path = f"{base_path}.pdf"
        try:
            sb.storage.from_(BUCKET).upload(
                pdf_path,
                pdf_bytes,
                file_options={"content-type": "application/pdf", "upsert": "true"}
            )
            logger.info("Uploaded PDF report", path=pdf_path, run_id=state.run_id)
        except Exception as e:
            logger.warning("Failed to upload PDF", error=str(e), path=pdf_path, run_id=state.run_id)

    return f"{BUCKET}/{md_path}"

