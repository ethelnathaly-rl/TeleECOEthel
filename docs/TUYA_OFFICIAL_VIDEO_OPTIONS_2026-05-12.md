# TeleECOE / Estación 5 RCP - opciones Tuya para video nítido y estable

Fecha: 2026-05-12

## Objetivo

Determinar si TeleECOE puede integrar un flujo de cámara Tuya equivalente al que usa la app Tuya/Smart Life, y comparar esa ruta con la integración actual por go2rtc.

## Resumen ejecutivo

La integración más cercana a la app Tuya no es un simple RTSP/HTTP local: Tuya usa WebRTC con señalización por API + MQTT y credenciales temporales/ICE. La documentación oficial confirma un flujo con backend propio, frontend WebRTC, Tuya OpenAPI y Tuya MQTT.

go2rtc ya implementa básicamente ese mismo patrón para Tuya: obtiene configuración WebRTC, conecta MQTT, negocia offer/answer/candidates y expone el resultado como stream para navegador/RTSP. Por eso, integrar “Tuya oficial WebRTC” directamente en Flask probablemente no va a mejorar automáticamente la calidad respecto a go2rtc si ambos terminan usando el mismo relay/servicio Tuya. Sí podría dar más control de diagnóstico, UI y reconexión, pero aumenta mucho la complejidad.

La opción más prometedora a corto plazo es optimizar y validar la ruta go2rtc actual con `resolution=hd`, WebRTC como visor, reconexión/estado claro, y grabación por FFmpeg transcode con warm-up. La opción más robusta si se exige nitidez estable tipo clínica sigue siendo una fuente local real: RTSP/ONVIF LAN, USB, cámara IP local o capturadora.

## Hallazgos de documentación oficial Tuya

### Servicios oficiales de live stream

Tuya documenta oficialmente el servicio **IoT Video Live Stream** para cámaras IPC. Los protocolos mencionados por Tuya son:

- **WebRTC**
- **RTSP**
- **HLS**

APIs oficiales relevantes encontradas:

- `POST /v1.0/users/{uid}/devices/{device_id}/stream/actions/allocate`
- `POST /v1.0/devices/{device_id}/stream/actions/allocate`
- `GET /v1.0/devices/{device_id}/webrtc-configs`

Para RTSP/HLS, Tuya documenta endpoints que devuelven una URL temporal de stream; los ejemplos incluyen HLS `.m3u8`. Esto abre una ruta oficial relativamente simple para navegador: pedir URL HLS desde backend Flask y reproducirla con `<video>` + `hls.js`, renovando la URL cuando expire.

Para WebRTC, Tuya sí documenta cómo obtener configuración (`supports_webrtc`, ICE/STUN/TURN, `auth`, `moto_id`, `skill`, resolución), pero la señalización completa en web sigue requiriendo backend + MQTT + SDP/candidates. No aparece como un “embed web” directo equivalente a la app Smart Life.

### Flujo oficial WebRTC

La documentación oficial Tuya WebRTC describe estos componentes:

- Tuya Developer Platform para HTTPS APIs.
- Web frontend que usa APIs JavaScript WebRTC para crear offers y candidates.
- Web backend que hospeda la página, obtiene configuración por HTTPS y conecta a Tuya MQTT.
- Tuya MQTT como canal de señalización asíncrona.
- IPC/cámara como extremo de audio/video.

Requisitos principales:

- Cámara vinculada a SmartLife/Tuya.
- Proyecto cloud en Tuya Developer Platform.
- Cuenta de app vinculada al proyecto.
- `clientId` / Access ID y `secret` / Access Secret.
- UID de la cuenta vinculada.
- `deviceId` de la cámara.
- Servicio/API de video autorizado en Tuya Developer Platform.

APIs clave documentadas:

- Generar configuración MQTT: `POST /v1.0/open-hub/access/config` o variante equivalente.
- Obtener configuración WebRTC: `GET /v1.0/users/{uId}/devices/{deviceId}/webrtc-configs`.
- Señalización por MQTT con protocolo WebRTC `302` para `offer`, `candidate`, `answer` y `disconnect`.

El `offer` incluye `stream_type`; en la documentación, el default/sub-stream aparece como `1`. El payload también usa `auth`, `mode: webrtc` y SDP generado por navegador.

### Demo oficial `tuya/webrtc-demo-go`

El demo oficial confirma que no es un embed simple. Requiere:

- `clientId` y `secret` del proyecto Tuya IoT.
- Autorización de cuenta Tuya/Open Platform.
- `deviceId`.
- Backend Go que sirve WebSocket local.
- Frontend JS que usa `RTCPeerConnection`, obtiene ICE servers, envía offer/candidates por WebSocket al backend y recibe answer/candidates.

Detalles importantes del demo:

