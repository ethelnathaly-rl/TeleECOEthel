# TeleECOE — Configuración detallada de video RCP HD/SD real

Fecha: 2026-05-12  
Proyecto: `SistemaEvaluacion v2` / TeleECOE  
Ruta local: `/home/lucina/.openclaw/workspace/projects/SistemaEvaluacion-v2/SistemaEvaluacion v2`

> Este documento existe para poder reconstruir la configuración de video RCP si en el futuro se desconfigura el proyecto, se cambia la cámara, se actualiza go2rtc o se hacen mejoras.
>
> **No contiene credenciales reales.** El archivo real `go2rtc.yaml` sí contiene datos sensibles de Tuya y no debe subirse a Git ni copiarse en chats/documentación pública.

---

## 1. Objetivo de esta configuración

La estación 5/RCP usa una cámara Tuya/Smart Life integrada por go2rtc. El objetivo fue permitir elegir entre calidades de transmisión **reales desde origen**, no solo reescalar localmente.

La configuración final agrega dos streams:

| Stream go2rtc | Calidad | Tipo | Descripción |
|---|---:|---|---|
| `camara1` | HD real | origen Tuya | Stream principal solicitado a Tuya/go2rtc con `resolution=hd`. |
| `camara1_sd` | SD real | origen Tuya | Substream liviano solicitado a Tuya/go2rtc con `resolution=sd`. Confirmado como H.264 640x360 ~20 fps. |

Diferencia clave:

- **HD real / SD real**: la cámara/Tuya entrega un stream diferente desde origen.
- **Reescalado local**: FFmpeg recibe un stream grande y lo convierte a otra resolución. Esto puede reducir peso final, pero no reduce el tráfico/origen ni necesariamente mejora estabilidad.

La opción implementada aquí es la primera: **calidad real solicitada a Tuya/go2rtc**.

---

## 2. Arquitectura de video actual

Ruta conceptual:

```text
Cámara Tuya / Smart Life
        ↓
Tuya Cloud / relay Tuya
        ↓
go2rtc local
        ↓
TeleECOE Flask / navegador tablet
```

Servicios locales relevantes:

| Servicio | Puerto | Uso |
|---|---:|---|
| Flask TeleECOE | `5000` | Aplicación web/tablet. |
| go2rtc API/UI | `1984` | Visores WebRTC/MSE/HLS y API. |
| go2rtc RTSP | `8554` | Entrada RTSP local usada por FFmpeg/ffprobe. |
| go2rtc WebRTC | `8555` | Transporte WebRTC hacia navegador. |

URLs locales útiles:

```text
TeleECOE tablet RCP:
http://172.18.4.179:5000/tablet/rcp/evaluar/1

Visor RCP directo dentro de Flask:
http://172.18.4.179:5000/tablet/camera/auto-reload

WebRTC HD real directo go2rtc:
http://172.18.4.179:1984/webrtc.html?src=camara1

WebRTC SD real directo go2rtc:
http://172.18.4.179:1984/webrtc.html?src=camara1_sd

HLS local HD real go2rtc:
http://172.18.4.179:1984/api/stream.m3u8?src=camara1&mp4

HLS local SD real go2rtc:
http://172.18.4.179:1984/api/stream.m3u8?src=camara1_sd&mp4

RTSP local HD real:
rtsp://127.0.0.1:8554/camara1

RTSP local SD real:
rtsp://127.0.0.1:8554/camara1_sd
```

---

## 3. Archivo sensible `go2rtc.yaml`

Archivo real:

```text
go2rtc.yaml
```

Este archivo está ignorado por Git porque contiene credenciales/URL sensible Tuya. No copiarlo entero en documentación pública.

### 3.1 Estructura correcta esperada

La sección `streams:` debe tener `camara1` y `camara1_sd` como entradas hermanas, no una dentro de la otra.

Forma correcta conceptual, con URL redactada:

