# TeleECOE

TeleECOE es un sistema web local para gestionar evaluaciones clinicas por estaciones tipo ECOE/OSCE. Esta pensado para trabajar con una **PC maestra** y varias **tablets o laptops evaluadoras**, dentro de una red local o mediante un tunel temporal controlado.

Nombre anterior del proyecto: `SistemaEvaluacion v2`.

## Version actual

**TeleECOE 1.1.0**

Esta version agrega manejo de estaciones activas/inactivas, grupos dinamicos, QR para tablets, exportaciones Excel separadas y scripts de conexion para tablets.

Versiones y rollback:

- Version actual: tag `v1.1.0`
- Version estable anterior: tag `v1.0.0`
- Guia de versiones: [`docs/VERSIONES.md`](docs/VERSIONES.md)
- Cambios por version: [`CHANGELOG.md`](CHANGELOG.md)

## Que problema resuelve

TeleECOE centraliza una evaluacion ECOE:

- el equipo organizador carga alumnos, estaciones y rubricas;
- cada evaluador abre una estacion desde tablet;
- el evaluador selecciona al alumno y completa la rubrica;
- el panel maestro consolida avance, notas y estado por estacion;
- el dashboard analitico resume resultados por estacion, item y grupo;
- si existe camara RCP configurada, puede mostrarse video y guardar evidencia MP4.

## Funciones principales

### Panel maestro

- Resumen de alumnos, estaciones activas y evaluaciones completadas.
- Matriz de avance por alumno y estacion.
- Enlace y QR para abrir el modo tablet.
- Descarga Excel del panel de calificaciones.
- Acceso a alumnos, examenes, estaciones y analitica.

### Examenes y convocatorias

- Crear una nueva convocatoria.
- Activar o cerrar examenes.
- Mantener historico separado por examen.
- Eliminar examenes no activos con confirmacion.
- Asociar alumnos a la convocatoria activa.

### Alumnos

- Registro manual de alumnos.
- Importacion masiva por CSV o XLSX.
- Descarga de plantilla compatible con Excel.
- Manejo de grupos dinamicos: 1, 2, 3 o mas grupos.
- Retiro de alumnos del examen activo sin borrar su historico global.

### Estaciones

- Crear, editar y ordenar estaciones.
- Activar o desactivar estaciones sin borrar rubricas ni resultados historicos.
- Configurar categorias, criterios, puntajes y tipos de respuesta.
- Ocultar estaciones inactivas del flujo de tablets.
- Bloquear rutas directas de tablet hacia estaciones inactivas.

### Modo tablet

- Lista solo estaciones activas.
- Seleccion de alumnos agrupada dinamicamente.
- Evaluacion o correccion de una evaluacion previa.
- Reinicio controlado de evaluaciones cuando corresponde.
- Interfaz pensada para uso rapido durante una estacion.

### Analitica

- Indicadores generales del examen activo.
- Filtros por estacion y grupo.
- Promedios por estacion.
- Tabla de items con tasas de acierto/fallo.
- Exportacion Excel del dashboard analitico con hojas separadas y graficos.

### RCP y video

TeleECOE puede integrarse con go2rtc y FFmpeg para una estacion RCP con camara.

Capacidades implementadas:

- visor con modos **HD**, **SD**, **HLS**, **WebRTC**, **Auto**, **MSE** y reconexion manual;
- grabacion MP4 mediante RTSP local y FFmpeg;
- validacion tecnica del video antes de asociarlo como evidencia;
- modo sin camara para pruebas o sedes donde la camara no este disponible.

La camara es opcional. El sistema puede usarse sin RCP/video.

## Novedades en 1.1.0

