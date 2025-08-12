#!/usr/bin/env python3
"""
Quick E2E verifier: Vercel (site) → Railway (APIs)

Checks:
- Fetch site, read CSP header, verify connect-src includes API hosts
- CORS preflight (OPTIONS) from site origin to Iris endpoint
- Health checks for Aube and Iris APIs

Usage:
  python infrastructure/testing/verify_vercel_to_railway.py \
    --site https://<vercel-site>.vercel.app \
    --iris https://<iris>.up.railway.app/api/v1/chat \
    --aube_api https://<aube>.up.railway.app
"""

import argparse
import sys
from urllib.parse import urlparse
import requests


def get_origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def fetch_csp(site_url: str) -> str:
    try:
        resp = requests.get(site_url, timeout=10)
        resp.raise_for_status()
        return resp.headers.get("Content-Security-Policy", "")
    except Exception as e:
        print(f"[CSP] ERROR fetching site: {e}")
        return ""


def csp_allows(csp: str, host_origin: str) -> bool:
    if not csp:
        # If no CSP header, it's not blocking
        return True
    # naive check: ensure host_origin appears in connect-src directive
    try:
        directives = {d.split(" ", 1)[0]: d for d in csp.split(";") if d.strip()}
        connect = directives.get("connect-src", "")
        return host_origin in connect
    except Exception:
        return host_origin in csp


def cors_preflight(origin: str, endpoint: str) -> (int, dict):
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,authorization",
    }
    # Most CORS middlewares accept OPTIONS on the same endpoint
    resp = requests.options(endpoint, headers=headers, timeout=10)
    return resp.status_code, dict(resp.headers)


def health(url: str) -> (int, str):
    resp = requests.get(url, timeout=10)
    return resp.status_code, resp.text[:200]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--iris", required=True)
    parser.add_argument("--aube_api", required=False)
    args = parser.parse_args()

    site = args.site.rstrip("/")
    iris = args.iris.rstrip("/")
    aube_api = args.aube_api.rstrip("/") if args.aube_api else None

    site_origin = get_origin(site)
    iris_origin = get_origin(iris)

    print(f"Site: {site}")
    print(f"Iris endpoint: {iris}")
    if aube_api:
        print(f"Aube API: {aube_api}")
    print("---")

    # 1) CSP
    csp = fetch_csp(site)
    if csp:
        print(f"[CSP] {csp}")
    else:
        print("[CSP] No CSP header or fetch error")
    csp_ok = csp_allows(csp, iris_origin)
    print(f"[CSP] connect-src allows {iris_origin}: {csp_ok}")
    if aube_api:
        aube_origin = get_origin(aube_api)
        csp_ok_aube = csp_allows(csp, aube_origin)
        print(f"[CSP] connect-src allows {aube_origin}: {csp_ok_aube}")

    # 2) Preflight CORS
    try:
        code, hdrs = cors_preflight(site_origin, iris)
        print(f"[CORS] Preflight to Iris status: {code}")
        print(f"[CORS] Response headers: { {k.lower(): v for k, v in hdrs.items()} }")
    except Exception as e:
        print(f"[CORS] ERROR preflight: {e}")

    # 3) Health checks
    try:
        iris_health_code, iris_health_body = health(get_origin(iris) + "/health")
        print(f"[HEALTH] Iris: {iris_health_code} body: {iris_health_body}")
    except Exception as e:
        print(f"[HEALTH] Iris ERROR: {e}")

    if aube_api:
        try:
            aube_health_code, aube_health_body = health(aube_api + "/health")
            print(f"[HEALTH] Aube: {aube_health_code} body: {aube_health_body}")
        except Exception as e:
            print(f"[HEALTH] Aube ERROR: {e}")

    # Exit code hint
    ok = True
    ok = ok and csp_ok
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()


