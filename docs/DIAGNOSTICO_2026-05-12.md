# Diagnóstico TeleECOE - 2026-05-12

## Objetivo

Ejecutar TeleECOE, diagnosticar su estado operativo y revisar el código para retomar desarrollo con seguridad.

## Estado operativo verificado

- Proyecto: `/home/lucina/.openclaw/workspace/projects/SistemaEvaluacion-v2/SistemaEvaluacion v2`
- Rama Git: `main`
- Últimos commits vistos:
  - `aa8c401 Optimizar visor y grabacion RCP Tuya`
  - `93b1b91 Cambiar visor RCP a WebRTC`
  - `f21db90 Evitar reconexión automática del visor RCP`
  - `5da2609 Robustecer validación de video RCP`
  - `71d1ce0 Agregar backlog de cambios solicitados para TeleECOE`
- Compilación Python: OK con `.venv-linux/bin/python -m py_compile run.py app/__init__.py app/routes/*.py app/models/*.py extensions.py`.
- Flask levantado con debug apagado durante diagnóstico.
- go2rtc levantado con configuración local sensible no versionada.

## Servicios levantados

- Flask: `http://127.0.0.1:5000` y `http://172.18.4.179:5000`
- go2rtc UI/API: `:1984`
- go2rtc RTSP: `:8554`
- go2rtc WebRTC: `:8555`

Listeners observados:

```text
0.0.0.0:5000 python
*:1984 go2rtc
*:8554 go2rtc
*:8555 go2rtc
```

## Endpoints verificados

- `GET /` → 200, dashboard maestro carga.
- `GET /tablet/` → 200, selección de estación carga.
- `GET /tablet/estacion/5` → 404. Esto no es necesariamente bug: la ruta real es `/tablet/<estacion_id>/seleccionar` o `/tablet/<estacion_id>/evaluar/<alumno_id>`.
- `GET :1984/` → 200, UI go2rtc carga.
- `GET :1984/webrtc.html?src=camara1` → 200, visor WebRTC carga.
- `GET :1984/api/streams` → 200, reporta `camara1` con productor configurado y 0 consumidores al momento de consulta.

## Base de datos

Conteos actuales:

- `Alumno`: 34
- `Estacion`: 10
- `Categoria`: 44
- `Criterio`: 208
- `Evaluacion`: 309
- `EvaluacionDetalle`: 4740

## Prueba cámara/RCP

### Resultado

La prueba integrada de grabación RCP no generó MP4 válido porque go2rtc no logró abrir `camara1` por RTSP en ese momento.

Evidencia:

```text
ffprobe rtsp://127.0.0.1:8554/camara1 → 404 Not Found
start → recording_started
status tras 18s → process_finished, returncode=8, bytes_written=0
stop → video_invalid, published=false, errors=[file_missing]
```

Logs go2rtc:

```text
error="tuya: mqtt: disconnect" stream=camara1
RTSP/1.0 404 Not Found
```

Interpretación: TeleECOE y go2rtc están levantados, pero la fuente Tuya Cloud/MQTT no está disponible/estable en ese momento. La validación robusta funcionó correctamente: no publicó ni asoció evidencia falsa.

## Revisión de código - hallazgos

### Críticos

1. **Sin autenticación ni autorización**
   - Archivos: `app/__init__.py`, `app/routes/master.py`, `app/routes/tablet.py`, `app/routes/analytics.py`.
   - Riesgo: cualquiera en la red local puede modificar datos, borrar registros, exportar información y controlar grabaciones.

2. **Sin CSRF en formularios y rutas destructivas**
   - Rutas POST de alumnos, estaciones, categorías, criterios, evaluación, reset y grabación.
   - Riesgo: acciones no deseadas desde otra página si el navegador tiene acceso al sistema.

3. **Borrados sin cascada completa garantizada**
   - Archivo: `app/models/models.py`.
   - `Evaluacion.detalles` tiene `cascade='all, delete-orphan'`, pero `Alumno.evaluaciones`, `Estacion.categorias/evaluaciones` y `Categoria.criterios` no.
   - Riesgo: `IntegrityError` o datos huérfanos al eliminar entidades con dependencias.

### Altos

4. **`FLASK_DEBUG` por defecto verdadero**
   - Archivo: `run.py`.
   - Aunque el diagnóstico lo levantó con `FLASK_DEBUG=false`, el fallback actual es inseguro para LAN.

5. **`SECRET_KEY` fallback insegura**
   - Archivo: `app/__init__.py`.
   - Usa `dev_secret_key_sistema_evaluacion` si no hay variable de entorno.

6. **Estado de grabación en memoria**
   - Archivo: `app/routes/tablet.py`.
   - `RECORDING_PROCESSES` se pierde si Flask reinicia o si luego se usa más de un worker.
   - Riesgo: procesos FFmpeg huérfanos o `.part.mp4` abandonados.

7. **Endpoints de grabación no validan alumno/estación**
   - Permiten IDs arbitrarios como `rcp/diag150142`.
   - Útil para pruebas, pero riesgoso en operación real.

### Medios

8. **Validación débil de formularios**
   - `int(request.form.get(...))` y conversiones similares pueden producir 500 con datos inválidos.

9. **Opciones tipo rango frágiles**
   - `parse_opciones()` usa `json.loads`; valores escritos como `0, 0.5, 1` caen al fallback `[0, 1, 2]`.

10. **Detener/validar video dentro del request**
    - `stop_and_validate_recording()` puede bloquear el POST de guardado si FFmpeg/FFprobe tarda.

11. **Ruta antigua rota**
    - `master.exportar_csv()` redirige a `analytics.export_data`, endpoint que no existe; el endpoint real es `analytics.export_csv`.

### Bajos/deuda técnica

- Lógica de negocio muy mezclada dentro de rutas Flask.
- No hay migraciones.
- No hay manejo centralizado de errores.
- Dependencia de CDN puede afectar uso offline.
- Consultas N+1 y carga completa en dashboard/analytics; aceptable para volumen actual, pero no escala bien.

## Próxima fase recomendada

Antes de seguir agregando funciones nuevas, se recomienda estabilizar en este orden:

1. Corregir bugs pequeños y seguros:
   - `master.exportar_csv` → `analytics.export_csv`.
   - `FLASK_DEBUG=false` por defecto.
   - Validación de ruta de tablet/documentación de URL correcta para estación.

2. Robustecer seguridad mínima LAN:
   - Login simple/admin PIN o token local.
   - CSRF con Flask-WTF o mecanismo equivalente.
   - Proteger rutas destructivas y exportaciones.

3. Robustecer integridad de datos:
   - Cascadas explícitas o borrados manuales transaccionales.
   - Manejo de `IntegrityError` con rollback y mensaje visible.

4. Robustecer RCP:
   - Validar estación/alumno en endpoints reales.
   - Detectar fuente Tuya desconectada antes de iniciar grabación.
   - Mostrar error claro si go2rtc/RTSP devuelve 404 o `tuya: mqtt: disconnect`.
   - Limpiar `.part.mp4` y procesos huérfanos al arrancar.

5. Agregar pruebas automatizadas mínimas:
   - Rutas principales con Flask test client.
   - CRUD básico.
   - Parseo de rango.
   - Grabación mockeada.

## Estado final del diagnóstico

El sistema TeleECOE está ejecutándose y la app base responde. La cámara RCP no está disponible por la ruta Tuya/go2rtc en el momento de la prueba (`tuya: mqtt: disconnect`). La nueva validación de video actuó correctamente al impedir publicar un MP4 inexistente o inválido.