- Se agrego `estacion.activa`.
- Gestion de Estaciones permite activar/desactivar sin borrar datos.
- Dashboard, tablets y analitica consideran solo estaciones activas donde corresponde.
- La seleccion de alumnos en tablet ya no esta limitada a Grupo 1 y Grupo 2.
- Analytics obtiene grupos reales desde los datos del examen.
- El dashboard muestra QR para tablets.
- `TABLET_URL` permite usar una URL LAN, local o publica temporal.
- `/exportar` genera Excel del panel de calificaciones.
- `/analytics/export` genera Excel del dashboard analitico.
- Se agregaron scripts para tablets por USB o depuracion inalambrica ADB.
- Se documento versionado con tags `v1.0.0` y `v1.1.0`.

## Requisitos

- Python 3.10 o superior.
- Navegador moderno.
- Git, si se instalara desde el repositorio.
- Opcional: FFmpeg y go2rtc para camara/grabacion RCP.
- Opcional: ADB para abrir TeleECOE en tablets Android por USB o depuracion inalambrica.

## Instalacion rapida

### Windows

Abre PowerShell en la carpeta del proyecto:

```powershell
.\install.ps1
.\start.ps1
```

Si PowerShell bloquea scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Tambien se incluyen scripts `.bat`:

```bat
install.bat
start.bat
```

### Linux/macOS

```bash
chmod +x install.sh start.sh
./install.sh
./start.sh
```

Luego abre el panel maestro:

```text
http://localhost:5000
```

Guia detallada:

- [`docs/INSTALLATION.md`](docs/INSTALLATION.md)

## Primer uso

El instalador prepara:

- entorno virtual `.venv`;
- archivo `.env` basado en `.env.example`;
- archivo `go2rtc.yaml` basado en `go2rtc.example.yaml`;
- base local `evaluaciones.db` con datos demo o estructura inicial.

Despues de iniciar el sistema, entra al panel maestro y revisa:

1. Alumnos.
2. Examen activo.
3. Estaciones activas.
4. QR o URL para tablets.
5. Exportaciones y analitica.

## Conexion de tablets

### Misma red local

Desde una tablet en la misma red:

```text
http://IP_DE_LA_PC:5000/tablet/
```

El panel maestro muestra la URL y el QR.

### URL personalizada o tunel temporal

Si necesitas que el QR apunte a una URL publica temporal o dominio propio, define `TABLET_URL` en `.env`:

```env
TABLET_URL=https://tu-dominio-o-tunel.example/tablet/
```

Advertencia: exponer TeleECOE por internet requiere controles adicionales de seguridad. Para pruebas puntuales, usar un tunel temporal solo en entornos controlados.

### Tablet Android por USB

Si la red WiFi bloquea conexion entre tablet y PC, se puede usar ADB reverse por USB:

```bash
scripts/connect_tablet_usb.sh
```

El script reenvia puertos locales y abre:

```text
http://127.0.0.1:5000/tablet/
```

### Tablet Android por depuracion inalambrica

```bash
scripts/connect_tablet_wireless.sh pair <IP:PUERTO_EMPAREJAR> <CODIGO>
scripts/connect_tablet_wireless.sh connect <IP:PUERTO_ADB>
```

Tambien puede intentarse:

```bash
scripts/connect_tablet_wireless.sh auto
```

## Configuracion importante

Variables comunes en `.env`:

```env
SECRET_KEY=cambiar-en-produccion
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
DATABASE_URL=sqlite:///evaluaciones.db
TABLET_URL=
RCP_CAMERA_ENABLED=false
```

Para camara RCP:

```env
RCP_CAMERA_ENABLED=true
RCP_CAMERA_STATION_ID=rcp
RECORDING_STREAM_URL=rtsp://127.0.0.1:8554/camara1
FFMPEG_BIN=ffmpeg
FFPROBE_BIN=ffprobe
WARMUP_SECONDS=5
```

## Configuracion de camara

El archivo real `go2rtc.yaml` no se versiona porque puede contener credenciales, `device_id`, URLs Tuya o direcciones privadas.

Crear plantilla local:

```bash
cp go2rtc.example.yaml go2rtc.yaml
```

