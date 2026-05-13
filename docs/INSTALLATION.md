# Instalación de TeleECOE

TeleECOE funciona en Windows, Linux y macOS usando Python 3.10+.

## Requisitos

- Python 3.10 o superior.
- Navegador moderno: Chrome, Edge, Firefox o Safari.
- Red local si se usarán tablets.
- Opcional para cámara/grabación RCP: go2rtc y FFmpeg configurados localmente.

---

## Windows

1. Instala Python desde <https://www.python.org/downloads/>.
2. Marca la opción **Add Python to PATH** durante la instalación.
3. Descarga o clona TeleECOE.
4. Abre PowerShell en la carpeta del proyecto.
5. Ejecuta:

```powershell
.\install.ps1
.\start.ps1
```

Si PowerShell bloquea scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

También puedes usar:

```bat
install.bat
start.bat
```

---

## Linux

```bash
chmod +x install.sh start.sh
./install.sh
./start.sh
```

---

## macOS

Instala Python 3 si no lo tienes:

```bash
brew install python
```

Luego:

```bash
chmod +x install.sh start.sh
./install.sh
./start.sh
```

---

## Acceso

PC maestra:

```text
http://localhost:5000
```

Tablets en la misma red:

```text
http://IP_DE_LA_PC:5000/tablet
```

La IP aparece al iniciar el servidor.

---

## Base de datos inicial

Los instaladores ejecutan:

```bash
python scripts/init_db.py --demo
```

Esto crea:

- `evaluaciones.db` local;
- estaciones de ejemplo;
- rúbricas simples;
- examen inicial;
- alumnos demo.

Para crear una base limpia sin alumnos demo:

```bash
python scripts/init_db.py --force
```

---

## Configuración local

Archivos importantes:

```text
.env              # configuración local, no subir a GitHub
go2rtc.yaml       # cámara real, no subir a GitHub
evaluaciones.db   # datos reales, no subir a GitHub
```

Se crean desde:

```text
.env.example
go2rtc.example.yaml
```

---

## Cámara RCP

Para usar cámara real, edita `go2rtc.yaml`.

Streams esperados por TeleECOE:

```text
camara1     # HD / principal
camara1_sd  # SD / liviano opcional
```

Si no configuras cámara, la app igual puede usarse para probar alumnos, estaciones, exámenes e importación.

---

## Importación de alumnos

Desde el panel **Alumnos** puedes descargar una plantilla:

- Excel `.xlsx` recomendado.
- CSV compatible con Excel.

Luego puedes subir el archivo para inscribir alumnos al examen activo.

---

## Verificación antes de publicar o compartir

```bash
python scripts/check_release.py
```

Debe terminar con:

```text
release_check_ok=true
```
