"""Run concise HTTP smoke checks against a deployed or local backend."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ENDPOINTS = (
    "/health",
    "/health/db",
    "/api/v1/reference",
    "/api/v1/sites/options",
)


@dataclass(frozen=True)
class SmokeResult:
    """Result for one smoke-test endpoint."""

    endpoint: str
    status: int | None
    ok: bool
    summary: str


def normalize_base_url(base_url: str) -> str:
    """Return a base URL without a trailing slash."""

    cleaned = base_url.strip().rstrip("/")
    if not cleaned:
        raise ValueError("--base-url must not be empty")
    if not cleaned.startswith(("http://", "https://")):
        raise ValueError("--base-url must start with http:// or https://")
    return cleaned


def summarize_payload(payload: bytes) -> str:
    """Return a short, non-secret summary of a JSON response."""

    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return f"bytes={len(payload)}"
    if isinstance(data, list):
        return f"items={len(data)}"
    if isinstance(data, dict):
        keys = ",".join(sorted(str(key) for key in data.keys()))
        return f"keys={keys}"
    return f"type={type(data).__name__}"


def check_endpoint(base_url: str, endpoint: str, timeout: float) -> SmokeResult:
    """Call one endpoint and return a concise pass/fail result."""

    url = f"{base_url}{endpoint}"
    request = Request(url, headers={"User-Agent": "nbs-backend-smoke-test"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
            status = response.status
    except HTTPError as exc:
        payload = exc.read()
        return SmokeResult(endpoint, exc.code, False, summarize_payload(payload))
    except URLError as exc:
        return SmokeResult(endpoint, None, False, str(exc.reason))
    except TimeoutError:
        return SmokeResult(endpoint, None, False, "request timed out")
    return SmokeResult(endpoint, status, status == 200, summarize_payload(payload))


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Backend base URL")
    parser.add_argument("--timeout", type=float, default=15.0, help="Seconds per request")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run all smoke checks and return a process exit code."""

    args = parse_args(argv or sys.argv[1:])
    try:
        base_url = normalize_base_url(args.base_url)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    results = [check_endpoint(base_url, endpoint, args.timeout) for endpoint in ENDPOINTS]
    for result in results:
        status = result.status if result.status is not None else "no-status"
        label = "PASS" if result.ok else "FAIL"
        print(f"{label} {result.endpoint} status={status} {result.summary}")

    if all(result.ok for result in results):
        print("PASS backend smoke test")
        return 0
    print("FAIL backend smoke test", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
