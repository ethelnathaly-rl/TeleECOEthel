# TeleECOE — Exámenes, histórico e importación de alumnos

Fecha: 2026-05-12  
Proyecto: `SistemaEvaluacion v2` / TeleECOE

## Objetivo

Separar la lista de alumnos y calificaciones por examen/convocatoria para poder:

- conservar históricos con fecha;
- cerrar un examen sin perder resultados;
- iniciar otro examen con lista limpia o copiando alumnos;
- agregar alumnos manualmente;
- importar alumnos de forma masiva desde un archivo compatible con Excel;
- descargar una plantilla desde el panel de administración.

---

## Cambios de base de datos

Se agregaron dos tablas nuevas:

### `examen`

Representa una convocatoria/examen.

Campos:

- `id`
- `nombre`
- `descripcion`
- `estado`: `activo`, `cerrado` o `archivado`
- `fecha_inicio`
- `fecha_cierre`
- `created_at`

### `examen_alumno`

Relaciona alumnos con un examen específico.

Campos:

- `id`
- `examen_id`
- `alumno_id`
- `estado`: `pendiente`, `evaluado_parcial`, `completado`, `ausente`, `anulado`
- `fecha_inscripcion`
- `observaciones`

Restricción:

- Un alumno no puede estar duplicado dentro del mismo examen: `UNIQUE(examen_id, alumno_id)`.

### Cambios en `evaluacion`

Se agregaron:

- `examen_id`
- `fecha_evaluacion`
- `updated_at`

Esto permite que una evaluación pertenezca a un examen/convocatoria concreta y no se mezcle con futuras rondas.

---

## Migración aplicada

Script:

```text
scripts/migrate_examenes.py
```

Qué hace:

1. Crea backup automático de `evaluaciones.db` en `backups/`.
2. Crea tablas `examen` y `examen_alumno` si no existen.
3. Agrega columnas nuevas a `evaluacion` si faltan.
4. Crea un examen inicial:

```text
Histórico inicial / Evaluación actual
```

5. Asocia todas las evaluaciones existentes a ese examen inicial.
6. Inscribe todos los alumnos actuales en ese examen.
7. Marca alumnos como `pendiente`, `evaluado_parcial` o `completado` según evaluaciones existentes.

Resultado verificado tras migración:

```text
examen_count=1
examen_alumno_count=34
evaluacion_without_exam=0
```

Esto significa:

- existe 1 examen inicial;
- los 34 alumnos actuales fueron inscritos;
- ninguna evaluación quedó sin examen asociado.

---

## Cambios de interfaz

### Dashboard principal `/`

Ahora muestra la convocatoria/examen activo:

```text
Examen / convocatoria activa
```

También tiene botón:

```text
Gestionar Exámenes
```

### Gestión de exámenes `/examenes`

Permite:

- crear nuevo examen;
- cerrar el examen activo;
- activar un examen histórico;
- copiar alumnos del examen activo al nuevo examen;
- ver estado, fechas, cantidad de alumnos y evaluaciones por examen.

Al crear un nuevo examen:

- el examen activo anterior se cierra;
- el nuevo queda como `activo`;
- opcionalmente se copian alumnos.

### Gestión de alumnos `/alumnos`

Ahora trabaja sobre el examen activo.

Permite:

- agregar alumno manualmente al examen activo;
- editar datos de alumno;
- retirar alumno solo del examen activo sin borrar histórico;
- descargar plantilla CSV compatible con Excel;
- importar alumnos masivamente desde CSV.

Importante:

- El botón “Retirar” no borra al alumno globalmente ni sus evaluaciones históricas.
- Solo lo quita del examen activo.

---

## Importación masiva

Ruta:

```text
POST /alumnos/importar
```

Plantillas:

```text
GET /alumnos/plantilla-xlsx
GET /alumnos/plantilla
```

Archivos descargados:

```text
plantilla_alumnos_teleecoe.xlsx
plantilla_alumnos_teleecoe.csv
```

Columnas esperadas:

```text
codigo,nombres,apellidos,grupo,cmp,correo,documento,observaciones
```

Notas:

- El formato recomendado es Excel `.xlsx`.
- También se acepta CSV compatible con Excel.
- En CSV, el sistema acepta separadores coma, punto y coma o tabulación.
- `codigo` puede usarse como ID si es numérico.
- Si hay `cmp`, se usa también para detectar alumnos existentes.
- Si el alumno existe, actualiza nombre/grupo/CMP.
- Si no existe, lo crea.
- Luego lo inscribe en el examen activo.

---

## Cambios de flujo tablet

Rutas tablet ahora usan el examen activo:

- selección de alumno por estación;
- detección de alumnos ya evaluados;
- creación/edición de evaluación;
- reinicio de evaluación.

Antes una evaluación se buscaba solo por:

```text
alumno_id + estacion_id
```

Ahora se busca por:

```text
examen_id + alumno_id + estacion_id
```

Esto evita que un nuevo examen sobrescriba evaluaciones de una convocatoria anterior.

---

## Archivos modificados

```text
app/models/models.py
app/models/__init__.py
app/routes/master.py
app/routes/tablet.py
app/routes/analytics.py
app/templates/master_dashboard.html
app/templates/master_alumnos.html
app/templates/master_examenes.html
app/templates/tablet_seleccionar.html
scripts/migrate_examenes.py
docs/EXAMENES_ALUMNOS_IMPORTACION_2026-05-12.md
```

---

## Verificación realizada

Después de migrar y reiniciar Flask:

```text
tablet_rcp_status=200
analytics_summary_status=200
examen_columns=id,nombre,descripcion,estado,fecha_inicio,fecha_cierre,created_at
examen_alumno_columns=id,examen_id,alumno_id,estado,fecha_inscripcion,observaciones
evaluacion_columns=id,alumno_id,estacion_id,puntaje_total,video_camara1,video_camara2,examen_id,fecha_evaluacion,updated_at
examen_count=1
examen_alumno_count=34
evaluacion_without_exam=0
```

---

## Formatos soportados

La importación soporta:

- `.xlsx` nativo mediante `openpyxl`.
- `.csv` compatible con Excel/Moodle.

---

## Próximas mejoras recomendadas

1. Exportar resultados por examen en CSV/Excel.
2. Agregar vista de histórico por alumno.
3. Permitir marcar alumno como ausente/anulado.
4. Agregar vista previa antes de confirmar importación.
5. Agregar vista previa visual antes de confirmar importación.
6. Agregar autenticación/roles antes de uso real multiusuario.