- El frontend conecta a un WebSocket local `/webrtc`.
- El backend despacha mensajes hacia Tuya MQTT/OpenAPI.
- El JS elimina líneas `a=extmap...` del SDP porque el dispositivo solo acepta payload JSON de hasta ~8 KB.
- El demo pide audio local con `getUserMedia({audio: true, video: false})` para habilitar flujo de audio/video.
- La muestra desactiva verificación de origen WebSocket; para producción habría que cerrarlo.

## Hallazgos de go2rtc / Tuya

### go2rtc ya implementa el patrón oficial

go2rtc soporta protocolo propietario Tuya con WebRTC y audio bidireccional. Soporta dos formas:

1. **Tuya Smart API**: recomendada por go2rtc. Requiere cuenta en app Tuya Smart; Smart Life no está soportado para ese flujo específico de descubrimiento según la documentación de go2rtc.
2. **Tuya Cloud API**: requiere proyecto Tuya Developer Platform, `device_id`, `client_id`, `client_secret`, `uid` y autorización del servicio `IoT Video Live Stream`.

La configuración expuesta por go2rtc para calidad es limitada:

- `resolution=hd` para stream principal, default.
- `resolution=sd` para sub-stream.

La propia documentación de go2rtc advierte que no todas las cámaras soportan stream HD por WebRTC aunque la cámara lo soporte en la app.

### Cómo selecciona HD/SD go2rtc

En el código de go2rtc:

- Si `resolution` está vacío o no es `hd`/`sd`, usa `hd`.
- Mapea stream principal `2` a `stream_type: 0`.
- Mapea substream `4` a `stream_type: 1`.
- Si conecta en HD y el dispositivo soporta cambio de claridad, envía comando de resolución `0` por protocolo `312`.

Esto es relevante porque TeleECOE ya estaba en `resolution=hd` según investigación previa; por tanto, el problema no parece ser que estemos forzando SD.

### Por qué go2rtc puede parecer peor que la app

Aunque go2rtc usa WebRTC Tuya, puede haber diferencias frente a la app oficial:

- La app Tuya puede tener heurísticas propietarias de reconexión/adaptación no documentadas.
- La cámara o Tuya Cloud pueden entregar diferente calidad según cliente, región, NAT o condiciones del relay.
- Si la ruta pasa por relay externo (`mqtt+udp`, remote relay), la calidad queda limitada por Tuya Cloud y red.
- go2rtc reexpone el stream a navegador y RTSP; la ruta RTSP/remux puede revelar errores H.264 que la app oculta o recupera mejor.
- La app probablemente renderiza directo WebRTC con tolerancia a pérdida; grabar evidencia MP4 requiere contenedor y decodificación más estrictos.

## Opciones comparadas

### Opción 0 - HLS oficial vía Tuya Cloud API

**Qué sería:** usar Tuya Cloud API para solicitar una URL HLS temporal (`.m3u8`) y reproducirla en TeleECOE con `<video>` + `hls.js`.

**Ventajas:**

- Es una vía oficial Tuya para web.
- Es más simple que reimplementar WebRTC/MQTT.
- Se puede embeber directamente en una app Flask local.
- Evita que el navegador tenga que entender RTSP.

**Límites:**

- Puede tener más latencia que WebRTC.
- La URL puede ser temporal y requerir renovación robusta.
- No garantiza paridad exacta con Smart Life/Tuya app.
- Sigue dependiendo de Tuya Cloud y de permisos/servicios del proyecto IoT.

**Recomendación:** probar como comparación oficial A/B contra go2rtc. Es la alternativa oficial web más viable.

### Opción 1 - Mantener go2rtc y optimizarlo

**Qué sería:** seguir usando `camara1` en go2rtc con Tuya WebRTC, WebRTC como visor principal en TeleECOE, RTSP local solo para FFmpeg/transcode y validación.

**Ventajas:**

- Ya está integrado.
- Evita reimplementar señalización Tuya.
- Permite visor WebRTC y grabación FFmpeg local.
- La app Flask no maneja secretos Tuya directamente si se mantiene encapsulado en go2rtc.

**Límites:**

- Si Tuya Cloud/relay degrada video, go2rtc no puede recuperar detalle perdido.
- Dependencia de MQTT/relay Tuya; errores como `tuya: mqtt: disconnect` siguen siendo posibles.
- HD depende de si la cámara expone HD por WebRTC.

**Recomendación:** opción base a corto plazo.

### Opción 2 - Integrar Tuya WebRTC oficial directo en TeleECOE

**Qué sería:** crear backend Flask/servicio auxiliar que implemente Tuya OpenAPI + MQTT signaling y frontend WebRTC propio, similar al demo oficial.

**Ventajas:**

