import os
from pathlib import Path
from datetime import datetime
import sys

os.environ.setdefault("APP_DB_PATH", str(Path("data")/"analysis.db"))

LOG = Path("runlog.txt")
with LOG.open("a", encoding="utf-8") as f:
    f.write(f"\n[{datetime.now().isoformat()}] Starting Dash...\n")
    f.flush()

try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from apps.dash.app import app
    app.run(debug=False, host="127.0.0.1", port=8050)
except Exception as e:
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"ERROR: {type(e).__name__}: {e}\n")
    raise
