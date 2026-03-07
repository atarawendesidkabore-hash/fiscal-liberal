"""Audit trail helper for fiscal actions (RGPD traceability baseline)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_FILE = Path(__file__).resolve().parents[2] / "data" / "audit_log.ndjson"


async def audit_log(**payload: Any) -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=True) + "\n")

