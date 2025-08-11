"""
CI Integration Checks – Stripe + Supabase

Purpose: Minimal integration gating for secrets and external services.

Checks:
- Stripe: list customers (read-only) to validate API key
- Supabase: insert a health-check event in events table via REST API

Exit code != 0 on failure.
"""

from __future__ import annotations

import os
import sys
import json
from datetime import datetime
from typing import Any, Dict

import requests


def log(msg: str, **kwargs: Any) -> None:
    timestamp = datetime.utcnow().isoformat()
    if kwargs:
        print(json.dumps({"ts": timestamp, "msg": msg, **kwargs}))
    else:
        print(json.dumps({"ts": timestamp, "msg": msg}))


def check_stripe() -> None:
    import stripe  # type: ignore

    stripe_key = os.getenv("STRIPE_TEST_KEY") or os.getenv("STRIPE_SECRET_KEY")
    if not stripe_key:
        log("Stripe key not set; skipping Stripe check (treated as failure in strict mode)")
        raise RuntimeError("Missing STRIPE_TEST_KEY/STRIPE_SECRET_KEY")

    stripe.api_key = stripe_key
    # Read-only request
    customers = stripe.Customer.list(limit=1)
    count = len(customers.data) if hasattr(customers, "data") else 0
    log("Stripe check OK", customers_seen=count)


def check_supabase_events() -> None:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        log("Supabase env not set; failing" )
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")

    event_body: Dict[str, Any] = {
        "stream_id": "health_check_ci",
        "event_type": "HealthCheck",
        "payload": {"ci": True, "source": "ci_integration_checks"},
        "app_source": "ci",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"bridge_version": "v1", "published_at": datetime.utcnow().isoformat()},
    }

    resp = requests.post(
        f"{supabase_url}/rest/v1/events",
        headers={
            "Content-Type": "application/json",
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Prefer": "return=representation",
        },
        data=json.dumps(event_body),
        timeout=20,
    )

    if resp.status_code >= 300:
        log("Supabase publish failed", status=resp.status_code, body=resp.text)
        raise RuntimeError("Supabase publish failed")

    log("Supabase event insert OK")


def main() -> int:
    try:
        check_stripe()
        check_supabase_events()
        log("CI integration checks completed successfully")
        return 0
    except Exception as e:  # noqa: BLE001
        log("CI integration checks failed", error=str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())


