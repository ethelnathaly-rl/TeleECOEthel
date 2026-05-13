# Análisis completo de TeleECOE y puntos de mejora - 2026-05-13

## Objetivo

Revisar el estado funcional y técnico de TeleECOE después de su publicación en GitHub, entendiendo qué hace el sistema, qué módulos tiene, qué riesgos quedan y qué mejoras conviene priorizar.

## Evidencia revisada

- Repositorio local sincronizado con GitHub `maxchahuara/TeleECOE`.
- `README.md` y documentación principal.
- `docs/TELEECOE_GUIA_COMPLETA.md`.
- `docs/DIAGNOSTICO_2026-05-12.md`.
- `docs/PRODUCT_SPEC.md`.
- `docs/IMPLEMENTATION_PLAN.md`.
- `docs/CAMBIOS_SOLICITADOS.md`.
- Código Flask principal: `app/__init__.py`, `run.py`, `app/models/models.py`, `app/routes/master.py`, `app/routes/tablet.py`, `app/routes/analytics.py`.
- Plantillas RCP: `app/templates/tablet_evaluar.html`, `app/templates/camera_auto_reload.html`.
- Verificación `scripts/check_release.py` ejecutada correctamente.

Resultado de verificación:

```text
python_compile_ok=true
release_check_ok=true
```

## Qué hace TeleECOE actualmente

TeleECOE es una aplicación web local para gestionar evaluaciones tipo ECOE/OSCE usando una PC maestra y tablets en la misma red.

### Módulos principales

1. **Master / Administración**
   - Dashboard de alumnos por estación.
   - Gestión de alumnos.
   - Importación CSV/XLSX.
   - Plantillas descargables.
   - Gestión de estaciones, categorías y criterios.
   - Gestión de exámenes/convocatorias.

2. **Tablet / Evaluación**
   - Selección de estación.
   - Selección de alumno.
   - Formulario de evaluación por rúbrica.
   - Edición/corrección de evaluación existente.
   - Reinicio de evaluación.

3. **RCP / Cámara / Evidencia**
   - Visor de cámara integrado con go2rtc.
   - Modos HD, SD, HLS, WebRTC, Auto, MSE.
   - Grabación mediante FFmpeg desde RTSP local.
   - Archivo temporal `.part.mp4` y publicación final solo si valida.
   - Validación técnica con FFprobe/FFmpeg.
   - Asociación de video validado a `video_camara1`.

4. **Analytics / Reportes**
   - Resumen global.
   - Métricas por ítem.
   - Distribución por estación.
   - Exportación CSV.
   - Filtros por examen, estación y grupo.

5. **Distribución open-source**
   - Instaladores Windows/Linux/macOS.
   - Scripts de inicio.
   - Base demo reproducible.
   - Backup.
   - Check de release anti-secretos.
   - README, instalación, licencia MIT y contribución.

## Fortalezas actuales

- Proyecto ya versionado y publicado en GitHub.
- Separación razonable por blueprints Flask: `master`, `tablet`, `analytics`.
- `.env`, `go2rtc.yaml` y base real excluidos de Git.
- Instalación documentada para Windows/Linux/macOS.
- Soporte real para CSV y XLSX.
- Modelo de exámenes/convocatorias ya evita mezclar históricos.
- RCP ya tiene validación defensiva: no asocia video inválido como evidencia.
- Visor de cámara flexible con HLS/WebRTC/MSE y calidad HD/SD.
- Documentación amplia y útil para retomar el proyecto.

## Riesgos y debilidades principales

### Críticos

1. **No hay autenticación ni roles**
   - Cualquier persona en la red local puede entrar al master, tablet o analytics.
   - Puede modificar alumnos, rúbricas, evaluaciones, exámenes o exportar datos.

2. **No hay protección CSRF**
   - Las rutas POST no tienen token CSRF.
   - Riesgo de acciones no deseadas desde otra página abierta en el navegador.

3. **`FLASK_DEBUG` por defecto inseguro en `run.py`**
   - `run.py` usa `FLASK_DEBUG=true` si no hay variable de entorno.
   - `.env.example` lo deja en false, pero el fallback del código sigue siendo riesgoso.

4. **`SECRET_KEY` fallback fija**
   - Si el usuario no configura `.env`, la app usa una clave conocida.

### Altos

5. **Grabación RCP depende de estado en memoria**
   - `RECORDING_PROCESSES` se pierde si Flask reinicia.
   - No funcionaría bien con múltiples workers.
   - Puede dejar procesos o `.part.mp4` huérfanos.

6. **Endpoints de grabación aceptan IDs arbitrarios**
   - `/tablet/api/record/start/<estacion_id>/<alumno_id>` no valida que estación/alumno existan antes de arrancar FFmpeg.

7. **Cámara Tuya Cloud es inherentemente inestable**
   - Ya se observó `tuya: mqtt: disconnect` y RTSP 404 desde go2rtc.
   - TeleECOE maneja mejor el fallo, pero la fuente sigue siendo el punto más débil.

8. **Sin migraciones formales**
   - Cambios de esquema dependen de scripts manuales.
   - Riesgo al actualizar instalaciones reales.

9. **Borrados y relaciones incompletas**
   - Algunas relaciones no tienen cascadas explícitas.
   - Borrados de estaciones/categorías/criterios pueden causar errores o datos huérfanos si hay dependencias.

### Medios

10. **Validación de formularios insuficiente**
    - Muchas conversiones `int(...)` pueden terminar en error 500 ante datos inválidos.

11. **Lógica de negocio mezclada en rutas**
    - `master.py` y `tablet.py` concentran reglas, persistencia, validación y presentación.
    - Dificulta pruebas automatizadas.