```yaml
streams:
  camara1:
    - tuya://<host-tuya>?device_id=<device_id>&email=<email>&password=<password>&resolution=hd
  camara1_sd:
    - tuya://<host-tuya>?device_id=<device_id>&email=<email>&password=<password>&resolution=sd

log:
  level: trace
  api: trace

webrtc:
  listen: ":8555"
  candidates:
    - 172.18.4.179:8555
```

Puntos importantes:

1. `camara1` debe apuntar a la misma fuente Tuya con `resolution=hd`.
2. `camara1_sd` debe apuntar a la misma fuente Tuya con `resolution=sd`.
3. Ambas claves deben estar bajo `streams:` con la misma indentación.
4. La URL real puede ser una lista YAML (`- tuya://...`) o una línea equivalente aceptada por go2rtc, pero mantener estructura clara evita errores.
5. Si queda así, está mal:

```yaml
streams:
  camara1:
    camara1_sd:
      - tuya://...resolution=sd
      - tuya://...resolution=hd
```

Ese error causó que `camara1` respondiera `404 Not Found` por RTSP.

### 3.2 Verificación redactada de estructura

Comando seguro para inspeccionar la estructura sin imprimir credenciales:

```bash
python3 - <<'PY'
from pathlib import Path
lines = Path('go2rtc.yaml').read_text(errors='replace').splitlines()
for i, line in enumerate(lines[:20], 1):
    s = line.strip()
    if 'tuya://' in s:
        leading = len(line) - len(line.lstrip(' '))
        res = 'sd' if 'resolution=sd' in s else ('hd' if 'resolution=hd' in s else 'unknown')
        print(f'{i}: indent={leading} <tuya-url-redacted resolution={res}>')
    else:
        print(f'{i}: {line}')
PY
```

Resultado sano esperado, conceptualmente:

```text
1: streams:
2:   camara1:
3:     <tuya-url-redacted resolution=hd>
4:   camara1_sd:
5:     <tuya-url-redacted resolution=sd>
```

---

## 4. Visor Flask: `camera_auto_reload.html`

Archivo:

```text
app/templates/camera_auto_reload.html
```

Este template es el visor embebido por la estación RCP. Está diseñado para mostrar controles flotantes abajo a la derecha.

Controles esperados:

```text
HD | SD | HLS | WebRTC | Auto | MSE | Reconectar
```

En la interfaz se muestran como **HD** y **SD** para que el evaluador pueda elegir rápido justo antes de presionar **Grabar**. Técnicamente siguen siendo calidades reales desde Tuya/go2rtc, no reescalado local.

### 4.1 Calidad

El visor guarda la calidad elegida en `localStorage`:

```javascript
const QUALITY_STORAGE_KEY = 'teleecoe.rcp.camera.quality';
```

Valores:

| Valor | Stream usado | Botón visible |
|---|---|---|
| `hd` | `camara1` | **HD** |
| `sd` | `camara1_sd` | **SD** |

Función central:

```javascript
function streamName() {
    return currentQuality === 'sd' ? 'camara1_sd' : 'camara1';
}
```

Esto permite que todos los modos de transporte usen la calidad seleccionada.

### 4.2 Transporte

El modo elegido se guarda en:

```javascript
const STORAGE_KEY = 'teleecoe.rcp.camera.mode';
```

Modos:

| Modo | Descripción |
|---|---|
| `webrtc` | Visor `webrtc.html` de go2rtc. Recomendado por estabilidad. |
| `hls` | Usa HLS oficial Tuya si está configurado; si no, HLS local de go2rtc. |
| `auto` | Visor `stream.html` de go2rtc sin forzar modo. |
| `mse` | Visor `stream.html?mode=mse`. Útil para diagnóstico, antes mostró cortes. |

URLs generadas por el visor:

