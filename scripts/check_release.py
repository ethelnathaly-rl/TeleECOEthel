#!/usr/bin/env python3
"""Verificación mínima antes de publicar TeleECOE en GitHub."""
from __future__ import annotations

import os
import py_compile
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
FORBIDDEN_TRACKED_NAMES = {".env", "go2rtc.yaml", "evaluaciones.db"}
FORBIDDEN_DIRS = {".git", ".venv", ".venv-linux", "venv", "env", "__pycache__", "logs", "backups", "tools", "artifacts", "downloads"}
SKIP_LOCAL_FILES = {
    ".env",
    "go2rtc.yaml",
    "go2rtc.yaml.backup-webrtc-lan-1778540806",
    "go2rtc.yaml.before-new-device",
    "evaluaciones.db",
    "go2rtc.exe",
    "test_video.mp4",
}
SECRET_PATTERNS = [
    re.compile(r"TUYA_CLIENT_SECRET\s*=\s*[^\s#]+", re.I),
    re.compile(r"password=[^\s]+", re.I),
    re.compile(r"SECRET_KEY\s*=\s*(?!cambiar|teleecoe-local-dev-change-me)[^\s#]+", re.I),
]
TEXT_EXTS = {".py", ".md", ".txt", ".yaml", ".yml", ".example", ".sh", ".ps1", ".bat", ".toml", ".cfg"}


def iter_files():
    for path in PROJECT_DIR.rglob("*"):
        rel = path.relative_to(PROJECT_DIR)
        if any(part in FORBIDDEN_DIRS for part in rel.parts):
            continue
        if path.is_file() and path.name not in SKIP_LOCAL_FILES:
            if any(path.name.startswith(prefix) for prefix in ("go2rtc.yaml.",)):
                continue
            yield path


def main() -> None:
    errors: list[str] = []

    for name in FORBIDDEN_TRACKED_NAMES:
        if (PROJECT_DIR / name).exists():
            # Local existence is expected; Git ignore must protect it. Warn only.
            print(f"local_sensitive_exists={name} (debe estar ignorado por Git)")

    for path in [PROJECT_DIR / "run.py", PROJECT_DIR / "app" / "__init__.py"]:
        py_compile.compile(str(path), doraise=True)
    for path in (PROJECT_DIR / "app").rglob("*.py"):
        py_compile.compile(str(path), doraise=True)
    for path in (PROJECT_DIR / "scripts").rglob("*.py"):
        py_compile.compile(str(path), doraise=True)
    print("python_compile_ok=true")

    for path in iter_files():
        if path.suffix.lower() not in TEXT_EXTS and not path.name.endswith(".example"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            sample = match.group(0)
            # Permitir placeholders documentados, nunca valores reales.
            if path.name in {".env.example", "go2rtc.example.yaml", "check_release.py"}:
                continue
            if any(token in sample for token in ["<password>", "TU_PASSWORD", "TUYA_CLIENT_SECRET=", "cambiar-"]):
                continue
            errors.append(f"possible_secret={path.relative_to(PROJECT_DIR)}:{sample[:80]}")

    required = ["README.md", "LICENSE", ".env.example", "go2rtc.example.yaml", "install.sh", "install.ps1", "start.sh", "start.ps1"]
    for name in required:
        if not (PROJECT_DIR / name).exists():
            errors.append(f"missing_required={name}")

    if errors:
        for e in errors:
            print(e)
        raise SystemExit(1)

    print("release_check_ok=true")


if __name__ == "__main__":
    main()
