import sqlite3

def inspect():
    conn = sqlite3.connect('evaluaciones.db')
    cursor = conn.cursor()
    
    print("=== EXAMEN ALUMNO ===")
    cursor.execute("""
        SELECT ea.id, ea.examen_id, ea.alumno_id, a.nombre, a.grupo, ea.estado 
        FROM examen_alumno ea 
        JOIN alumno a ON ea.alumno_id = a.id
    """)
    for r in cursor.fetchall():
        print(r)
        
    print("\n=== EVALUACIONES ===")
    cursor.execute("""
        SELECT e.id, e.examen_id, e.alumno_id, a.nombre, e.estacion_id, e.puntaje_total, e.comentarios
        FROM evaluacion e
        JOIN alumno a ON e.alumno_id = a.id
    """)
    for r in cursor.fetchall():
        print(r)

    conn.close()

if __name__ == '__main__':
    inspect()