- Control total de UI, reconexión, eventos y métricas.
- Podría replicar más fielmente el flujo oficial documentado.
- Permite diagnosticar `video_clarity`, ICE, `skill`, `stream_type`, answer/candidates y reconexiones con más detalle.

**Límites:**

- Alta complejidad y superficie de seguridad: client secret, tokens, MQTT, WebSocket, ICE, SDP, renovación de tokens.
- Probablemente usa la misma infraestructura Tuya y no garantiza mejor nitidez que go2rtc.
- Habría que proteger muy bien credenciales y sesiones.
- La grabación MP4 seguiría necesitando MediaRecorder, servidor de grabación, o FFmpeg desde otra salida.

**Recomendación:** solo como prototipo diagnóstico si go2rtc no permite medir/controlar lo necesario. No lo pondría como ruta principal todavía.

Nota: los SDK oficiales con paridad tipo Smart Life/BizBundle encontrados son principalmente **Android/iOS**, no un SDK web genérico listo para embeber en Flask.

### Opción 3 - Tuya Cloud API `stream/actions/allocate`

**Qué sería:** usar endpoint cloud que asigna URL de stream si el servicio está autorizado.

**Ventajas:**

- Podría devolver una URL de stream manejable por backend.
- Está presente en código de go2rtc para Cloud API.

**Límites:**

- No queda claro que sea mejor que WebRTC ni que entregue una URL apta para embed/grabación estable en navegador local.
- Requiere proyecto cloud y autorización correcta de video.
- Puede tener expiración, restricciones regionales o costos/quotas.

**Recomendación:** investigar solo si se activa Tuya Cloud API formalmente y se puede probar sin exponer credenciales.

### Opción 4 - Capturar/emular app Tuya/Smart Life

**Qué sería:** usar Android/AVD o dispositivo físico con la app Tuya/Smart Life y capturar pantalla/video.

**Ventajas:**

- Es lo más parecido a “lo que ve la app”.
- Puede servir para diagnóstico visual o comparación A/B.

**Límites:**

- No es integración limpia en TeleECOE.
- Automatización frágil, permisos, latencia, posible DRM/black screen, mantenimiento alto.
- Difícil de grabar evidencia sincronizada y estable en producción.

**Recomendación:** útil para comparar calidad, no como arquitectura final.

### Opción 5 - Cámara local real RTSP/ONVIF/USB/IP LAN

**Qué sería:** reemplazar o complementar Tuya con una fuente local directa.

**Ventajas:**

- Mejor control de nitidez, bitrate, FPS y estabilidad.
- Menos dependencia de nube/relay/MQTT.
- Grabación FFmpeg más simple y confiable.

**Límites:**

- Requiere hardware/configuración.
- La cámara Tuya actual no expuso RTSP/ONVIF/HTTP local en pruebas previas.

**Recomendación:** opción más robusta si la exigencia de calidad es estricta.

## Prueba mínima recomendada

Sin tocar credenciales en documentación:

1. Confirmar que el stream go2rtc real está usando `resolution=hd`.
2. Verificar si la API de go2rtc reporta resolución efectiva, codec y FPS cuando el productor está conectado.
3. Probar una sesión WebRTC en `:1984/webrtc.html?src=camara1` y registrar si hay `mqtt: disconnect`.
4. Comparar visualmente en el mismo momento:
   - App Tuya/Smart Life.
   - go2rtc WebRTC directo.
   - TeleECOE iframe WebRTC.
5. Si la app se ve claramente mejor mientras go2rtc no, levantar un prototipo oficial Tuya WebRTC en entorno aislado con credenciales por variables de entorno, solo para comparar calidad/resolución efectiva.
6. Si ambos se ven parecidos o ambos sufren cortes, cambiar de arquitectura hacia cámara local real.

## Conclusión provisional

La investigación apunta a que go2rtc no es una integración “inferior” por diseño; ya implementa el mismo tipo de WebRTC + MQTT que Tuya documenta oficialmente. La diferencia es que Tuya también ofrece URLs RTSP/HLS por Cloud API, y **HLS es la opción oficial más fácil de embeber en una web Flask local**.

Orden recomendado de experimentos:

1. Mantener go2rtc/WebRTC como ruta actual estable y no romper lo que ya funciona.
2. Probar HLS oficial de Tuya Cloud API como comparación A/B en TeleECOE.
3. Solo si HLS mejora claramente la nitidez/estabilidad, convertirlo en modo alternativo o principal.
4. Si HLS tiene mucha latencia o cortes, seguir con go2rtc WebRTC para preview y FFmpeg transcode para evidencia.
5. Si se requiere nitidez garantizada tipo Smart Life/app nativa, evaluar SDK móvil Tuya o, más práctico para TeleECOE, migrar a cámara local real RTSP/ONVIF/USB.
