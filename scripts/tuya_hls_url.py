#!/usr/bin/env python3
"""Generate a temporary Tuya Cloud HLS/RTSP live-stream URL.

This script is intentionally credential-free in source control. Read secrets from
environment variables or from a local .env file loaded by the shell before calling
it. It prints only the resulting stream URL (or JSON with --json).

Required env:
  TUYA_CLIENT_ID
  TUYA_CLIENT_SECRET
  TUYA_DEVICE_ID

Optional env:
  TUYA_UID                  If set, use /users/{uid}/devices/{device_id}/...
  TUYA_ENDPOINT             Default: https://openapi.tuyaus.com
  TUYA_STREAM_TYPE          Default: hls. Valid Tuya values: hls or rtsp.
  TUYA_GRANT_TYPE           Default: 1 (simple mode)
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def load_local_env_file() -> None:
    """Load simple KEY=VALUE pairs from .env for standalone CLI use."""
    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


class TuyaError(RuntimeError):
    pass


@dataclass(frozen=True)
class TuyaConfig:
    endpoint: str
    client_id: str
    client_secret: str
    device_id: str
    uid: str | None
    stream_type: str
    grant_type: str
    timeout: int


def getenv_required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise TuyaError(f"Missing required environment variable: {name}")
    return value


def load_config(timeout: int) -> TuyaConfig:
    endpoint = os.environ.get("TUYA_ENDPOINT", "https://openapi.tuyaus.com").strip().rstrip("/")
    if not endpoint.startswith(("https://", "http://")):
        endpoint = f"https://{endpoint}"

    stream_type = os.environ.get("TUYA_STREAM_TYPE", "hls").strip().lower()
    if stream_type not in {"hls", "rtsp"}:
        raise TuyaError("TUYA_STREAM_TYPE must be hls or rtsp")

    return TuyaConfig(
        endpoint=endpoint,
        client_id=getenv_required("TUYA_CLIENT_ID"),
        client_secret=getenv_required("TUYA_CLIENT_SECRET"),
        device_id=getenv_required("TUYA_DEVICE_ID"),
        uid=os.environ.get("TUYA_UID", "").strip() or None,
        stream_type=stream_type,
        grant_type=os.environ.get("TUYA_GRANT_TYPE", "1").strip() or "1",
        timeout=timeout,
    )


def content_sha256(body: bytes | None) -> str:
    return hashlib.sha256(body or b"").hexdigest()


def canonical_url(path: str, query: dict[str, str] | None = None) -> str:
    if not query:
        return path
    return f"{path}?{urlencode(sorted(query.items()))}"


def sign(
    *,
    config: TuyaConfig,
    method: str,
    path: str,
    query: dict[str, str] | None,
    body: bytes | None,
    access_token: str | None = None,
    nonce: str | None = None,
    timestamp_ms: str | None = None,
) -> tuple[str, str, str]:
    """Return (signature, timestamp_ms, nonce) for Tuya Cloud auth."""
    nonce = nonce or uuid.uuid4().hex
    timestamp_ms = timestamp_ms or str(int(time.time() * 1000))
    url = canonical_url(path, query)
    string_to_sign = "\n".join([
        method.upper(),
        content_sha256(body),
        "",
        url,
    ])

    if access_token:
        raw = f"{config.client_id}{access_token}{timestamp_ms}{nonce}{string_to_sign}"
    else:
        raw = f"{config.client_id}{timestamp_ms}{nonce}{string_to_sign}"

    digest = hmac.new(
        config.client_secret.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()
    return digest, timestamp_ms, nonce


def request_json(
    config: TuyaConfig,
    method: str,
    path: str,
    *,
    query: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    access_token: str | None = None,
) -> dict[str, Any]:
    body = None
    if payload is not None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    signature, timestamp_ms, nonce = sign(
        config=config,
        method=method,
        path=path,
        query=query,
        body=body,
        access_token=access_token,
    )

    url = config.endpoint + canonical_url(path, query)
    headers = {
        "client_id": config.client_id,
        "sign": signature,
        "t": timestamp_ms,
        "nonce": nonce,
        "sign_method": "HMAC-SHA256",
        "Accept": "application/json",
    }
    if access_token:
        headers["access_token"] = access_token
    if body is not None:
        headers["Content-Type"] = "application/json"

    req = Request(url, data=body, headers=headers, method=method.upper())
    try:
        with urlopen(req, timeout=config.timeout) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:800]
        raise TuyaError(f"HTTP {exc.code} from Tuya API: {detail}") from exc
    except URLError as exc:
        raise TuyaError(f"Network error calling Tuya API: {exc.reason}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TuyaError(f"Tuya API returned non-JSON response: {raw[:300]}") from exc

    if not data.get("success", False):
        code = data.get("code", "unknown")
        msg = data.get("msg") or data.get("errorMsg") or data.get("message") or "Tuya API request failed"
        raise TuyaError(f"Tuya API error {code}: {msg}")

    return data


def get_access_token(config: TuyaConfig) -> str:
    data = request_json(
        config,
        "GET",
        "/v1.0/token",
        query={"grant_type": config.grant_type},
    )
    token = (data.get("result") or {}).get("access_token")
    if not token:
        raise TuyaError("Tuya token response did not include access_token")
    return token


def allocate_stream_url(config: TuyaConfig, access_token: str) -> str:
    if config.uid:
        path = f"/v1.0/users/{config.uid}/devices/{config.device_id}/stream/actions/allocate"
    else:
        path = f"/v1.0/devices/{config.device_id}/stream/actions/allocate"

    data = request_json(
        config,
        "POST",
        path,
        payload={"type": config.stream_type},
        access_token=access_token,
    )
    url = (data.get("result") or {}).get("url")
    if not url:
        raise TuyaError("Tuya stream allocation response did not include result.url")
    return url


def main() -> int:
    load_local_env_file()
    parser = argparse.ArgumentParser(description="Generate a temporary Tuya HLS/RTSP live-stream URL")
    parser.add_argument("--json", action="store_true", help="print JSON {status,url,type,endpoint}")
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("TUYA_TIMEOUT", "20")))
    args = parser.parse_args()

    try:
        config = load_config(args.timeout)
        token = get_access_token(config)
        stream_url = allocate_stream_url(config, token)
    except Exception as exc:
        if args.json:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        else:
            print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        host = urlparse(config.endpoint).netloc
        print(json.dumps({
            "status": "ok",
            "url": stream_url,
            "type": config.stream_type,
            "endpoint": host,
        }, ensure_ascii=False))
    else:
        print(stream_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
