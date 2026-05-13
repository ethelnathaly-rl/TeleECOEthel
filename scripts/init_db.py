#!/usr/bin/env python3
"""Inicializa una base SQLite limpia para TeleECOE.

Uso:
  python scripts/init_db.py              # crea evaluaciones.db si no existe
  python scripts/init_db.py --demo       # agrega alumnos demo
  python scripts/init_db.py --force      # reemplaza la base existente
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_DIR / "evaluaciones.db"


def configure_database_url() -> None:
    os.environ.setdefault("DATABASE_URL", "sqlite:///" + str(DB_PATH))
    os.environ.setdefault("SECRET_KEY", "teleecoe-local-dev-change-me")


def seed_base(db, models, demo: bool = False) -> None:
    Examen = models.Examen
    ExamenAlumno = models.ExamenAlumno
    Alumno = models.Alumno
    Estacion = models.Estacion
    Categoria = models.Categoria
    Criterio = models.Criterio

    if not Examen.query.first():
        db.session.add(Examen(nombre="Examen inicial", descripcion="Convocatoria inicial creada por init_db.py", estado="activo"))

    if not Estacion.query.first():
        estaciones = [
            Estacion(id="e1", nombre="Estación 1", orden=1),
            Estacion(id="e2", nombre="Estación 2", orden=2),
            Estacion(id="e3", nombre="Estación 3", orden=3),
            Estacion(id="e4", nombre="Estación 4", orden=4),
            Estacion(id="rcp", nombre="RCP", orden=5),
        ]
        db.session.add_all(estaciones)
        db.session.flush()

        for est in estaciones:
            cat = Categoria(estacion_id=est.id, nombre="Evaluación general", orden=1, tipo="normal")
            db.session.add(cat)
            db.session.flush()
            db.session.add_all([
                Criterio(id=f"{est.id}_c1", categoria_id=cat.id, texto="Cumple el paso principal", puntos=1.0, tipo="checkbox"),
                Criterio(id=f"{est.id}_c2", categoria_id=cat.id, texto="Comunica correctamente", puntos=1.0, tipo="checkbox"),
                Criterio(id=f"{est.id}_c3", categoria_id=cat.id, texto="Puntaje técnico", puntos=2.0, tipo="rango", opciones="[0, 1, 2]"),
            ])

    if demo and not Alumno.query.first():
        examen = Examen.query.filter_by(estado="activo").first() or Examen.query.first()
        alumnos = [
            Alumno(nombre="Alumno Demo 1", cmp="DEMO001", grupo=1),
            Alumno(nombre="Alumno Demo 2", cmp="DEMO002", grupo=1),
            Alumno(nombre="Alumno Demo 3", cmp="DEMO003", grupo=2),
        ]
        db.session.add_all(alumnos)
        db.session.flush()
        for alumno in alumnos:
            db.session.add(ExamenAlumno(examen_id=examen.id, alumno_id=alumno.id, fecha_inscripcion=datetime.utcnow()))

    db.session.commit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="agrega alumnos demo")
    parser.add_argument("--force", action="store_true", help="elimina evaluaciones.db antes de crearla")
    args = parser.parse_args()

    if args.force and DB_PATH.exists():
        DB_PATH.unlink()
        print(f"removed={DB_PATH}")

    configure_database_url()

    from app import create_app
    from extensions import db
    from app.models import models

    app = create_app()
    with app.app_context():
        db.create_all()
        seed_base(db, models, demo=args.demo)

    print(f"database_ready={DB_PATH}")
    print(f"demo={args.demo}")


if __name__ == "__main__":
    main()
