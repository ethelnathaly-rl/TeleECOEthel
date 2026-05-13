#!/usr/bin/env python3
"""Migración segura para agregar exámenes/convocatorias a TeleECOE.

- Crea backup de evaluaciones.db antes de tocar datos.
- Crea tablas examen y examen_alumno si no existen.
- Agrega columnas examen_id, fecha_evaluacion y updated_at a evaluacion.
- Crea un examen inicial y asocia evaluaciones/alumnos actuales.
"""
from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_DIR / "evaluaciones.db"
BACKUP_DIR = PROJECT_DIR / "backups"


def columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row is not None


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"No existe la base de datos: {DB_PATH}")

    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"evaluaciones-before-examenes-{stamp}.db"
    shutil.copy2(DB_PATH, backup_path)
    print(f"backup_created={backup_path}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        conn.execute("BEGIN")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS examen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                estado VARCHAR(20) NOT NULL DEFAULT 'activo',
                fecha_inicio DATETIME NOT NULL,
                fecha_cierre DATETIME,
                created_at DATETIME NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS examen_alumno (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                examen_id INTEGER NOT NULL,
                alumno_id INTEGER NOT NULL,
                estado VARCHAR(30) NOT NULL DEFAULT 'pendiente',
                fecha_inscripcion DATETIME NOT NULL,
                observaciones TEXT,
                CONSTRAINT uq_examen_alumno UNIQUE (examen_id, alumno_id),
                FOREIGN KEY(examen_id) REFERENCES examen(id),
                FOREIGN KEY(alumno_id) REFERENCES alumno(id)
            )
            """
        )

        eval_cols = columns(conn, "evaluacion")
        if "examen_id" not in eval_cols:
            conn.execute("ALTER TABLE evaluacion ADD COLUMN examen_id INTEGER")
            print("added_column=evaluacion.examen_id")
        if "fecha_evaluacion" not in eval_cols:
            conn.execute("ALTER TABLE evaluacion ADD COLUMN fecha_evaluacion DATETIME")
            print("added_column=evaluacion.fecha_evaluacion")
        if "updated_at" not in eval_cols:
            conn.execute("ALTER TABLE evaluacion ADD COLUMN updated_at DATETIME")
            print("added_column=evaluacion.updated_at")

        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        active = conn.execute("SELECT id FROM examen WHERE estado='activo' ORDER BY id DESC LIMIT 1").fetchone()
        if active:
            examen_id = int(active[0])
            print(f"active_exam_existing={examen_id}")
        else:
            cur = conn.execute(
                """
                INSERT INTO examen (nombre, descripcion, estado, fecha_inicio, created_at)
                VALUES (?, ?, 'activo', ?, ?)
                """,
                ("Histórico inicial / Evaluación actual", "Examen creado por migración para conservar las evaluaciones existentes.", now, now),
            )
            examen_id = int(cur.lastrowid)
            print(f"active_exam_created={examen_id}")

        conn.execute("UPDATE evaluacion SET examen_id=? WHERE examen_id IS NULL", (examen_id,))
        conn.execute("UPDATE evaluacion SET fecha_evaluacion=COALESCE(fecha_evaluacion, ?) WHERE fecha_evaluacion IS NULL", (now,))
        conn.execute("UPDATE evaluacion SET updated_at=COALESCE(updated_at, ?) WHERE updated_at IS NULL", (now,))

        alumnos = [row[0] for row in conn.execute("SELECT id FROM alumno")]
        for alumno_id in alumnos:
            conn.execute(
                """
                INSERT OR IGNORE INTO examen_alumno (examen_id, alumno_id, estado, fecha_inscripcion)
                VALUES (?, ?, 'pendiente', ?)
                """,
                (examen_id, alumno_id, now),
            )

        # Marcar completado/parcial según cantidad de estaciones evaluadas en este examen.
        total_estaciones = conn.execute("SELECT COUNT(*) FROM estacion").fetchone()[0] or 0
        for alumno_id in alumnos:
            hechas = conn.execute(
                "SELECT COUNT(DISTINCT estacion_id) FROM evaluacion WHERE examen_id=? AND alumno_id=?",
                (examen_id, alumno_id),
            ).fetchone()[0] or 0
            estado = "completado" if total_estaciones and hechas >= total_estaciones else ("evaluado_parcial" if hechas else "pendiente")
            conn.execute(
                "UPDATE examen_alumno SET estado=? WHERE examen_id=? AND alumno_id=?",
                (estado, examen_id, alumno_id),
            )

        conn.commit()
        print(f"migration_ok=true")
        print(f"exam_id={examen_id}")
        print(f"students_enrolled={len(alumnos)}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
