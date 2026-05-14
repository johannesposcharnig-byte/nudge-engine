#!/usr/bin/env python3
"""Smoke-test the local Nudge Engine API."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "http://127.0.0.1:8765"
DEFAULT_FIXTURE = Path("tests/fixtures/api_activation_payload.json")


def _request_json(url: str, *, payload: dict | None = None) -> tuple[int, dict]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urlopen(request, timeout=10) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _load_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_smoke_test(base_url: str, fixture_path: Path) -> int:
    try:
        health_status, health = _request_json(f"{base_url.rstrip('/')}/health")
    except URLError:
        print("API is not reachable. Start it with: python3 -m src.api", file=sys.stderr)
        return 2

    if health_status != 200 or health.get("status") != "ok":
        print(f"Healthcheck failed: {health}", file=sys.stderr)
        return 1

    payload = _load_fixture(fixture_path)
    try:
        analyze_status, report = _request_json(f"{base_url.rstrip('/')}/analyze", payload=payload)
    except HTTPError as error:
        body = error.read().decode("utf-8")
        print(f"Analyze request failed with HTTP {error.code}: {body}", file=sys.stderr)
        return 1

    required = ["executive_summary", "result_quality", "audit_lineage", "nudge_recommendations"]
    missing = [key for key in required if key not in report]
    if analyze_status != 200 or missing:
        print(f"Analyze response incomplete. status={analyze_status}, missing={missing}", file=sys.stderr)
        return 1

    quality = report["result_quality"]
    lineage = report["audit_lineage"]
    print("Local API smoke test OK")
    print(f"- status: {report['executive_summary'].get('status')}")
    print(f"- decision_state: {quality.get('decision_state', {}).get('state')}")
    print(f"- pilot_readiness: {quality.get('pilot_readiness')}")
    print(f"- audit_run_id: {lineage.get('run_id')}")
    print(f"- nudges_returned: {len(report.get('nudge_recommendations', []))}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the local Nudge Engine API.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    args = parser.parse_args()
    return run_smoke_test(args.base_url, args.fixture)


if __name__ == "__main__":
    raise SystemExit(main())
