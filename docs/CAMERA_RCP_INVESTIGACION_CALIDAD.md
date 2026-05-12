# Investigación de calidad del visor RCP / cámara Tuya

Fecha: 2026-05-11

## Pregunta

¿Por qué la cámara RCP se pixela y qué opciones reales existen para mejorarla?

## Hallazgos comprobados

### 1. La ruta no es local directa

La fuente activa de `camara1` en go2rtc aparece como Tuya/WebRTC con transporte `mqtt+udp` y un `remote_addr` externo tipo relay. Esto confirma que el video llega desde infraestructura Tuya/relay hacia la laptop, aunque la cámara y la laptop estén en la misma red.

Ruta práctica actual:

```text
Cámara Tuya → nube/relay Tuya → go2rtc en laptop → navegador/estación RCP
```

### 2. El stream está en HD, no en SD

La configuración activa usa `resolution=hd`. Según la documentación de go2rtc para Tuya, la perilla principal expuesta es `resolution=hd` o `resolution=sd`; por tanto, no estamos usando accidentalmente baja resolución.

### 3. La resolución recibida es alta, pero el H.264 llega con errores/cortes

`ffprobe` sobre el RTSP local de go2rtc detectó video H.264 High de aproximadamente `2304x1296` a `20 fps`.

Sin embargo, al intentar copiar 10 segundos sin recomprimir (`-c copy`) aparecieron errores H.264 como:

- `non-existing PPS 0 referenced`
- `decode_slice_header error`
- `no frame`
- `Missing reference picture`
- `No start code is found`

El archivo resultante sin reencode quedó inválido. Esto indica que la fuente/relay Tuya o el restream puede entregar paquetes incompletos o sin cabeceras suficientes para remux directo estable.

### 4. WebRTC mejora estabilidad, pero no puede recuperar detalle perdido

WebRTC fue mejor que MSE en la prueba visual, pero si los bloques/pixelación ya vienen comprimidos o dañados desde Tuya Cloud, cambiar el reproductor no elimina el defecto.

## Interpretación

La pixelación no parece causada principalmente por que TeleECOE fuerce SD. La evidencia apunta a una mezcla de:

1. compresión/adaptación del stream Tuya Cloud;
2. transporte Tuya por relay externo;
3. paquetes H.264 con errores o cabeceras incompletas al llegar a go2rtc/RTSP;
4. escalado visual en navegador si se muestra a pantalla completa;
5. posible ruta WebRTC navegador↔go2rtc no óptima si no anuncia claramente la IP LAN correcta.

## Opciones de mejora

### Opción A — Ajustar WebRTC LAN de go2rtc

Agregar candidato LAN explícito para que el navegador use directamente la IP local de la laptop hacia go2rtc:

```yaml
webrtc:
  listen: ":8555"
  candidates:
    - 172.18.4.179:8555
```

Ventaja: puede mejorar el tramo laptop↔navegador/tablet.

Límite: no arregla compresión o errores que ya vengan desde Tuya Cloud.

### Opción B — Mantener WebRTC para preview y mejorar solo evidencia grabada

La grabación debe seguir transcodificando con FFmpeg y descartando errores. Se probó una salida `1280x720`, 15 fps, H.264 baseline, bitrate aproximado 1.8 Mbps. El MP4 resultante validó correctamente: duración 12.6 s, 189 frames, ~1.49 Mbps, decodificación con 0 warnings.

Inspección técnica de frames: calidad usable, compresión/ruido leve, sin corrupción severa ni macroblocks grandes. Esta ruta mejora la evidencia frente al escalado anterior `640x360`, aunque no elimina artefactos que ya vengan de Tuya Cloud.

Ventaja: mejora el video final/evidencia.

Límite: consume más CPU y espacio; no necesariamente mejora el preview en vivo.

### Opción C — Reducir escalado del preview

Si la señal efectiva tiene mucho macroblock, verla a pantalla completa aumenta la percepción de pixelación. Se puede mostrar el visor en un contenedor con tamaño máximo y fondo negro, o añadir un modo “Nitidez” que no estire más de cierto tamaño.

Ventaja: mejora percepción visual sin tocar cámara.

Límite: no aumenta información real de imagen.

### Opción D — Fuente local real

Para calidad clínica/estable, usar cámara con RTSP/ONVIF local real, cámara USB, cámara IP local o capturadora.

Ventaja: elimina dependencia de Tuya Cloud y reduce artefactos.

Límite: requiere hardware/configuración adicional.

## Pruebas aplicadas

### Candidato WebRTC LAN explícito

Se agregó en el `go2rtc.yaml` real, no versionado, un candidato WebRTC LAN explícito `172.18.4.179:8555` y se reinició go2rtc con el binario real `./tools/go2rtc`.

Verificación:

- API go2rtc OK.
- WebRTC escucha en `172.18.4.179:8555`.
- RTSP sigue activo en `:8554`.

### Grabación integrada TeleECOE a 720p

Se actualizó la grabación RCP para que sea parametrizable por entorno y use por defecto:

- `RECORDING_SCALE=1280:720`
- `RECORDING_FPS=15`
- `RECORDING_VIDEO_BITRATE=1800k`
- `RECORDING_VIDEO_MAXRATE=2200k`
- `RECORDING_VIDEO_BUFSIZE=3600k`
- `RECORDING_PRESET=veryfast`

Prueba integrada desde endpoints TeleECOE:

- Archivo: `Aquality182257_Ercp_C1_1778541777.mp4`
- Publicado: sí
- `returncode`: 0
- Validación app: `video_valid=true`
- Resolución: 1280x720
- FPS: 15
- Duración: 13.4 s
- Frames: 201
- Bitrate: ~1.54 Mbps
- Decodificación FFmpeg: 0 warnings

## Recomendación

1. Mantener WebRTC como modo principal del visor.
2. Mantener la grabación/evidencia a 720p como nuevo default.
3. Hacer validación visual real en estación 5 con una evaluación corta.
4. Si la prioridad es nitidez máxima en vivo, usar una cámara local real RTSP/ONVIF/USB; Tuya Cloud seguirá teniendo techo de calidad.

No se recomienda volver a MSE como modo principal; WebRTC fue visualmente más estable.
