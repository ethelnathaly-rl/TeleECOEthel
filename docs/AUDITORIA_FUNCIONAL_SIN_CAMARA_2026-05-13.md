# Auditoría funcional TeleECOE sin cámara/login - 2026-05-13

## Alcance

Por indicación del usuario, esta auditoría excluye por ahora:

- Login, roles y seguridad avanzada.
- Cámara/RCP/go2rtc/FFmpeg como flujo de video real.

Se revisó el funcionamiento base de TeleECOE:

- Dashboard maestro.
- Exámenes/convocatorias.
- Alumnos.
- Importación CSV/XLSX.
- Plantillas descargables.
- Estaciones.
- Constructor de rúbricas.
- Tablet sin cámara.
- Guardado y reinicio de evaluación.
- Analytics/exportación.
- Casos borde de duplicados y eliminaciones.

Las pruebas se ejecutaron con Flask test client sobre copias temporales de `evaluaciones.db`, sin modificar la base real.

## Hallazgos iniciales

### 1. Entorno virtual incompleto

El Python global no tenía Flask y `.venv-linux` no tenía `openpyxl`.

Evidencia:

```text
ModuleNotFoundError: No module named 'flask'
ModuleNotFoundError: No module named 'openpyxl'
```

Corrección operativa:

```bash
.venv-linux/bin/python -m pip install -r requirements.txt
```

Después de sincronizar dependencias, la app pudo importar y ejecutar rutas.

### 2. Rutas reales del constructor

La ruta correcta del constructor no es `/estaciones/<id>/rubrica`, sino:

- `GET /estaciones/<id>/constructor`
- `POST /categorias/nueva/<id_estacion>`
- `POST /criterios/nuevo/<id_categoria>`

Esto no es bug de ejecución, pero conviene unificar nombres en documentación/UI si aparece en guías.

### 3. Formularios podían lanzar 500 con números inválidos

Fallaban con error 500:

- Crear estación con `orden` no numérico.
- Crear alumno con `grupo` no numérico.

Corrección aplicada en `app/routes/master.py`:

- Validar `grupo` al crear/editar alumnos.
- Validar `orden` al crear/editar estaciones.
- Mostrar `flash()` y redirigir en lugar de lanzar 500.
- Manejar duplicados con `IntegrityError`.

### 4. Eliminar estación con rúbrica podía lanzar 500

Eliminar una estación que todavía tenía categorías/criterios fallaba por dependencias relacionadas.

Corrección aplicada en `app/routes/master.py`:

- Al eliminar estación, borrar primero detalles/evaluaciones de esa estación.
- Luego borrar criterios.
- Luego categorías.
- Finalmente borrar la estación.
- Manejar `IntegrityError` con rollback y mensaje visible.

## Pruebas ejecutadas

### Rutas base

Se verificaron con status 200:

- `/`
- `/examenes`
- `/alumnos`
- `/alumnos/plantilla`
- `/alumnos/plantilla-xlsx`
- `/estaciones`
- `/tablet/`
- `/analytics/`
- `/analytics/api/summary`
- `/analytics/api/items`
- `/analytics/api/stations`
- `/analytics/export`

`/exportar` redirige correctamente a exportación analytics.

### Flujo funcional completo probado

Sobre base temporal:

- Crear examen activo.
- Crear alumno manual.
- Editar alumno.
- Importar alumnos desde CSV.
- Importar alumnos desde XLSX.
- Descargar plantilla CSV.
- Descargar plantilla XLSX.
- Crear estación.
- Abrir constructor.
- Crear categoría.
- Crear criterios checkbox/rango.
- Abrir selección tablet.
- Abrir formulario de evaluación sin RCP.
- Guardar evaluación y verificar puntaje esperado.
- Reiniciar evaluación.
- Consultar analytics y export CSV.
- Eliminar categoría/criterios.
- Eliminar estación.

Resultado final después de fixes:

```text
functional_audit_ok=true
edge_audit_ok=true
release_check_ok=true
```

## Casos borde probados

- Estación duplicada: ya no produce 500; se maneja con mensaje.
- Alumno con ID duplicado: ya no produce 500; se maneja con mensaje.
- Estación con categorías/criterios: ya puede eliminarse sin 500.
- Categoría con criterio evaluado: no produjo 500 en la prueba.
- Criterio con detalle de evaluación: no produjo 500 en la prueba.
- Grupo inválido en alumno: ya no produce 500.
- Orden inválido en estación: ya no produce 500.

## Estado actual

El producto base, sin considerar cámara/login, queda funcionalmente estable en los flujos probados.

Quedan como mejoras no urgentes:

1. Unificar nombres/documentación del constructor de rúbrica.
2. Agregar tests automatizados permanentes en `tests/` en vez de scripts temporales.
3. Mejorar mensajes de validación por campo en la UI.
4. Evitar borrado físico de estaciones con histórico si se quiere conservar trazabilidad académica.
5. Migrar usos futuros de `Query.get()` a `db.session.get()` para eliminar warnings de SQLAlchemy 2.x.
