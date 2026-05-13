#!/usr/bin/env python3
"""Crea un backup timestamped de evaluaciones.db."""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_DIR / "evaluaciones.db"
BACKUP_DIR = PROJECT_DIR / "backups"


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"No existe {DB_PATH}; inicializa la base primero.")
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = BACKUP_DIR / f"evaluaciones-{stamp}.db"
    shutil.copy2(DB_PATH, target)
    print(f"backup_created={target}")


if __name__ == "__main__":
    main()