Streams esperados:

```text
camara1     # stream principal/HD
camara1_sd  # stream liviano/SD opcional
```

El proyecto no incluye credenciales de camara. Cada instalacion debe configurar sus propios streams.

## Exportaciones

TeleECOE genera dos archivos Excel distintos:

- `/exportar`: `panel_control_calificaciones.xlsx`
- `/analytics/export`: `dashboard_analitico_teleecoe.xlsx`

El primero esta orientado al control operativo de notas. El segundo esta orientado a analisis por estaciones e items.

## Versiones y rollback

Listar versiones:

```bash
git fetch --tags
git tag --sort=version:refname
```

Volver temporalmente a la version estable anterior:

```bash
git switch --detach v1.0.0
```

Volver a la rama principal:

```bash
git switch main
git pull
```

Crear una rama de recuperacion desde una version anterior:

```bash
git switch -c recuperacion-v1.0.0 v1.0.0
```

## Verificacion antes de publicar

Linux/macOS:

```bash
source .venv/bin/activate
python scripts/check_release.py
```

Windows:

```powershell
.\.venv\Scripts\python.exe scripts\check_release.py
```

La salida esperada incluye:

```text
python_compile_ok=true
release_check_ok=true
```

## Archivos que no deben subirse

El repositorio ignora archivos sensibles o pesados:

- `.env`
- `go2rtc.yaml`
- `evaluaciones.db`
- bases SQLite dentro de `instance/`
- grabaciones MP4
- logs
- backups
- entornos virtuales
- binarios descargados
- herramientas locales dentro de `tools/`

Antes de publicar cambios, revisar:

```bash
git status --ignored --short
python scripts/check_release.py
```

## Estructura principal

```text
app/
  models/             Modelos de datos
  routes/             Rutas Flask: master, tablet, analytics
  templates/          Vistas HTML
docs/                 Documentacion tecnica y operativa
scripts/              Inicializacion, backup, verificacion y conexion tablets
go2rtc.example.yaml   Plantilla segura de video
.env.example          Plantilla de configuracion
VERSION               Version actual
CHANGELOG.md          Historial de cambios
```

## Documentacion

- [`docs/INSTALLATION.md`](docs/INSTALLATION.md): instalacion Windows, Linux y macOS.
- [`docs/VERSIONES.md`](docs/VERSIONES.md): versiones publicadas y rollback.
- [`CHANGELOG.md`](CHANGELOG.md): cambios por version.
- [`docs/TELEECOE_GUIA_COMPLETA.md`](docs/TELEECOE_GUIA_COMPLETA.md): guia general del sistema.
- [`docs/EXAMENES_ALUMNOS_IMPORTACION_2026-05-12.md`](docs/EXAMENES_ALUMNOS_IMPORTACION_2026-05-12.md): examenes e importacion.
- [`docs/RCP_VIDEO_CONFIG_HD_SD_2026-05-12.md`](docs/RCP_VIDEO_CONFIG_HD_SD_2026-05-12.md): video RCP.

## Estado de seguridad

TeleECOE esta disenado para red local o entornos controlados. Antes de usarlo como servicio publico se recomienda agregar:

- autenticacion de usuarios;
- roles y permisos;
- proteccion CSRF;
- configuracion de servidor WSGI/produccion;
- HTTPS gestionado;
- politicas de respaldo y retencion;
- auditoria de accesos.

Ver tambien [`SECURITY.md`](SECURITY.md).

## Licencia

MIT. Ver [`LICENSE`](LICENSE).

## Contribuir

Las contribuciones son bienvenidas. Antes de enviar cambios:

1. Crea una rama.
2. Evita subir datos reales o credenciales.
3. Ejecuta `scripts/check_release.py`.
4. Documenta cambios relevantes en `CHANGELOG.md`.

Guia: [`CONTRIBUTING.md`](CONTRIBUTING.md).