```javascript
// WebRTC
http://${host}:1984/webrtc.html?src=${streamName()}&_=${stamp}

// MSE
http://${host}:1984/stream.html?src=${streamName()}&mode=mse&_=${stamp}

// Auto
http://${host}:1984/stream.html?src=${streamName()}&_=${stamp}

// HLS local go2rtc
http://${host}:1984/api/stream.m3u8?src=${streamName()}&mp4&_=${stamp}
```

### 4.3 Fallback HLS

El visor intenta HLS cuando se presiona el botón HLS.

Lógica:

1. Si está configurado HLS oficial Tuya (`RCP_CAMERA_HLS_URL` o `RCP_CAMERA_HLS_URL_COMMAND`), usa `/tablet/api/camera/hls-url`.
2. Si no hay HLS oficial Tuya, usa HLS local go2rtc:

```text
/api/stream.m3u8?src=<camara1|camara1_sd>&mp4
```

3. Si HLS falla, cae a WebRTC automáticamente.

---

## 5. Endpoint Flask HLS

Archivo:

```text
app/routes/tablet.py
```

Endpoint:

```text
GET /tablet/api/camera/hls-url
```

Uso:

- Sirve para obtener una URL HLS oficial temporal de Tuya si se configura por entorno.
- No guarda tokens.
- No imprime credenciales.
- Si no está configurado, el visor puede usar HLS local go2rtc directamente.

Variables relacionadas:

```text
RCP_CAMERA_DEFAULT_MODE
RCP_CAMERA_HLS_URL
RCP_CAMERA_HLS_URL_COMMAND
RCP_CAMERA_HLS_URL_TIMEOUT
```

Actualmente la vía oficial Tuya Cloud quedó bloqueada por plan vencido/pago, así que la ruta práctica sin pago es HLS local go2rtc o WebRTC go2rtc.

---

## 6. Variables `.env` relevantes

Archivo sensible real:

```text
.env
```

Plantilla segura:

```text
.env.example
```

Variables importantes:

```env
FLASK_DEBUG=false
TEMPLATES_AUTO_RELOAD=true

RCP_CAMERA_DEFAULT_MODE=webrtc
RCP_CAMERA_HLS_URL=
RCP_CAMERA_HLS_URL_COMMAND=
RCP_CAMERA_HLS_URL_TIMEOUT=10
```

Notas:

- `TEMPLATES_AUTO_RELOAD=true` evita que Flask siga sirviendo plantillas viejas durante desarrollo.
- Si `RCP_CAMERA_HLS_URL_COMMAND` queda apuntando al generador Tuya Cloud y el plan Tuya está vencido, HLS oficial fallará y el visor deberá caer a WebRTC.
- Para pruebas sin pago, conviene dejar HLS oficial vacío y usar HLS local go2rtc.

---

## 7. Comandos de arranque/reinicio

### 7.1 Reiniciar go2rtc

Usar el binario local correcto:

```bash
./tools/go2rtc -config go2rtc.yaml
```

No usar `go2rtc` global: puede no existir o no ser la versión correcta.

Versión usada durante estas pruebas:

```text
go2rtc 1.9.14
```

### 7.2 Reiniciar Flask

Desde la carpeta del proyecto:

```bash
.venv-linux/bin/python run.py
```

Flask sirve la app en:

```text
http://172.18.4.179:5000
```

---

## 8. Verificaciones técnicas

### 8.1 Verificar que Flask sirve los botones HD/SD

```bash
python3 - <<'PY'
import urllib.request
url = 'http://127.0.0.1:5000/tablet/camera/auto-reload'
with urllib.request.urlopen(url, timeout=10) as r:
    body = r.read(20000).decode('utf-8', errors='replace')
    print(f'status={r.status}')
    print('has_hd_sd=' + str(('HD real' in body) and ('SD real' in body)))
    print('uses_camara1_sd=' + str('camara1_sd' in body))
PY
```

Resultado esperado:

```text
status=200
has_hd_sd=True
uses_camara1_sd=True
```

### 8.2 Verificar HD real por RTSP

