# Author: MilanWoj
import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

HOST_METRICS_FILE = Path(settings.host_metrics_path)
STALE_AFTER_SECONDS = 15


def get_host_metrics() -> dict:
    if not HOST_METRICS_FILE.exists():
        return {"available": False, "reason": "metrics_writer.sh not running"}

    try:
        data = json.loads(HOST_METRICS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"available": False, "reason": "metrics file unreadable"}

    try:
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        age_seconds = (datetime.now(timezone.utc) - updated_at).total_seconds()
    except (KeyError, ValueError):
        return {"available": False, "reason": "missing or invalid timestamp"}

    if age_seconds > STALE_AFTER_SECONDS:
        return {"available": False, "reason": f"stale ({age_seconds:.0f}s old)"}

    return {"available": True, **data}
