from __future__ import annotations

from datetime import UTC, datetime
from random import Random


def trigger_quality_check(pipeline_name: str = "daily_customer_snapshot") -> str:
    """
    Example agentic action:
    simulates triggering a data quality run and returns a concise report.
    """
    rng = Random(42)
    null_rate = round(rng.uniform(0.0, 0.03), 4)
    dup_rate = round(rng.uniform(0.0, 0.01), 4)
    status = "PASS" if null_rate < 0.02 and dup_rate < 0.008 else "WARN"
    timestamp = datetime.now(UTC).isoformat()
    return (
        f"Quality check for `{pipeline_name}` at {timestamp}: {status}. "
        f"null_rate={null_rate}, duplicate_rate={dup_rate}. "
        "Action: investigate upstream source if WARN persists."
    )
