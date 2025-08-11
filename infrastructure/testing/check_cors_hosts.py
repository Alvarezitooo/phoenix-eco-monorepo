"""
Quick checks for CORS/Hosts configuration.

Usage:
  python infrastructure/testing/check_cors_hosts.py --site https://phoenix-eco-monorepo.vercel.app \
    --aube https://aube.example.com --iris https://iris.example.com
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, Any

import requests


def check_health(base_url: str) -> Dict[str, Any]:
    try:
        r = requests.get(f"{base_url.rstrip('/')}/health", timeout=10)
        return {"url": base_url, "status": r.status_code, "ok": r.ok}
    except Exception as e:  # noqa: BLE001
        return {"url": base_url, "error": str(e), "ok": False}


def check_cors_preflight(api_base: str, site_origin: str, path: str = "/") -> Dict[str, Any]:
    try:
        url = f"{api_base.rstrip('/')}{path}"
        headers = {
            "Origin": site_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        }
        r = requests.options(url, headers=headers, timeout=10)
        allowed_origin = r.headers.get("access-control-allow-origin")
        return {
            "url": url,
            "status": r.status_code,
            "allowed_origin": allowed_origin,
            "cors_ok": allowed_origin in ("*", site_origin),
        }
    except Exception as e:  # noqa: BLE001
        return {"url": api_base, "error": str(e), "cors_ok": False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, help="Site origin, e.g. https://phoenix-eco-monorepo.vercel.app")
    parser.add_argument("--aube", required=False, help="Aube API base URL")
    parser.add_argument("--iris", required=False, help="Iris API base URL")
    args = parser.parse_args()

    report: Dict[str, Any] = {"site": args.site, "checks": []}

    if args.aube:
        report["checks"].append({"aube_health": check_health(args.aube)})
        report["checks"].append({"aube_cors": check_cors_preflight(args.aube, args.site, "/api/v1/analyze/job-resilience")})
    if args.iris:
        report["checks"].append({"iris_health": check_health(args.iris)})
        report["checks"].append({"iris_cors": check_cors_preflight(args.iris, args.site, "/")})

    print(json.dumps(report, indent=2, ensure_ascii=False))
    # non-zero exit if any cors_ok false where check exists
    for entry in report["checks"]:
        for _, val in entry.items():
            if isinstance(val, dict) and ("cors_ok" in val) and not val.get("cors_ok", False):
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