12. **Analytics puede escalar mal**
    - Carga evaluaciones/detalles en memoria y hace cálculos Python.
    - Está bien para decenas/centenas, pero no para miles grandes.

13. **Dependencia de CDN en visor HLS**
    - `camera_auto_reload.html` usa `https://cdn.jsdelivr.net/npm/hls.js@1`.
    - Si se opera sin internet, HLS puede fallar.

14. **Pruebas automatizadas mínimas ausentes**
    - Hay `check_release.py`, pero no test suite funcional con Flask test client.

15. **Estado de video no está modelado en base de datos**
    - Solo se guarda ruta de video o `None`.
    - No quedan campos estructurados como `video_estado`, `video_error`, `duracion`, `bytes`, `validado_en`.

## Mejoras recomendadas por prioridad

### Fase 1 - Seguridad mínima LAN

1. Agregar login local simple.
   - Admin/coordinador.
   - Evaluador/tablet.
   - Técnico opcional.

2. Agregar roles y protección de rutas.
   - Master solo admin.
   - Analytics admin/coordinador.
   - Tablet evaluador.
   - Grabación solo desde flujo válido.

3. Agregar CSRF.
   - Formularios de master, tablet y acciones destructivas.

4. Cambiar defaults inseguros.
   - `FLASK_DEBUG=false` por defecto en código.
   - Si no hay `SECRET_KEY`, generar error claro o clave local persistente fuera de Git.

### Fase 2 - Confiabilidad RCP/cámara

5. Agregar página de diagnóstico RCP.
   - Estado Flask/go2rtc.
   - Estado RTSP `camara1` y `camara1_sd`.
   - FFmpeg/FFprobe disponibles.
   - Últimos logs de grabación.
   - Botón de prueba corta.

6. Validar estación/alumno antes de iniciar grabación.

7. Persistir estado de video en DB.
   - `video_estado`: pendiente, grabando, valido, invalido, fallido.
   - `video_error`.
   - `video_duracion`.
   - `video_bytes`.
   - `video_validado_en`.

8. Limpiar procesos y temporales al arrancar.
   - Detectar `.part.mp4` viejos.
   - Registrar/archivar logs de FFmpeg.

9. Probar candidato 854x480 con warm-up.
   - Comparar calidad/peso frente a 640x360 y 1280x720.

### Fase 3 - Integridad de datos y backups

10. Implementar backup automático antes de acciones críticas.
    - Antes de migraciones.
    - Antes de eliminar examen.
    - Antes de importación masiva.

11. Agregar migraciones con Alembic/Flask-Migrate.

12. Revisar cascadas y borrados.
    - Evitar eliminación física cuando haya histórico.
    - Preferir archivado/desactivación.

13. Envolver guardado de evaluación en transacción robusta.
    - Si falla un detalle, rollback completo.
    - Mostrar mensaje claro.

### Fase 4 - UX durante evaluación

14. Confirmación previa antes de evaluar.
    - Alumno correcto.
    - Estación correcta.
    - Examen activo correcto.

15. Búsqueda rápida de alumno en tablet.

16. Pantalla de éxito más útil.
    - Siguiente alumno.
    - Volver a lista.
    - Estado de video.
    - Puntaje guardado.

17. Dashboard con estados más claros.
    - Pendiente.
    - Parcial.
    - Completado.
    - Video válido/fallido si aplica.

18. Mejorar modo corrección.
    - Aviso de cambios.
    - Historial de correcciones.
    - Quién corrigió y cuándo, si se agregan usuarios.

### Fase 5 - Reportes y analítica

19. Exportación integral por examen.
    - Resumen por alumno.
    - Detalle por estación.
    - Detalle por criterio.
    - Estado de video.

20. Reporte imprimible por alumno.

21. Reporte por estación con ranking y distribución.

22. Mejorar filtros de analytics.
    - Examen.
    - Grupo.
    - Estación.
    - Alumno.
    - Estado.

### Fase 6 - Instalación y operación

23. Modo offline completo.
    - Descargar/servir Bootstrap, iconos, hls.js localmente.

24. Launcher gráfico o acceso directo.
    - Windows: acceso directo/start launcher.
    - Linux/macOS: script con URL visible.

25. Comando de diagnóstico general.
    - `python scripts/diagnose.py`.
    - Valida DB, rutas, cámara, FFmpeg, puertos y permisos.

26. Cierre de jornada.
    - Backup DB.
    - Resumen exportado.
    - Verificación videos.
    - Reporte final.

## Quick wins recomendados

Estas mejoras son pequeñas y de alto impacto:

1. Cambiar `FLASK_DEBUG` por defecto a `false` en `run.py`.
2. Corregir/confirmar cualquier endpoint antiguo de exportación que apunte a rutas inexistentes.
3. Agregar validación de alumno/estación en endpoints de grabación.
4. Servir `hls.js` local en lugar de CDN.
5. Agregar `video_estado` básico o al menos mostrar en UI cuando el video falló.
6. Crear `scripts/diagnose.py` para revisar entorno antes de una jornada.
7. Agregar pruebas Flask mínimas para rutas principales.

## Recomendación de siguiente sprint

El siguiente bloque de trabajo debería ser:

1. Seguridad mínima: login + CSRF + debug false.
2. Diagnóstico RCP: página/endpoint de salud cámara-go2rtc-FFmpeg.
3. Estado estructurado de video en DB.
4. Tests mínimos de rutas y guardado de evaluación.

Esto reduce el mayor riesgo operativo antes de seguir agregando funciones nuevas.