```bash
./tools/ffmpeg-static/ffprobe \
  -v error \
  -rtsp_transport tcp \
  -select_streams v:0 \
  -show_entries stream=codec_name,width,height,avg_frame_rate,r_frame_rate \
  -of json \
  rtsp://127.0.0.1:8554/camara1
```

Resultado esperado aproximado para HD, si Tuya entrega bien en ese momento:

```json
{
  "streams": [
    {
      "codec_name": "h264",
      "width": 2304,
      "height": 1296,
      "r_frame_rate": "...",
      "avg_frame_rate": "20/1"
    }
  ]
}
```

Puede mostrar errores H.264/PPS heredados de Tuya Cloud/relay. Eso ya se observó antes y no necesariamente implica que el visor no funcione, pero sí explica pixelación/corrupción al copiar/remuxear sin transcode.

### 8.3 Verificar SD real por RTSP

```bash
./tools/ffmpeg-static/ffprobe \
  -v error \
  -rtsp_transport tcp \
  -select_streams v:0 \
  -show_entries stream=codec_name,width,height,avg_frame_rate,r_frame_rate \
  -of json \
  rtsp://127.0.0.1:8554/camara1_sd
```

Resultado confirmado el 2026-05-12:

```json
{
  "streams": [
    {
      "codec_name": "h264",
      "width": 640,
      "height": 360,
      "r_frame_rate": "239/12",
      "avg_frame_rate": "20/1"
    }
  ]
}
```

Esto confirma que `camara1_sd` es un substream real liviano, no reescalado local.

### 8.4 Verificar HLS local go2rtc

HD:

```bash
curl -s 'http://127.0.0.1:1984/api/stream.m3u8?src=camara1&mp4' | head
```

SD:

```bash
curl -s 'http://127.0.0.1:1984/api/stream.m3u8?src=camara1_sd&mp4' | head
```

Resultado sano esperado:

```text
#EXTM3U
#EXT-X-STREAM-INF:...
hls/playlist.m3u8?...
```

Si responde vacío, timeout o error interno, probar primero WebRTC. HLS local de go2rtc puede necesitar que el productor Tuya ya esté activo o puede ser sensible a audio/codecs.

---

## 9. Recomendación de uso práctico

Para la tablet durante evaluación RCP:

1. Probar primero:

```text
SD real + WebRTC
```

Motivo:

- SD real usa menos ancho de banda.
- WebRTC fue más estable que MSE en pruebas previas.
- Si la prioridad es fluidez y evitar cortes, SD real puede ser mejor aunque menos nítido.

2. Si se necesita más nitidez:

```text
HD real + WebRTC
```

Motivo:

- Mayor detalle visual.
- Puede pesar más y exponer más los problemas de Tuya Cloud/relay.

3. HLS:

```text
SD real + HLS
HD real + HLS
```

Útil para comparar, pero si falla debe caer a WebRTC.

4. MSE:

Usar solo como diagnóstico. Anteriormente mostró reconexiones/cortes con go2rtc/Tuya.

---

## 10. Grabación RCP vs visor

Importante: el selector HD/SD actual afecta principalmente al **visor**.

La grabación RCP en `app/routes/tablet.py` históricamente usa:

```text
rtsp://127.0.0.1:8554/camara1
```

Y luego FFmpeg transcodifica a MP4 validado.

Si en el futuro se quiere que la grabación también use SD real o HD real seleccionable, hay que modificar la lógica de grabación para elegir entre:

```text
rtsp://127.0.0.1:8554/camara1      # HD real
rtsp://127.0.0.1:8554/camara1_sd   # SD real
```

No confundir:

- `RECORDING_SCALE=854:-2` o `640:-2` = reescalado local de FFmpeg.
- `camara1_sd` = stream SD real desde Tuya/go2rtc.

---

## 11. Problemas conocidos y diagnóstico rápido

### 11.1 No aparece botón HD/SD/HLS

Causas probables:

