# TeleECOE - visor RCP HLS Tuya

Fecha: 2026-05-12

## Objetivo

Usar la mejor ruta de video disponible para la estación 5/RCP. Si Tuya Cloud entrega una URL HLS estable, TeleECOE puede usarla como visor principal. Si no está configurada o falla, cae automáticamente a WebRTC/go2rtc.

## Estado implementado

El visor `/tablet/camera/auto-reload` ahora soporta cuatro modos:

- **HLS**: si hay Tuya Cloud HLS configurado, usa esa URL oficial; si no, usa HLS local generado por go2rtc: `/api/stream.m3u8?src=camara1&mp4`.
- **WebRTC**: fallback principal vía go2rtc `webrtc.html?src=camara1`.
- **Auto**: reproductor automático de go2rtc.
- **MSE**: modo diagnóstico.

El botón HLS queda disponible incluso sin Tuya Cloud, usando go2rtc local como opción gratuita de comparación.

## Variables de entorno

```env
# Vacío = usa HLS si está configurado; si no, WebRTC.
RCP_CAMERA_DEFAULT_MODE=

# Opción simple para pruebas: URL temporal/directa .m3u8.
RCP_CAMERA_HLS_URL=

# Opción recomendada: comando local que imprime la URL temporal HLS.
# Puede devolver texto plano o JSON: {"url":"https://...m3u8"}
RCP_CAMERA_HLS_URL_COMMAND=
RCP_CAMERA_HLS_URL_TIMEOUT=15
```

No guardar `client_id`, `secret`, access tokens ni URLs firmadas permanentes en Git.

## Flujo recomendado para Tuya Cloud API

1. Crear/usar proyecto Tuya Developer Platform.
2. Autorizar IoT Core / IoT Video Live Stream.
3. Vincular el dispositivo/cuenta correctos.
4. Completar variables solo en `.env` local:

```env
RCP_CAMERA_DEFAULT_MODE=hls
RCP_CAMERA_HLS_URL_COMMAND=.venv-linux/bin/python scripts/tuya_hls_url.py --json

TUYA_ENDPOINT=https://openapi.tuyaus.com
TUYA_CLIENT_ID=...
TUYA_CLIENT_SECRET=...
TUYA_DEVICE_ID=...
TUYA_UID=... # opcional
TUYA_STREAM_TYPE=hls
```

5. El script incluido `scripts/tuya_hls_url.py`:
   - obtiene token Tuya con HMAC-SHA256;
   - llama al endpoint oficial `stream/actions/allocate`;
   - imprime la URL HLS temporal como JSON;
   - no guarda credenciales ni tokens.


## Fallback

Si Tuya Cloud HLS devuelve error, si la URL expira, o si el navegador no puede reproducir HLS, el visor cae a WebRTC/go2rtc para no bloquear la evaluación. Si Tuya Cloud HLS no está configurado, HLS usa directamente el endpoint gratuito/local de go2rtc.

## Grabación

Por ahora la grabación/evidencia se mantiene por la ruta validada:

```text
go2rtc RTSP local → FFmpeg transcode + warm-up → MP4 validado
```

No se cambia la grabación a HLS hasta comprobar que HLS sea más estable/nítido en pruebas reales.
