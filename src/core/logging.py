import json
import os
from datetime import datetime, timezone


def log_event(report_dir: str, event_type: str, payload: dict) -> None:
    os.makedirs(report_dir, exist_ok=True)
    path = os.path.join(report_dir, "audit_log.jsonl")
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    record = {
        "timestamp": timestamp,
        "event_type": event_type,
        "payload": payload,
    }
    with open(path, "a", encoding="ascii") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")