1. Flask está sirviendo plantilla vieja.
2. Navegador/tablet tiene cache/localStorage viejo.
3. Se está mirando la página padre y no el iframe interno.

Soluciones:

```text
- Recarga dura del navegador.
- Abrir directo /tablet/camera/auto-reload.
- Confirmar TEMPLATES_AUTO_RELOAD=true.
- Reiniciar Flask.
```

Verificación:

```bash
python3 - <<'PY'
import urllib.request
with urllib.request.urlopen('http://127.0.0.1:5000/tablet/camera/auto-reload', timeout=10) as r:
    body = r.read(20000).decode('utf-8', errors='replace')
    print('HD' in body, 'SD' in body, 'HLS' in body)
PY
```

### 11.2 `camara1` da 404

Causa vista el 2026-05-12:

`go2rtc.yaml` quedó mal indentado y `camara1_sd` terminó dentro de `camara1`.

Revisar que estén como entradas hermanas bajo `streams:`.

### 11.3 `camara1_sd` da timeout

Posibles causas:

1. Tuya Cloud/relay demoró en abrir el productor.
2. go2rtc está reiniciando productor.
3. Cámara offline o Tuya MQTT desconectado.
4. La sesión Tuya no entrega substream temporalmente.

Revisar logs:

```bash
tail -n 120 logs/go2rtc.log
```

Buscar líneas tipo:

```text
start producer ... resolution=sd
stop producer ... resolution=sd
tuya: mqtt: disconnect
```

### 11.4 Errores H.264/PPS en HD

Se observaron antes errores como:

```text
non-existing PPS 0 referenced
decode_slice_header error
Missing reference picture
```

Interpretación:

- Vienen de la ruta Tuya Cloud/relay o del empaquetado H.264 recibido.
- Por eso no conviene usar copy/remux directo como evidencia final.
- Para grabación, mantener FFmpeg con transcode, warm-up y validación MP4.

---

## 12. Archivos tocados por esta configuración

### Sensible / no versionar

```text
go2rtc.yaml
.env
logs/go2rtc.log
```

### Código/documentación versionable

```text
app/templates/camera_auto_reload.html
app/routes/tablet.py
app/__init__.py
.env.example
docs/RCP_HLS_SETUP.md
docs/TUYA_OFFICIAL_VIDEO_OPTIONS_2026-05-12.md
docs/RCP_VIDEO_CONFIG_HD_SD_2026-05-12.md
scripts/tuya_hls_url.py
```

---

## 13. Estado final registrado

Al cierre de esta configuración:

- El visor Flask sirve botones `HD` y `SD` para selección manual simple antes de grabar.
- `camara1_sd` fue validado como stream real:

```text
H.264 640x360 ~20 fps
```

- `camara1` representa HD real con `resolution=hd`.
- `camara1_sd` representa SD real con `resolution=sd`.
- WebRTC sigue siendo el modo recomendado inicial.
- HLS local go2rtc queda disponible como alternativa gratuita.
- HLS oficial Tuya Cloud quedó bloqueado por plan Tuya vencido/pago.

---

## 14. Próximas mejoras posibles

1. Agregar selector de calidad también para grabación, no solo visor.
2. Guardar la preferencia HD/SD por estación o por dispositivo tablet.
3. Añadir indicador visible de resolución actual en el visor.
4. Crear endpoint `/tablet/api/camera/status` que consulte go2rtc y muestre si HD/SD están activos.
5. Probar grabación usando `camara1_sd` directamente para evidencia liviana.
6. Comparar visualmente:

```text
SD + WebRTC
HD + WebRTC
SD + HLS local
HD + HLS local
```

En esos nombres, **HD** y **SD** son las etiquetas visibles para el evaluador; internamente siguen correspondiendo a `camara1` y `camara1_sd`.

7. Si se requiere nitidez garantizada sin dependencia Tuya Cloud/relay, evaluar cámara RTSP/ONVIF/USB local.
