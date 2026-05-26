import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evaluaciones.db')

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Agregar video_camara1
    try:
        cursor.execute("ALTER TABLE evaluacion ADD COLUMN video_camara1 VARCHAR(255);")
        print("Columna video_camara1 añadida con éxito.")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            pass
        else:
            print(f"Error video_camara1: {e}")

    # Agregar video_camara2
    try:
        cursor.execute("ALTER TABLE evaluacion ADD COLUMN video_camara2 VARCHAR(255);")
        print("Columna video_camara2 añadida con éxito.")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            pass
        else:
            print(f"Error video_camara2: {e}")

    # Agregar comentarios (Etapa 2)
    try:
        cursor.execute("ALTER TABLE evaluacion ADD COLUMN comentarios TEXT;")
        print("Columna comentarios añadida con éxito.")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            print("La columna comentarios ya existe.")
        else:
            print(f"Error comentarios: {e}")

    # Agregar tipo_evaluacion (ECOE/Stage2)
    try:
        cursor.execute("ALTER TABLE examen ADD COLUMN tipo_evaluacion VARCHAR(50) NOT NULL DEFAULT 'ecoe';")
        print("Columna tipo_evaluacion añadida con éxito.")
    except Exception as e:
        if "duplicate column" in str(e).lower() or "duplicate" in str(e).lower():
            print("La columna tipo_evaluacion ya existe.")
        else:
            print(f"Error tipo_evaluacion: {e}")

    # Agregar timer_state
    try:
        cursor.execute("ALTER TABLE examen ADD COLUMN timer_state VARCHAR(20) NOT NULL DEFAULT 'stopped';")
        print("Columna timer_state añadida con éxito.")
    except Exception as e:
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            print("La columna timer_state ya existe.")
        else:
            print(f"Error timer_state: {e}")

    # Agregar timer_end_time
    try:
        cursor.execute("ALTER TABLE examen ADD COLUMN timer_end_time VARCHAR(50);")
        print("Columna timer_end_time añadida con éxito.")
    except Exception as e:
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            print("La columna timer_end_time ya existe.")
        else:
            print(f"Error timer_end_time: {e}")

    # Agregar timer_remaining
    try:
        cursor.execute("ALTER TABLE examen ADD COLUMN timer_remaining INTEGER DEFAULT 480;")
        print("Columna timer_remaining añadida con éxito.")
    except Exception as e:
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            print("La columna timer_remaining ya existe.")
        else:
            print(f"Error timer_remaining: {e}")

    # Agregar tablet_show_ecoe
    try:
        cursor.execute("ALTER TABLE examen ADD COLUMN tablet_show_ecoe BOOLEAN NOT NULL DEFAULT 1;")
        print("Columna tablet_show_ecoe añadida con éxito.")
    except Exception as e:
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            print("La columna tablet_show_ecoe ya existe.")
        else:
            print(f"Error tablet_show_ecoe: {e}")

    # Agregar tablet_show_stage2
    try:
        cursor.execute("ALTER TABLE examen ADD COLUMN tablet_show_stage2 BOOLEAN NOT NULL DEFAULT 1;")
        print("Columna tablet_show_stage2 añadida con éxito.")
    except Exception as e:
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            print("La columna tablet_show_stage2 ya existe.")
        else:
            print(f"Error tablet_show_stage2: {e}")
            
    # Crear tabla estacion_contenido_evaluado
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estacion_contenido_evaluado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estacion_id VARCHAR(50) NOT NULL,
                etapa VARCHAR(20) NOT NULL,
                seccion VARCHAR(50) NOT NULL,
                titulo VARCHAR(200),
                contenido TEXT,
                orden INTEGER DEFAULT 1,
                visible BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL,
                updated_at DATETIME,
                FOREIGN KEY (estacion_id) REFERENCES estacion (id) ON DELETE CASCADE
            );
        """)
        print("Tabla estacion_contenido_evaluado creada con éxito o ya existe.")
    except Exception as e:
        print(f"Error creando tabla estacion_contenido_evaluado: {e}")
            
    conn.commit()
    conn.close()
    print("Migración completada.")

if __name__ == '__main__':
    migrate()
