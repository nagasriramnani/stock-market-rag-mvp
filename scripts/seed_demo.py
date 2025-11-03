"""Seed demo data for testing."""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SB_URL = os.getenv("SUPABASE_URL")
SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SB_URL or not SB_KEY:
    print("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    sys.exit(1)

sb = create_client(SB_URL, SB_KEY)

# Create a demo run
run = sb.table("runs").insert({
    "tickers": ["AAPL", "MSFT"],
    "time_window_hours": 24,
    "status": "completed",
    "started_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
    "finished_at": datetime.utcnow().isoformat(),
    "notes": ["Demo run"],
}).execute()

print(f"Created demo run: {run.data[0]['id'] if run.data else 'N/A'}")

