# Changelog

## [1.3.1] - 2026-05-26

### Agregado

- Funcionalidad interactiva de ampliación (zoom/lightbox) en las imágenes clínicas en el **Modo Evaluado** (`/evaluado/`).
- Efecto hover premium de aumento (`scale` y `shadow`) en todas las imágenes dentro del acordeón clínico.
- Cursor dinámico de lupa (`zoom-in`) y modal Bootstrap (`imageZoomModal`) adaptativo y responsive que despliega imágenes como la radiografía o recetas en alta resolución al hacer clic.

## [1.3.0] - 2026-05-26

### Agregado

- Carga de datos clínicos reales y recursos de simulación premium para el **Modo Evaluado** (`/evaluado/`) y **Modo Evaluador** (`/tablet/`).
- Generación e integración de recursos médicos hiperrealistas en `app/static/ejemplos/`:
  - `rx_torax.png`: Radiografía de tórax con consolidación basal derecha.
  - `analisis_sangre.png`: Reporte analítico completo de hemograma y reactantes.
  - `receta_medica.png`: Modelo de receta formal con Amoxicilina/Ácido Clavulánico y Paracetamol.
- Grupo 3 de alumnos de prueba (`Dra. Camila Ortega Reyes`, `Dr. Mateo San Martín Flores`, etc.) vinculados al examen activo.
- Evaluaciones precargadas con comentarios de retroalimentación cualitativa detallada en español para demostrar el funcionamiento de los Popovers flotantes en el panel maestro de PC.
- Habilitación de HTML seguro (`|safe` filter) en el acordeón clínico del Modo Evaluado, permitiendo incorporar imágenes interactivas, listas y tablas.

## [1.2.0] - 2026-05-26

### Agregado

- Centro de Conexión Premium para Tablets en el Panel Maestro con pestañas interactivas para Red Local (Wi-Fi) y Acceso Público (Túnel).
- Generación de códigos QR dinámicos según el tipo de conexión activa y el tipo de ruteo de red.
- Botones de "Copiar Enlace" con micro-animaciones y confirmación visual instantánea.
- Formulario de Observaciones de Grupo Directo para la Etapa 2 en la tablet, permitiendo a los evaluadores calificar observaciones de todos los alumnos en una sola vista sin cambiar de página.
- Guardado rápido asíncrono (AJAX) y auto-guardado de observaciones al desenfocar (onblur) el área de comentarios.
- Temporizador flotante en tiempo real integrado en la pantalla principal de selección de alumnos para la tablet.

## [1.1.0] - 2026-05-22

### Agregado

- Gestión de estaciones activas/inactivas sin borrar rúbricas ni histórico.
- Selección de alumnos en tablet con grupos dinámicos, compatible con 1, 2, 3 o más grupos.
- QR y URL configurable para tablets desde el panel maestro (`TABLET_URL` opcional).
- Exportaciones Excel separadas para panel de calificaciones y dashboard analítico.
- Script USB ADB para tablets (`scripts/connect_tablet_usb.sh`).
- Script de depuración inalámbrica ADB para tablets (`scripts/connect_tablet_wireless.sh`).
- Migración idempotente para `estacion.activa`.
- Preparación de estación 5 sin cámara para pruebas de conectividad.
- Dependencia `qrcode` para generar el QR local.

### Cambiado

- Dashboard, tablet y analítica filtran estaciones activas cuando corresponde.
- La estación RCP con cámara puede deshabilitarse por configuración local sin romper estaciones sin cámara.
- El dashboard muestra una URL de tablet única, ya sea LAN/local o una URL pública temporal configurada.

### Verificado

- `scripts/check_release.py` pasa correctamente.
- Rutas locales principales responden HTTP 200: `/`, `/tablet/`, `/tablet-qr.svg`, `/estaciones`, `/analytics/`.

## [1.0.0] - 2026-05-13

### Publicado

- Primera versión pública estable en GitHub.
- Instalación multiplataforma Windows, Linux y macOS.
- Base demo reproducible, scripts de instalación/arranque/backup/verificación.
- Exámenes, alumnos, importación CSV/XLSX, estaciones, evaluación tablet, analítica y exportaciones base.
- Plantillas seguras `.env.example` y `go2rtc.example.yaml` sin credenciales.

## Historial inicial

### Preparación de repositorio

- Agregado `.gitignore` para excluir secretos, bases de datos, grabaciones, logs, entornos virtuales, backups y binarios pesados.
- Agregado `.env.example` para configuración local segura.
- Agregado `go2rtc.example.yaml` como plantilla sin credenciales.
- Agregado `README.md` con instalación, ejecución, estado actual y advertencias.
- Agregado `SECURITY.md` con lineamientos de seguridad.

### RCP / cámara

- Estación RCP orientada a una sola cámara (`camara1`).
- Grabación por FFmpeg RTSP transcode.
- Warm-up configurable para descartar frames iniciales del stream.
