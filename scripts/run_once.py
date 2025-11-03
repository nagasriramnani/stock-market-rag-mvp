"""CLI script to run agent once."""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from agent.graph import app
from agent.state import RunState

load_dotenv()


def main():
    """Run agent with CLI arguments."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_once.py TICKER1,TICKER2 [hours]")
        sys.exit(1)

    tickers = [t.strip().upper() for t in sys.argv[1].split(",")]
    hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24

    print(f"Running agent for {tickers} (last {hours} hours)")
    print("This may take 30-60 seconds...\n")

    try:
        state = RunState(tickers=tickers, time_window_hours=hours)
        result = app.invoke(state)

        print(f"\n✅ Run completed!")
        print(f"Run ID: {result.run_id}")
        print(f"Articles found: {len(result.articles)}")
        print(f"Artifacts: {result.artifacts}")
        if result.notes:
            print(f"\nNotes:")
            for note in result.notes:
                print(f"  - {note}")
        if result.errors:
            print(f"\n⚠️  Errors:")
            for error in result.errors:
                print(f"  - {error}")
    except KeyboardInterrupt:
        print("\n❌ Run cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Run failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

