# Cambios solicitados

Este documento es el lugar principal para escribir pedidos concretos de cambio del producto en lenguaje natural.

Este archivo ya incorpora un backlog recomendado de mejoras para TeleECOE, ordenado por prioridad y por área funcional. La intención es que sirva como lista de trabajo viva: cada cambio puede revisarse, implementarse, verificarse y luego moverse a la sección **Completados** con su commit correspondiente.

## Cómo usarlo

1. Editar este archivo con los cambios deseados.
2. Mantener cada pedido en una sección separada.
3. Cuando termines, avisar en el chat de administración: `ya edité CAMBIOS_SOLICITADOS.md`.
4. LUCINA revisará el diff contra Git, interpretará los cambios, propondrá/ejecutará un plan y dejará commit.
5. Si un cambio ya fue implementado, moverlo desde **Pendientes** hacia **Completados** y anotar el commit.
6. Si un cambio necesita aclaración antes de implementarse, moverlo temporalmente a **En análisis**.

## Reglas

- No escribir contraseñas, tokens, URLs Tuya privadas ni datos sensibles.
- No pegar datos reales de pacientes/alumnos si no es necesario.
- Si un cambio es urgente, marcarlo como `Prioridad: Alta`.
- Si algo es solo una idea, marcarlo como `Estado: Idea`, no como requisito.
- Si hay duda, escribirla explícitamente en `Preguntas / dudas`.
- Mantener las solicitudes en lenguaje natural, sin incluir código de implementación.
- Antes de modificar base de datos, rúbricas, evaluaciones o videos, crear respaldo.
- Las mejoras relacionadas con seguridad, datos reales o videos deben tratarse como prioritarias.

## Plantilla para nuevos pedidos

Copiar y pegar este bloque para cada cambio nuevo:

```md
### Título breve del cambio

Estado: Pendiente
Prioridad: Media
Área/Pantalla: 
Archivo o función si la conoces: 

Descripción:
- 

Resultado esperado:
- 

Criterios de aceptación:
- [ ] 
- [ ] 

Notas / contexto:
- 

Preguntas / dudas:
- 
```

---

## Resumen ejecutivo de prioridades recomendadas

Estas son las líneas principales de mejora recomendadas para TeleECOE:

1. Estabilizar la estación RCP y la grabación de video.
2. Proteger la base de datos con respaldos, validaciones e integridad transaccional.
3. Corregir exportaciones y fortalecer reportes.
4. Agregar seguridad mínima: login, roles, protección de acciones destructivas y CSRF.
5. Mejorar el flujo de tablets para evitar errores durante la evaluación.
6. Mejorar el constructor de rúbricas con vista previa, puntaje máximo y control de cambios.
7. Asegurar operación sin Internet mediante dependencias locales.
8. Crear herramientas de diagnóstico, mantenimiento y cierre de jornada.
9. Preparar el proyecto para GitHub privado sin datos sensibles.
10. Mejorar la experiencia visual y operativa para administradores, evaluadores y técnicos.

---

## Orden recomendado de implementación

### Fase 1: Confiabilidad crítica

Objetivo: asegurar que el sistema pueda usarse sin perder datos, resultados ni videos.

Cambios recomendados:

- Robustecer cierre y validación de videos RCP.
- Agregar diagnóstico de cámara, go2rtc y FFmpeg.
- Crear respaldos automáticos y manuales.
- Corregir exportación desde el dashboard principal.
- Verificar integridad de base de datos.
- Evitar evaluaciones parcialmente guardadas.

### Fase 2: Seguridad mínima

Objetivo: evitar accesos o cambios indebidos dentro de la red local.

Cambios recomendados:

- Agregar inicio de sesión.
- Agregar roles básicos.
- Proteger rutas destructivas.
- Agregar confirmaciones claras antes de borrar o reiniciar.
- Evitar eliminación física cuando haya datos históricos.
- Agregar protección CSRF en formularios.

### Fase 3: Operación durante evaluación

Objetivo: reducir errores humanos durante la jornada ECOE.

Cambios recomendados:

- Mejorar búsqueda y selección de alumnos.
- Confirmar alumno y estación antes de iniciar evaluación.
- Mejorar pantalla de éxito.
- Mostrar claramente si un alumno ya fue evaluado.
- Mejorar estados visuales del dashboard.

### Fase 4: Reportes y analítica

Objetivo: entregar resultados confiables, filtrables y exportables.

Cambios recomendados:

- Mejorar filtros.
- Crear reportes por alumno.
- Crear reportes por estación.
- Crear análisis por criterio.
- Exportar resumen y detalle.
- Crear reportes imprimibles.

### Fase 5: Mantenimiento y evolución

Objetivo: facilitar uso futuro, despliegue y crecimiento.

Cambios recomendados:

- Preparar funcionamiento offline.
- Crear launcher de inicio.
- Crear guía rápida de operación.
- Crear cierre de jornada.
- Agregar soporte para varias jornadas o cohortes.
- Preparar GitHub privado.

---

## Pendientes

---

# Fase 1: Confiabilidad crítica

## 1. Robustecer cierre y validación de videos RCP

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Estación RCP / Grabación de video  
Archivo o función si la conoces: `app/routes/tablet.py`, lógica de FFmpeg, guardado de `video_camara1`

Descripción:
- Mejorar el proceso completo de grabación RCP para evitar archivos MP4 inválidos.
- Actualmente existe un antecedente de video inválido con error `moov atom not found`.
- La grabación no debe considerarse válida hasta que FFmpeg haya cerrado correctamente el archivo.
- El sistema debe evitar asociar a una evaluación un video corrupto, incompleto o vacío.

Resultado esperado:
- El video RCP debe cerrarse correctamente al finalizar la evaluación.
- El archivo final debe ser reproducible.
- La evaluación debe guardar la ruta del video solo si el archivo fue validado.
- Si la grabación falla, el sistema debe registrar el error y mostrar un mensaje claro.

Criterios de aceptación:
- [ ] La grabación se inicia correctamente desde el flujo RCP.
- [ ] La grabación se detiene correctamente al guardar la evaluación.
- [ ] El proceso de FFmpeg termina con estado correcto.
- [ ] El archivo generado existe y tiene tamaño mayor a cero.
- [ ] El archivo MP4 final puede abrirse y reproducirse.
- [ ] El video final tiene duración detectable.
- [ ] No aparece el error `moov atom not found`.
- [ ] La evaluación solo queda asociada a un video validado.
- [ ] Si el video falla, la evaluación no queda marcada falsamente como si tuviera evidencia válida.

Notas / contexto:
- Este cambio es la prioridad técnica más importante del proyecto.
- Se recomienda grabar primero en un archivo temporal y renombrarlo solo cuando esté validado.
- Este cambio debe probarse con una grabación corta y otra de duración similar a una evaluación real.

Preguntas / dudas:
- Definir si una evaluación RCP puede guardarse aunque el video falle.
- Definir si el sistema debe bloquear el guardado o permitirlo con estado “video con error”.

---

## 2. Usar archivo temporal durante la grabación RCP

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Estación RCP / Grabación  
Archivo o función si la conoces: Lógica de creación de archivos de video

Descripción:
- La grabación no debe escribirse directamente como archivo MP4 final.
- Mientras FFmpeg está grabando, el archivo debe considerarse temporal.
- Solo después de detener FFmpeg y validar el video, debe convertirse en archivo final.
- Esto evita que archivos incompletos aparezcan como videos válidos.

Resultado esperado:
- Durante la grabación, el archivo queda marcado como temporal o pendiente.
- Al finalizar correctamente, se renombra como video final.
- Si falla, se conserva como archivo fallido o se limpia según la política definida.
- La evaluación no apunta a un archivo temporal.

Criterios de aceptación:
- [ ] El sistema diferencia video temporal de video final.
- [ ] El video final solo existe después de una validación correcta.
- [ ] Los archivos temporales no se muestran como evidencia válida.
- [ ] Si la grabación falla, queda un estado claro para diagnóstico.
- [ ] No se pierde información útil para investigar fallos.

Notas / contexto:
- Esta mejora está relacionada directamente con el problema de MP4 inválido.
- Ayuda a evitar videos corruptos asociados a evaluaciones.

Preguntas / dudas:
- Definir si los archivos temporales fallidos deben conservarse para diagnóstico o eliminarse automáticamente.

---

## 3. Agregar validación técnica del video después de grabar

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Estación RCP / Validación de evidencia  
Archivo o función si la conoces: Lógica posterior a FFmpeg

Descripción:
- Después de detener la grabación, el sistema debe validar técnicamente el archivo generado.
- La validación debe confirmar que el video existe, tiene tamaño, duración y puede ser leído.
- El objetivo es impedir que un archivo dañado quede registrado como evidencia.

Resultado esperado:
- El sistema valida cada video antes de asociarlo a la evaluación.
- Si el video es válido, queda vinculado a `video_camara1`.
- Si el video es inválido, se informa al evaluador o al técnico.
- El estado del video queda registrado.

Criterios de aceptación:
- [ ] Se confirma que el archivo existe.
- [ ] Se confirma que el archivo tiene tamaño mayor a cero.
- [ ] Se confirma que el archivo tiene duración detectable.
- [ ] Se confirma que el video puede decodificarse.
- [ ] Se registra el resultado de la validación.
- [ ] La evaluación muestra si el video fue validado o falló.

Notas / contexto:
- La validación puede apoyarse en herramientas externas del entorno como FFmpeg o FFprobe, sin exponer detalles técnicos al evaluador.
- Los mensajes técnicos deben quedar disponibles para diagnóstico, no para el usuario final común.

Preguntas / dudas:
- Definir si la validación será obligatoria para finalizar RCP o solo generará advertencia.

---

## 4. Agregar comprobación previa de cámara RCP

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Estación RCP / Pantalla previa  
Archivo o función si la conoces: `tablet_evaluar.html`, visor de cámara, rutas de cámara

Descripción:
- Antes de permitir iniciar una evaluación RCP, el sistema debe comprobar que la cámara esté disponible.
- La pantalla debe mostrar un estado claro de cámara conectada o con error.
- El evaluador no debería iniciar RCP si la cámara no está lista.

Resultado esperado:
- El evaluador ve el estado de cámara antes de empezar.
- Si la cámara está bien, puede iniciar evaluación y grabación.
- Si la cámara falla, aparece una advertencia clara.
- El responsable técnico puede identificar el problema con mayor rapidez.

Criterios de aceptación:
- [ ] La pantalla RCP muestra el estado de la cámara.
- [ ] El sistema diferencia cámara conectada de cámara no disponible.
- [ ] El botón de iniciar evaluación no aparece o queda deshabilitado si la cámara falla.
- [ ] El mensaje de error es comprensible para el evaluador.
- [ ] El detalle técnico queda disponible para diagnóstico.

Notas / contexto:
- La comprobación debe contemplar el flujo actual: Tuya Smart Cloud, go2rtc, RTSP local y FFmpeg.
- No debe mostrarse información sensible, credenciales ni URLs privadas.

Preguntas / dudas:
- Definir cuánto tiempo debe esperar el sistema antes de declarar que la cámara no está disponible.

---

## 5. Separar visualmente “ver cámara” de “iniciar evaluación”

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Estación RCP  
Archivo o función si la conoces: Template de evaluación RCP

Descripción:
- La pantalla RCP debe permitir comprobar visualmente la cámara antes de iniciar la evaluación.
- Ver la cámara no debe significar automáticamente que la evaluación ya empezó.
- El flujo debe ser más claro para el evaluador.

Resultado esperado:
- Primero se muestra alumno y visor de cámara.
- Luego se confirma que la cámara está disponible.
- Después aparece el botón para iniciar evaluación y grabación.
- La rúbrica aparece solo cuando la grabación haya iniciado correctamente.

Criterios de aceptación:
- [ ] El evaluador puede ver la cámara antes de iniciar.
- [ ] La evaluación no empieza automáticamente al cargar la pantalla.
- [ ] El botón de inicio aparece en un momento claro del flujo.
- [ ] La rúbrica no aparece antes de iniciar grabación.
- [ ] Si FFmpeg falla, la rúbrica no queda disponible como si todo estuviera correcto.

Notas / contexto:
- Esto reduce el riesgo de evaluaciones sin evidencia de video.
- También reduce confusión del evaluador durante la estación RCP.

Preguntas / dudas:
- Definir si el administrador puede permitir una evaluación RCP sin video en casos excepcionales.

---

## 6. Mostrar warm-up visible antes de grabación útil en RCP

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Estación RCP  
Archivo o función si la conoces: Flujo de inicio de grabación RCP

Descripción:
- Ya existe un warm-up de 5 segundos para descartar frames iniciales defectuosos.
- El evaluador debe ver una cuenta regresiva o mensaje claro mientras ocurre ese warm-up.
- El sistema debe indicar cuándo la grabación útil realmente comenzó.

Resultado esperado:
- Al presionar iniciar, aparece un mensaje como “Preparando cámara”.
- Se muestra una cuenta regresiva o estado de preparación.
- Cuando termina el warm-up, aparece “Grabando” y se habilita la rúbrica.
- El evaluador sabe cuándo empezar la maniobra evaluada.

Criterios de aceptación:
- [ ] El warm-up no ocurre de forma invisible.
- [ ] El evaluador ve que la cámara se está preparando.
- [ ] El sistema indica claramente cuándo empieza la grabación útil.
- [ ] La rúbrica aparece después del warm-up exitoso.
- [ ] Si el warm-up falla, se muestra error claro.

Notas / contexto:
- Esto evita que se pierda evidencia si el alumno inicia la maniobra antes de tiempo.
- También mejora la coordinación entre evaluador y alumno.

Preguntas / dudas:
- Confirmar si el warm-up debe mantenerse en 5 segundos o hacerse configurable.

---

## 7. Agregar estados explícitos de grabación RCP

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Estación RCP / Diagnóstico  
Archivo o función si la conoces: Lógica de estado de grabación

Descripción:
- El sistema debe manejar estados claros de la grabación, no solo iniciar o detener.
- Esto permitirá saber exactamente qué está ocurriendo durante el flujo RCP.
- Los estados deben servir tanto para interfaz como para diagnóstico.

Resultado esperado:
- La grabación puede tener estados como:
  - No iniciada.
  - Preparando cámara.
  - Grabando.
  - Deteniendo grabación.
  - Validando video.
  - Video guardado correctamente.
  - Error de grabación.
  - Video inválido.
- La interfaz muestra estados simples.
- El diagnóstico técnico conserva detalles.

Criterios de aceptación:
- [ ] Existe un estado visible para el evaluador.
- [ ] Existe un estado registrable para diagnóstico.
- [ ] El sistema distingue entre error de cámara, error de FFmpeg y video inválido.
- [ ] El estado final del video queda asociado a la evaluación.
- [ ] Los mensajes son claros y no exponen información sensible.

Notas / contexto:
- Esto ayudará a resolver problemas de grabación durante pruebas reales.
- También puede servir para reportes posteriores.

Preguntas / dudas:
- Definir si estos estados deben guardarse en base de datos o solo en logs.

---

## 8. Crear pantalla de diagnóstico técnico para RCP

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Administración / Diagnóstico técnico  
Archivo o función si la conoces: Nueva pantalla de diagnóstico

Descripción:
- Crear una pantalla para que el responsable técnico revise el estado de la estación RCP.
- La pantalla debe reunir información útil sin obligar a revisar consola, logs o archivos manualmente.
- Debe ser accesible solo para administrador o técnico cuando existan roles.

Resultado esperado:
- El técnico puede verificar en una sola pantalla si RCP está listo.
- La pantalla muestra cámara, go2rtc, FFmpeg, último video, errores recientes y espacio en disco.
- Sirve para pruebas antes de iniciar una jornada ECOE.

Criterios de aceptación:
- [ ] La pantalla muestra estado de cámara.
- [ ] La pantalla muestra estado de stream local.
- [ ] La pantalla muestra si FFmpeg está disponible.
- [ ] La pantalla muestra último intento de grabación.
- [ ] La pantalla muestra último video generado y su estado.
- [ ] La pantalla muestra espacio disponible en disco.
- [ ] La pantalla no muestra credenciales ni URLs privadas sensibles.

Notas / contexto:
- Esta pantalla es clave para operar el sistema sin depender del desarrollador.
- Debe priorizar mensajes claros tipo semáforo: correcto, advertencia, error.

Preguntas / dudas:
- Definir si esta pantalla estará dentro del módulo Master o en un módulo Técnico separado.

---

## 9. Detectar procesos FFmpeg huérfanos o grabaciones abiertas

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: RCP / Mantenimiento técnico  
Archivo o función si la conoces: Lógica de procesos FFmpeg

Descripción:
- Si Flask se reinicia o falla durante una grabación, puede perder referencia al proceso FFmpeg.
- El sistema debe poder detectar situaciones anómalas relacionadas con grabaciones abiertas.
- Debe evitar que queden procesos huérfanos o archivos incompletos sin control.

Resultado esperado:
- Al iniciar TeleECOE, el sistema puede revisar si hay grabaciones pendientes o archivos temporales.
- El técnico puede ver advertencias si hay procesos o archivos problemáticos.
- El sistema ofrece una forma segura de cerrar, marcar o limpiar estos casos.

Criterios de aceptación:
- [ ] Se detectan archivos temporales de grabación no finalizados.
- [ ] Se informa si hay indicios de grabaciones incompletas.
- [ ] Se evita iniciar una nueva grabación si existe una anterior bloqueando el flujo.
- [ ] Se registra el evento para diagnóstico.
- [ ] La limpieza no borra evidencia válida por accidente.

Notas / contexto:
- Este cambio protege contra fallos de energía, reinicio de Flask o cierre accidental.
- Debe diseñarse con cuidado para no eliminar evidencia útil.

Preguntas / dudas:
- Definir política para archivos temporales antiguos: conservar, mover a carpeta de fallidos o eliminar manualmente.

---

## 10. Crear respaldos automáticos de la base de datos

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Base de datos / Administración / Mantenimiento  
Archivo o función si la conoces: Gestión de `evaluaciones.db`

Descripción:
- TeleECOE debe crear respaldos automáticos de la base de datos.
- La base contiene alumnos, estaciones, rúbricas, evaluaciones y detalles.
- Perder la base durante una jornada sería crítico.

Resultado esperado:
- El sistema crea respaldos con fecha y hora.
- Los respaldos se almacenan en una carpeta segura excluida de Git.
- El administrador puede saber cuándo fue el último respaldo.
- Antes de cambios importantes, se recomienda o ejecuta un respaldo.

Criterios de aceptación:
- [ ] Se crea respaldo automático al iniciar el sistema.
- [ ] Se puede crear respaldo antes de una jornada.
- [ ] Se puede crear respaldo después de una jornada.
- [ ] Los respaldos tienen nombre con fecha y hora.
- [ ] Los respaldos no se suben a Git.
- [ ] El sistema informa si el respaldo falló.

Notas / contexto:
- El archivo `evaluaciones.db` no debe versionarse.
- Los backups tampoco deben subirse al repositorio.
- Debe cuidarse que el respaldo no ocurra mientras una escritura está incompleta.

Preguntas / dudas:
- Definir cuántos respaldos conservar automáticamente.
- Definir si se debe permitir elegir carpeta de respaldo.

---

## 11. Agregar botón de respaldo manual

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Master / Administración / Mantenimiento  
Archivo o función si la conoces: Nueva acción de respaldo

Descripción:
- Además de los respaldos automáticos, el administrador debe poder crear un respaldo manual cuando lo necesite.
- Esto es útil antes de importar alumnos, cambiar rúbricas o iniciar una jornada.

Resultado esperado:
- Existe un botón “Crear respaldo ahora”.
- Al usarlo, el sistema crea una copia de la base con fecha y hora.
- El sistema muestra confirmación clara.
- Si falla, muestra una advertencia útil.

Criterios de aceptación:
- [ ] El botón aparece solo para usuarios autorizados cuando existan roles.
- [ ] El respaldo se crea correctamente.
- [ ] El nombre del respaldo permite identificar fecha y hora.
- [ ] La pantalla confirma la creación del respaldo.
- [ ] Si falla, el error queda registrado para diagnóstico.

Notas / contexto:
- Este cambio es pequeño pero muy valioso para operación real.
- Debe ir acompañado de política de almacenamiento.

Preguntas / dudas:
- Definir si el respaldo manual debe incluir solo la base o también configuración no sensible.

---

## 12. Crear pantalla de estado e integridad de base de datos

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Administración / Mantenimiento  
Archivo o función si la conoces: Nueva pantalla de integridad

Descripción:
- Crear una pantalla que muestre el estado de la base de datos y métricas básicas.
- El administrador debe saber si la base existe, cuánto pesa, cuándo fue respaldada y cuántos registros contiene.

Resultado esperado:
- La pantalla muestra estado general de la base.
- Muestra conteos de alumnos, estaciones, categorías, criterios, evaluaciones y detalles.
- Muestra último respaldo.
- Muestra advertencias si hay inconsistencias.

Criterios de aceptación:
- [ ] Se muestra si `evaluaciones.db` existe.
- [ ] Se muestra tamaño aproximado de la base.
- [ ] Se muestra fecha del último respaldo.
- [ ] Se muestran conteos principales.
- [ ] Se informa si hay posibles inconsistencias.
- [ ] No se exponen datos personales innecesarios.

Notas / contexto:
- Esta pantalla puede formar parte del módulo técnico o de administración.
- Ayuda a validar el sistema antes de una jornada.

Preguntas / dudas:
- Definir qué inconsistencias deben revisarse en primera versión.

---

## 13. Evitar evaluaciones parcialmente guardadas

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Guardado de evaluaciones  
Archivo o función si la conoces: Lógica de guardado de evaluación y detalle

Descripción:
- Cuando se guarda una evaluación, el sistema debe asegurar que evaluación, detalles, puntaje y video queden consistentes.
- Si se está editando una evaluación, borrar detalles anteriores y guardar nuevos debe hacerse de forma segura.
- No debe quedar una evaluación sin detalles por un error intermedio.

Resultado esperado:
- El guardado ocurre de forma atómica.
- Si una parte falla, el sistema revierte o evita dejar datos incompletos.
- El usuario recibe un mensaje claro.
- El error queda registrado para diagnóstico.

Criterios de aceptación:
- [ ] No quedan evaluaciones sin detalles por errores de guardado.
- [ ] No se pierden detalles previos si falla una edición.
- [ ] El puntaje total corresponde a los detalles guardados.
- [ ] La asociación de video no queda en estado contradictorio.
- [ ] Los errores se muestran de forma comprensible.

Notas / contexto:
- Este cambio protege la integridad de los resultados.
- Es especialmente importante en edición de evaluaciones existentes.

Preguntas / dudas:
- Definir si se debe conservar historial de detalles previos antes de reemplazarlos.

---

## 14. Corregir exportación desde dashboard principal

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Master / Dashboard principal / Exportación  
Archivo o función si la conoces: `app/routes/master.py`, `master_dashboard.html`

Descripción:
- La guía del proyecto menciona un bug pendiente en exportación desde el dashboard principal.
- La exportación debe funcionar correctamente porque es una función operativa clave.
- El administrador debe poder descargar resultados sin depender de consultas manuales.

Resultado esperado:
- La exportación desde el dashboard principal genera un archivo correcto.
- El archivo contiene los resultados esperados.
- Los filtros aplicados, si existen, se respetan.
- El archivo puede abrirse en Excel u otra herramienta compatible.

Criterios de aceptación:
- [ ] El botón de exportación funciona.
- [ ] El archivo descargado no está vacío.
- [ ] Los alumnos aparecen correctamente.
- [ ] Las estaciones aparecen correctamente.
- [ ] Los puntajes aparecen correctamente.
- [ ] Los caracteres especiales se muestran bien.
- [ ] Si se aplican filtros, la exportación respeta esos filtros.
- [ ] Si ocurre un error, se muestra mensaje claro.

Notas / contexto:
- Este cambio debe probarse con la base actual y con una base pequeña de prueba.
- Debe evitarse exportar videos o datos innecesarios en este archivo.

Preguntas / dudas:
- Definir si la exportación principal será resumen por alumno, matriz alumno-estación o detalle completo.

---

# Fase 2: Seguridad mínima

## 15. Agregar inicio de sesión

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Seguridad / Acceso al sistema  
Archivo o función si la conoces: Autenticación general

Descripción:
- TeleECOE actualmente se describe como un sistema local sin autenticación.
- Aunque se use en red local, debe evitar que cualquier persona conectada pueda administrar o modificar datos.
- Se requiere un inicio de sesión básico.

Resultado esperado:
- El sistema solicita usuario y contraseña para ingresar a funciones administrativas.
- Las tablets pueden tener acceso controlado según el rol definido.
- El acceso a rutas sensibles queda protegido.

Criterios de aceptación:
- [ ] Existe pantalla de login.
- [ ] El administrador puede iniciar sesión.
- [ ] Las rutas administrativas requieren sesión.
- [ ] El sistema permite cerrar sesión.
- [ ] Las contraseñas no se guardan en texto plano.
- [ ] No se muestran detalles internos si el login falla.

Notas / contexto:
- Este cambio es obligatorio antes de exponer el sistema fuera de un entorno estrictamente controlado.
- La primera versión puede ser simple, pero debe ser segura.

Preguntas / dudas:
- Definir si los evaluadores también tendrán usuario individual o si habrá acceso por estación.

---

## 16. Crear roles básicos de usuario

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Seguridad / Roles  
Archivo o función si la conoces: Gestión de permisos

Descripción:
- No todos los usuarios deben poder hacer lo mismo.
- Se recomienda separar al menos tres roles: administrador, evaluador y técnico.
- Cada rol debe tener permisos claros.

Resultado esperado:
- El administrador gestiona alumnos, estaciones, rúbricas, resultados y exportaciones.
- El evaluador solo registra evaluaciones.
- El técnico revisa diagnóstico, cámara, FFmpeg, backups y estado del sistema.
- Las acciones peligrosas quedan restringidas.

Criterios de aceptación:
- [ ] Existe rol administrador.
- [ ] Existe rol evaluador.
- [ ] Existe rol técnico o equivalente.
- [ ] Las rutas administrativas no están disponibles para evaluadores.
- [ ] Las acciones de diagnóstico no exponen secretos.
- [ ] Las acciones destructivas requieren rol autorizado.

Notas / contexto:
- Los roles pueden implementarse por etapas.
- Primero debe protegerse administración y eliminación de datos.

Preguntas / dudas:
- Definir si un usuario puede tener más de un rol.

---

## 17. Proteger acciones destructivas con confirmación y permisos

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Master / Seguridad / Acciones destructivas  
Archivo o función si la conoces: Rutas de eliminar, reiniciar, borrar, modificar

Descripción:
- Acciones como eliminar alumnos, eliminar estaciones, borrar evaluaciones o reiniciar una evaluación pueden causar pérdida de datos.
- Estas acciones deben pedir confirmación clara y estar restringidas.

Resultado esperado:
- El usuario no puede borrar o reiniciar accidentalmente.
- Las acciones peligrosas requieren permisos adecuados.
- Se muestra una advertencia antes de continuar.
- La acción queda registrada si existe auditoría.

Criterios de aceptación:
- [ ] Eliminar alumno pide confirmación.
- [ ] Eliminar estación pide confirmación.
- [ ] Reiniciar evaluación pide confirmación.
- [ ] Borrar video pide confirmación.
- [ ] Cambiar rúbricas usadas muestra advertencia.
- [ ] Solo usuarios autorizados pueden ejecutar acciones destructivas.
- [ ] Los mensajes explican la consecuencia de la acción.

Notas / contexto:
- Esto debe hacerse antes de usar el sistema en una jornada formal.
- Las confirmaciones deben ser claras y no ambiguas.

Preguntas / dudas:
- Definir si se requerirá escribir una palabra de confirmación para acciones críticas.

---

## 18. Evitar eliminación física de registros con historial

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Master / Alumnos / Estaciones / Rúbricas / Evaluaciones  
Archivo o función si la conoces: Modelos y rutas de eliminación

Descripción:
- No se recomienda borrar físicamente alumnos, estaciones, criterios o evaluaciones que ya tengan historial.
- En su lugar, deben poder archivarse, desactivarse o anularse.
- Esto protege la trazabilidad de resultados.

Resultado esperado:
- Los registros usados en evaluaciones no se eliminan definitivamente.
- Se pueden marcar como inactivos o archivados.
- El historial sigue disponible para reportes.
- Las pantallas normales pueden ocultar registros inactivos.

Criterios de aceptación:
- [ ] Un alumno con evaluaciones no se borra físicamente sin advertencia fuerte.
- [ ] Una estación con evaluaciones no se borra físicamente sin advertencia fuerte.
- [ ] Un criterio usado no desaparece de resultados históricos.
- [ ] Existe estado activo/inactivo o equivalente.
- [ ] Los reportes históricos siguen siendo interpretables.

Notas / contexto:
- Esta mejora también ayuda al versionado de rúbricas.
- Debe revisarse cómo afectará al dashboard y a las tablets.

Preguntas / dudas:
- Definir si habrá una pantalla para ver registros archivados.

---

## 19. Agregar protección CSRF en formularios y rutas destructivas

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Seguridad / Formularios  
Archivo o función si la conoces: Formularios Flask, rutas POST

Descripción:
- Los formularios y rutas que modifican datos deben protegerse contra envíos no autorizados.
- Esto es especialmente importante en acciones destructivas o administrativas.
- Aunque el sistema sea local, la protección mejora la seguridad general.

Resultado esperado:
- Los formularios administrativos usan protección CSRF.
- Las rutas que crean, editan o eliminan datos están protegidas.
- Si un token no es válido, la acción no se ejecuta.
- El usuario ve un mensaje comprensible.

Criterios de aceptación:
- [ ] Formularios de alumnos protegidos.
- [ ] Formularios de estaciones protegidos.
- [ ] Formularios de rúbricas protegidos.
- [ ] Formularios de evaluación protegidos según aplique.
- [ ] Rutas de eliminación protegidas.
- [ ] Rutas de reinicio de evaluación protegidas.
- [ ] El sistema no rompe el flujo normal de tablets.

Notas / contexto:
- Esta mejora debe coordinarse con el login y roles.
- Debe probarse que las tablets sigan funcionando correctamente.

Preguntas / dudas:
- Definir si todas las rutas POST tendrán CSRF o solo las administrativas.

---

## 20. Asegurar configuración segura fuera de pruebas

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Configuración general / Producción local  
Archivo o función si la conoces: Configuración Flask, `.env`, arranque

Descripción:
- El sistema no debe funcionar en modo debug durante una jornada real.
- La configuración debe diferenciar entre desarrollo y operación.
- Deben evitarse mensajes técnicos visibles para usuarios.

Resultado esperado:
- En operación real, `debug` está desactivado.
- Los errores se registran, pero no se muestran con trazas internas al usuario.
- Las variables sensibles siguen fuera del repositorio.
- La configuración de ejemplo no contiene secretos.

Criterios de aceptación:
- [ ] Existe una forma clara de configurar modo desarrollo u operación.
- [ ] El modo operación no muestra depurador.
- [ ] Los errores se muestran con mensajes amigables.
- [ ] Los detalles técnicos quedan en logs.
- [ ] `.env` sigue excluido de Git.
- [ ] `.env.example` documenta variables sin secretos.

Notas / contexto:
- Esto es necesario antes de usar TeleECOE con usuarios reales.
- Debe revisarse junto con GitHub y despliegue local.

Preguntas / dudas:
- Definir nombres finales de los modos: desarrollo, prueba, operación.

---

# Fase 3: Operación durante evaluación

## 21. Mejorar selección de alumnos en tablets

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Selección de alumno  
Archivo o función si la conoces: `tablet_seleccionar.html`, rutas de selección

Descripción:
- El evaluador debe poder encontrar rápidamente al alumno correcto.
- La lista puede crecer y volverse difícil de manejar si hay muchos alumnos.
- Deben agregarse herramientas simples de búsqueda y filtro.

Resultado esperado:
- La tablet permite buscar por nombre.
- La tablet permite buscar por CMP o identificador.
- La tablet permite filtrar por grupo.
- La lista muestra claramente estado evaluado o pendiente.

Criterios de aceptación:
- [ ] Existe buscador por nombre.
- [ ] Existe buscador por identificador o CMP.
- [ ] Existe filtro por grupo.
- [ ] Se ve si el alumno ya fue evaluado en esa estación.
- [ ] Se ve si el alumno está pendiente.
- [ ] La interfaz sigue siendo simple en tablet.

Notas / contexto:
- Esto reduce errores durante la jornada.
- Debe ser cómodo de usar con pantalla táctil.

Preguntas / dudas:
- Definir si la búsqueda será en tiempo real o con botón de buscar.

---

## 22. Confirmar alumno y estación antes de iniciar evaluación

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Inicio de evaluación  
Archivo o función si la conoces: Flujo de evaluación tablet

Descripción:
- Antes de iniciar una evaluación, el sistema debe confirmar claramente quién será evaluado y en qué estación.
- Esto reduce el riesgo de registrar respuestas en el alumno equivocado.

Resultado esperado:
- Antes del formulario, aparece una confirmación con alumno, grupo e estación.
- El evaluador puede continuar o cancelar.
- En RCP, esta confirmación ocurre antes de iniciar grabación.

Criterios de aceptación:
- [ ] Se muestra nombre del alumno.
- [ ] Se muestra identificador o CMP si existe.
- [ ] Se muestra grupo.
- [ ] Se muestra estación.
- [ ] El evaluador confirma antes de continuar.
- [ ] Existe opción para volver atrás.

Notas / contexto:
- Esta mejora es especialmente importante si hay alumnos con nombres parecidos.
- Debe mantenerse rápida para no retrasar la evaluación.

Preguntas / dudas:
- Definir si la confirmación se puede omitir en modo rápido.

---

## 23. Mejorar advertencia cuando ya existe evaluación

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Tablet / Selección de alumno / Edición de evaluación  
Archivo o función si la conoces: Flujo de evaluación existente

Descripción:
- Si un alumno ya tiene evaluación registrada para una estación, el sistema debe advertirlo de forma clara.
- El evaluador debe saber si va a ver, editar, reemplazar o reiniciar una evaluación.

Resultado esperado:
- La tablet muestra “ya evaluado” de forma visible.
- Al seleccionar un alumno evaluado, se muestran opciones claras.
- Reiniciar o reemplazar evaluación requiere permiso o confirmación.

Criterios de aceptación:
- [ ] Los alumnos evaluados se distinguen visualmente.
- [ ] Al abrir uno evaluado, aparece advertencia.
- [ ] Se puede cancelar sin modificar nada.
- [ ] Editar evaluación queda claramente identificado.
- [ ] Reiniciar evaluación no ocurre accidentalmente.
- [ ] Si existen roles, reiniciar requiere permiso autorizado.

Notas / contexto:
- Esto protege resultados ya registrados.
- También ayuda a evitar duplicidad o sobrescritura accidental.

Preguntas / dudas:
- Definir si el evaluador puede editar libremente o solo durante un tiempo limitado.

---

## 24. Mejorar pantalla de éxito después de guardar evaluación

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Tablet / Pantalla de éxito  
Archivo o función si la conoces: `tablet_exito.html`

Descripción:
- La pantalla de éxito debe entregar información suficiente para confirmar que se guardó lo correcto.
- Actualmente se menciona una pantalla de confirmación, pero puede enriquecerse.

Resultado esperado:
- Después de guardar se muestra alumno, estación, puntaje, hora y estado de video si aplica.
- El evaluador puede volver a la lista de alumnos o continuar con otro alumno.
- Si hubo advertencia de video, se muestra claramente.

Criterios de aceptación:
- [ ] Muestra nombre del alumno.
- [ ] Muestra estación.
- [ ] Muestra puntaje obtenido.
- [ ] Muestra hora de guardado.
- [ ] En RCP, muestra estado del video.
- [ ] Tiene botón claro para continuar.
- [ ] No muestra información técnica innecesaria.

Notas / contexto:
- Esto ayuda al evaluador a detectar errores inmediatamente.
- Debe mantenerse simple y legible.

Preguntas / dudas:
- Definir si debe mostrar también puntaje máximo y porcentaje.

---

## 25. Mejorar estados visuales en dashboard principal

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Master / Dashboard principal  
Archivo o función si la conoces: `master_dashboard.html`

Descripción:
- El dashboard principal debe permitir identificar rápidamente qué evaluaciones están pendientes, completas o con error.
- Se recomienda usar estados visuales consistentes.

Resultado esperado:
- El administrador ve el estado de cada alumno por estación.
- Los estados son claros y no dependen solo de texto pequeño.
- Se diferencian evaluaciones pendientes, evaluadas, con error y con video fallido.

Criterios de aceptación:
- [ ] Evaluación pendiente se distingue claramente.
- [ ] Evaluación completada se distingue claramente.
- [ ] Evaluación con error se distingue claramente.
- [ ] RCP con video válido se distingue de RCP con video fallido.
- [ ] Los colores tienen significado consistente.
- [ ] La información sigue siendo legible al imprimir o exportar.

Notas / contexto:
- Se recomiendan colores tipo semáforo, pero también texto para accesibilidad.
- Debe evitarse depender únicamente del color.

Preguntas / dudas:
- Definir lista oficial de estados del dashboard.

---

# Fase 4: Constructor de rúbricas

## 26. Mostrar puntaje máximo por estación y por rúbrica

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Master / Constructor de rúbricas  
Archivo o función si la conoces: `master_constructor.html`

Descripción:
- Mientras se crea o edita una rúbrica, el administrador debe ver el puntaje máximo posible.
- Esto ayuda a detectar errores de configuración.
- También ayuda a comparar estaciones.

Resultado esperado:
- El constructor muestra puntaje máximo total de la estación.
- Si es posible, muestra subtotal por categoría.
- El administrador puede verificar que la rúbrica tiene la escala esperada.

Criterios de aceptación:
- [ ] Se muestra puntaje máximo total.
- [ ] Se muestran subtotales por categoría si aplica.
- [ ] El puntaje cambia al modificar criterios.
- [ ] El sistema advierte si una rúbrica no tiene criterios.
- [ ] El cálculo coincide con el puntaje usado en evaluación.

Notas / contexto:
- Es importante para reportes y análisis.
- Debe contemplar checkbox, rango numérico y selección única.

Preguntas / dudas:
- Definir cómo calcular puntaje máximo en categorías de selección única y rango.

---

## 27. Agregar vista previa de rúbrica como la verá la tablet

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Master / Constructor de rúbricas  
Archivo o función si la conoces: Constructor y template tablet

Descripción:
- El administrador debe poder revisar cómo verá la rúbrica el evaluador antes de usarla.
- Esto reduce errores de diseño, orden, textos o puntajes.

Resultado esperado:
- Existe una opción de “Vista previa”.
- La vista previa muestra categorías y criterios como aparecerán en la tablet.
- No guarda datos ni crea evaluación.

Criterios de aceptación:
- [ ] Existe botón o enlace de vista previa.
- [ ] La vista previa respeta orden de categorías.
- [ ] La vista previa respeta orden de criterios.
- [ ] Muestra tipos de criterio correctamente.
- [ ] No altera datos reales.
- [ ] Es clara para validar antes de una jornada.

Notas / contexto:
- Esta mejora puede evitar errores antes de iniciar evaluaciones reales.
- También sirve para capacitación de evaluadores.

Preguntas / dudas:
- Definir si la vista previa debe simular también el puntaje.

---

## 28. Permitir duplicar estaciones o rúbricas

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Master / Estaciones / Constructor de rúbricas  
Archivo o función si la conoces: Gestión de estaciones y criterios

Descripción:
- Muchas estaciones pueden tener estructuras similares.
- Duplicar una estación o rúbrica ahorraría tiempo y reduciría errores.
- La copia debe poder editarse sin afectar la original.

Resultado esperado:
- El administrador puede duplicar una estación completa con sus categorías y criterios.
- La estación duplicada queda como copia editable.
- No se copian evaluaciones históricas.

Criterios de aceptación:
- [ ] Existe opción para duplicar estación.
- [ ] Se copian categorías.
- [ ] Se copian criterios.
- [ ] Se copian opciones de criterios si existen.
- [ ] No se copian evaluaciones.
- [ ] La copia tiene nombre diferenciado.
- [ ] La copia puede editarse independientemente.

Notas / contexto:
- Útil para crear variaciones de estaciones.
- Debe evitar confusión entre original y copia.

Preguntas / dudas:
- Definir si también se debe duplicar el orden o asignar nuevo orden al final.

---

## 29. Advertir o bloquear cambios peligrosos en rúbricas ya usadas

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Master / Constructor de rúbricas  
Archivo o función si la conoces: Edición de categorías y criterios

Descripción:
- Si una rúbrica ya tiene evaluaciones registradas, modificar criterios o puntajes puede afectar la interpretación histórica.
- El sistema debe advertir antes de cambios peligrosos.
- En algunos casos, debe recomendar duplicar o crear nueva versión.

Resultado esperado:
- Al intentar editar una rúbrica usada, aparece advertencia.
- El administrador entiende el impacto.
- El sistema evita borrar criterios ya usados sin control.
- Los reportes históricos siguen siendo coherentes.

Criterios de aceptación:
- [ ] El sistema detecta si una estación ya tiene evaluaciones.
- [ ] Se advierte antes de modificar criterios usados.
- [ ] Se advierte antes de modificar puntajes usados.
- [ ] Se advierte antes de eliminar categorías usadas.
- [ ] Se ofrece duplicar o versionar como alternativa.
- [ ] No se rompen reportes históricos.

Notas / contexto:
- Esta mejora protege la validez académica de resultados.
- Puede implementarse por etapas.

Preguntas / dudas:
- Definir qué cambios se consideran seguros y cuáles peligrosos.

---

## 30. Implementar versionado de rúbricas

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Master / Rúbricas / Evaluaciones / Reportes  
Archivo o función si la conoces: Modelos de estación, categoría, criterio y evaluación

Descripción:
- Cada evaluación debería quedar asociada a la versión de rúbrica usada en ese momento.
- Esto permite modificar rúbricas futuras sin alterar resultados anteriores.
- Es una mejora importante si TeleECOE se usará en varias jornadas.

Resultado esperado:
- Las rúbricas pueden tener versiones.
- Una evaluación conserva referencia a la versión aplicada.
- Los reportes históricos usan la versión correcta.
- Se puede crear una nueva versión sin romper evaluaciones anteriores.

Criterios de aceptación:
- [ ] Se puede identificar versión de rúbrica.
- [ ] Una evaluación queda asociada a una versión.
- [ ] Las versiones antiguas pueden consultarse.
- [ ] Los cambios nuevos no alteran resultados antiguos.
- [ ] La interfaz explica claramente qué versión está activa.

Notas / contexto:
- Esta mejora puede requerir cambios de modelo de datos.
- Conviene implementarla después de respaldos y seguridad básica.

Preguntas / dudas:
- Definir si el versionado será automático o manual.

---

# Fase 5: Reportes y analítica

## 31. Mejorar filtros del módulo Analytics

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Analytics / Dashboard analítico  
Archivo o función si la conoces: `app/routes/analytics.py`, `analytics_dashboard.html`

Descripción:
- La guía menciona que hay que revisar filtros de analytics.
- Los filtros deben permitir analizar resultados de forma confiable.
- Deben ser coherentes con exportaciones y dashboard principal.

Resultado esperado:
- Analytics permite filtrar por grupo, alumno, estación y estado.
- Los resultados mostrados respetan los filtros.
- Los gráficos y tablas se actualizan correctamente.
- La exportación respeta los mismos filtros cuando aplique.

Criterios de aceptación:
- [ ] Filtro por grupo funciona.
- [ ] Filtro por alumno funciona.
- [ ] Filtro por estación funciona.
- [ ] Filtro por estado funciona si existe.
- [ ] Los conteos se actualizan correctamente.
- [ ] Las gráficas coinciden con las tablas.
- [ ] La exportación coincide con lo filtrado.

Notas / contexto:
- Esta mejora debe probarse con datos reales o una copia de prueba.
- Debe cuidarse que los filtros no oculten errores importantes.

Preguntas / dudas:
- Definir qué filtros serán obligatorios en la primera versión.

---

## 32. Crear reporte individual por alumno

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Analytics / Reportes / Alumno  
Archivo o función si la conoces: Reportes nuevos

Descripción:
- El administrador debería poder consultar el desempeño completo de un alumno.
- El reporte debe resumir estaciones, puntajes y estado de evaluaciones.

Resultado esperado:
- Existe una vista o exportación por alumno.
- Muestra cada estación evaluada.
- Muestra puntaje obtenido, puntaje máximo y porcentaje si aplica.
- Muestra pendientes.
- En RCP, muestra si tiene video válido.

Criterios de aceptación:
- [ ] Se puede seleccionar un alumno.
- [ ] Se muestran todas sus estaciones.
- [ ] Se muestran puntajes.
- [ ] Se muestran pendientes.
- [ ] Se muestra promedio o resumen global.
- [ ] Se indica estado de video RCP si corresponde.
- [ ] Puede imprimirse o exportarse.

Notas / contexto:
- Útil para revisión individual o entrega de resultados.
- Debe evitar mostrar datos no necesarios.

Preguntas / dudas:
- Definir si el reporte individual será imprimible, CSV, PDF o vista web.

---

## 33. Crear reporte por estación

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Analytics / Reportes / Estación  
Archivo o función si la conoces: Reportes nuevos

Descripción:
- El administrador debería poder analizar el desempeño general por estación.
- Esto permite identificar estaciones difíciles o problemas de enseñanza.

Resultado esperado:
- Existe una vista o exportación por estación.
- Muestra alumnos evaluados.
- Muestra promedio, mínimo, máximo y distribución.
- Muestra pendientes.
- Puede incluir análisis de criterios.

Criterios de aceptación:
- [ ] Se puede seleccionar una estación.
- [ ] Se muestran alumnos evaluados.
- [ ] Se muestra promedio.
- [ ] Se muestra puntaje mínimo.
- [ ] Se muestra puntaje máximo.
- [ ] Se muestran pendientes.
- [ ] Puede exportarse.

Notas / contexto:
- Útil para coordinadores y docentes.
- Debe contemplar diferencias de puntaje máximo entre estaciones.

Preguntas / dudas:
- Definir si incluirá gráficos en la primera versión.

---

## 34. Crear análisis por criterio o ítem

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Analytics / Análisis por ítem  
Archivo o función si la conoces: `analytics.py`, consultas de detalle

Descripción:
- El análisis por criterio permite identificar qué habilidades o ítems fallan más.
- Esta información es muy valiosa para retroalimentación docente.
- La guía ya menciona análisis por ítem como función conocida.

Resultado esperado:
- Se puede ver por criterio cuántos alumnos lo lograron o fallaron.
- Se muestran porcentajes de logro.
- Se puede filtrar por estación y grupo.
- El resultado puede exportarse.

Criterios de aceptación:
- [ ] Se lista cada criterio de una estación.
- [ ] Se muestra cantidad de logrados.
- [ ] Se muestra cantidad de no logrados o valores equivalentes.
- [ ] Se muestra porcentaje.
- [ ] Se puede filtrar por grupo.
- [ ] Se puede exportar.
- [ ] El cálculo es coherente con los detalles guardados.

Notas / contexto:
- Debe contemplar tipos de criterio distintos: checkbox, rango y selección única.
- Para criterios no binarios, se debe definir cómo resumir los resultados.

Preguntas / dudas:
- Definir cómo presentar criterios de rango y selección única en el análisis.

---

## 35. Crear exportación completa de resultados

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Analytics / Exportación  
Archivo o función si la conoces: Exportaciones CSV

Descripción:
- Además de exportaciones resumidas, TeleECOE debe permitir exportar resultados completos.
- Esto es útil para análisis externo, respaldo académico y revisión posterior.

Resultado esperado:
- El administrador puede exportar:
  - Resumen por alumno.
  - Resumen por estación.
  - Detalle por criterio.
  - Matriz alumno-estación.
- Las exportaciones son claras y consistentes.

Criterios de aceptación:
- [ ] Existe exportación resumen por alumno.
- [ ] Existe exportación resumen por estación.
- [ ] Existe exportación detalle por criterio.
- [ ] Existe exportación matriz alumno-estación.
- [ ] Los archivos abren correctamente en Excel.
- [ ] Los caracteres especiales se conservan.
- [ ] No se exportan datos sensibles innecesarios.
- [ ] No se exportan videos directamente.

Notas / contexto:
- Exportar no reemplaza los backups.
- Deben documentarse las columnas de cada archivo.

Preguntas / dudas:
- Definir nombres finales de cada tipo de exportación.

---

## 36. Crear reportes imprimibles

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Analytics / Reportes  
Archivo o función si la conoces: Vistas imprimibles o exportación PDF futura

Descripción:
- Además de CSV, sería útil contar con reportes listos para imprimir.
- Pueden servir para actas, revisión docente o entrega interna.

Resultado esperado:
- Existen vistas imprimibles con diseño claro.
- Los reportes no dependen de elementos interactivos.
- Se pueden imprimir desde el navegador.

Criterios de aceptación:
- [ ] Existe reporte imprimible por alumno.
- [ ] Existe reporte imprimible por estación.
- [ ] Existe resumen imprimible de jornada.
- [ ] El diseño se ve bien en papel.
- [ ] No incluye botones ni navegación innecesaria al imprimir.

Notas / contexto:
- Puede implementarse primero como página imprimible, antes de generar PDF.
- Debe respetar privacidad de datos.

Preguntas / dudas:
- Definir si se requiere PDF automático o basta con impresión del navegador.

---

# Fase 6: Gestión de videos

## 37. Definir política de retención de videos

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Administración / Videos / RCP  
Archivo o función si la conoces: Documentación y configuración de videos

Descripción:
- Los videos ocupan espacio y pueden contener información sensible.
- El proyecto debe definir cuánto tiempo se guardan, quién puede verlos y cuándo se eliminan.
- Esta política debe estar documentada.

Resultado esperado:
- Existe una política clara de retención de videos.
- El administrador conoce cuándo conservar o eliminar videos.
- La eliminación, si existe, requiere permisos y confirmación.
- Los videos no se suben a Git ni se exponen accidentalmente.

Criterios de aceptación:
- [ ] Se documenta cuánto tiempo conservar videos.
- [ ] Se define quién puede ver videos.
- [ ] Se define quién puede eliminar videos.
- [ ] Se define qué hacer con videos inválidos.
- [ ] Se define qué hacer con videos huérfanos.
- [ ] La política se refleja en la interfaz o documentación.

Notas / contexto:
- Esto es importante por privacidad y almacenamiento.
- Debe coordinarse con normativa o necesidades institucionales.

Preguntas / dudas:
- Definir duración de conservación: 30 días, hasta cierre de actas, indefinida o configurable.

---

## 38. Mostrar uso de almacenamiento de videos

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Administración / Diagnóstico / Videos  
Archivo o función si la conoces: Pantalla de mantenimiento

Descripción:
- El administrador debe poder saber cuánto espacio ocupan los videos.
- También debe ver cuánto espacio libre queda en disco.
- Esto evita fallos por falta de almacenamiento durante una jornada.

Resultado esperado:
- La pantalla de mantenimiento muestra cantidad de videos, espacio usado y espacio libre.
- Si el espacio libre es bajo, se muestra advertencia.
- La información ayuda a decidir limpieza o respaldo.

Criterios de aceptación:
- [ ] Se muestra cantidad de videos guardados.
- [ ] Se muestra espacio total usado por videos.
- [ ] Se muestra espacio libre disponible.
- [ ] Se muestra advertencia si el espacio es bajo.
- [ ] No se muestran rutas sensibles innecesariamente.

Notas / contexto:
- Esta mejora puede integrarse con diagnóstico RCP.
- Debe ser visible antes de iniciar una jornada.

Preguntas / dudas:
- Definir umbral de advertencia por espacio libre.

---

## 39. Detectar videos huérfanos, faltantes o corruptos

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Administración / Diagnóstico / Videos  
Archivo o función si la conoces: Mantenimiento de archivos de video

Descripción:
- El sistema debe detectar inconsistencias entre base de datos y archivos de video.
- Puede haber videos sin evaluación, evaluaciones que apuntan a archivos inexistentes o videos corruptos.
- Estas situaciones deben ser visibles para el administrador o técnico.

Resultado esperado:
- Existe una revisión de consistencia de videos.
- Se listan videos huérfanos.
- Se listan evaluaciones con video faltante.
- Se listan videos inválidos o corruptos.
- Las acciones de limpieza requieren confirmación.

Criterios de aceptación:
- [ ] Se detectan videos no asociados a evaluaciones.
- [ ] Se detectan evaluaciones que apuntan a videos inexistentes.
- [ ] Se detectan videos con tamaño cero.
- [ ] Se detectan videos inválidos cuando sea posible.
- [ ] Se muestra resumen de problemas.
- [ ] No se eliminan archivos automáticamente sin confirmación.

Notas / contexto:
- Esta mejora complementa la validación de grabación RCP.
- Debe evitar eliminar evidencia por error.

Preguntas / dudas:
- Definir si los videos huérfanos deben moverse a una carpeta de cuarentena.

---

## 40. Agregar visualización de video desde evaluación RCP

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Master / Resultados / Evaluación RCP  
Archivo o función si la conoces: Vista de resultados o detalle de evaluación

Descripción:
- Cuando una evaluación RCP tiene video válido, el administrador debería poder revisarlo desde el sistema.
- No debe depender de buscar manualmente el archivo en carpetas.
- El acceso debe estar protegido.

Resultado esperado:
- La vista de evaluación muestra si hay video.
- Si existe y es válido, se puede reproducir.
- Si falta o está corrupto, se muestra advertencia.
- Solo usuarios autorizados pueden verlo.

Criterios de aceptación:
- [ ] Se muestra estado del video en la evaluación.
- [ ] Se puede abrir o reproducir video válido.
- [ ] Se muestra duración si está disponible.
- [ ] Se advierte si el archivo falta.
- [ ] Se advierte si el archivo es inválido.
- [ ] El acceso respeta roles cuando existan.

Notas / contexto:
- Debe cuidarse privacidad y permisos.
- No debe exponer rutas internas sensibles al usuario común.

Preguntas / dudas:
- Definir si la reproducción será en navegador o mediante descarga local controlada.

---

# Fase 7: Operación offline e instalación local

## 41. Eliminar dependencia de CDN para operación sin Internet

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Frontend / Base visual / Analytics  
Archivo o función si la conoces: `base.html`, librerías Bootstrap, Chart.js u otras

Descripción:
- TeleECOE debe funcionar aunque no haya Internet.
- Si Bootstrap, Chart.js u otras librerías se cargan desde CDN, algunas pantallas podrían fallar o verse mal.
- Las dependencias necesarias deben estar disponibles localmente.

Resultado esperado:
- Las pantallas mantienen estilos y gráficos sin Internet.
- Las librerías externas necesarias se sirven desde el propio proyecto.
- El sistema puede usarse en red local aislada.

Criterios de aceptación:
- [ ] El sistema carga estilos sin Internet.
- [ ] El sistema carga gráficos sin Internet.
- [ ] No hay errores por CDN inaccesible.
- [ ] Las dependencias locales están organizadas.
- [ ] La documentación indica que el sistema puede operar offline.
- [ ] No se incluyen librerías innecesarias o pesadas sin control.

Notas / contexto:
- Esta mejora es importante para jornadas en lugares con conectividad limitada.
- Debe respetarse licenciamiento de librerías.

Preguntas / dudas:
- Definir qué librerías exactas se usan actualmente desde CDN.

---

## 42. Crear pantalla de estado general del sistema

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Master / Estado del sistema  
Archivo o función si la conoces: Nueva pantalla de estado

Descripción:
- Antes de iniciar una jornada, el administrador necesita saber si el sistema está listo.
- Una pantalla tipo semáforo ayudaría a revisar componentes críticos.

Resultado esperado:
- La pantalla muestra estado de base de datos, backups, cámara, FFmpeg, go2rtc, espacio en disco y red local.
- Cada elemento aparece como correcto, advertencia o error.
- La pantalla sirve como checklist pre-jornada.

Criterios de aceptación:
- [ ] Se muestra estado de base de datos.
- [ ] Se muestra estado de último respaldo.
- [ ] Se muestra estado de cámara RCP.
- [ ] Se muestra estado de FFmpeg.
- [ ] Se muestra estado de go2rtc o stream local.
- [ ] Se muestra espacio disponible.
- [ ] Se muestran advertencias claras.
- [ ] No se muestran secretos ni URLs privadas.

Notas / contexto:
- Puede combinarse con diagnóstico RCP y mantenimiento.
- Debe ser fácil de entender para un responsable no programador.

Preguntas / dudas:
- Definir si será una pantalla independiente o parte del dashboard principal.

---

## 43. Crear modo pre-jornada ECOE

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Administración / Preparación de jornada  
Archivo o función si la conoces: Nueva pantalla o flujo operativo

Descripción:
- Antes de iniciar una evaluación real, el sistema debería ofrecer una revisión guiada.
- Este modo ayuda a confirmar que todo está cargado y operativo.

Resultado esperado:
- El administrador puede revisar:
  - Alumnos cargados.
  - Estaciones cargadas.
  - Rúbricas completas.
  - Cámara RCP lista.
  - Espacio disponible.
  - Último respaldo.
  - Red local.
- El sistema muestra si hay elementos pendientes.

Criterios de aceptación:
- [ ] Se muestra cantidad de alumnos.
- [ ] Se muestra cantidad de estaciones.
- [ ] Se indica si hay estaciones sin rúbrica.
- [ ] Se indica estado de RCP.
- [ ] Se indica último respaldo.
- [ ] Se indica espacio disponible.
- [ ] Se muestra resultado general: listo, advertencias o no listo.

Notas / contexto:
- Puede implementarse después de las pantallas de diagnóstico.
- Es muy útil para el día de la evaluación.

Preguntas / dudas:
- Definir si el modo pre-jornada debe impedir iniciar evaluaciones si hay errores críticos.

---

## 44. Crear launcher o inicio simple para Windows

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Instalación / Operación local  
Archivo o función si la conoces: Arranque del proyecto

Descripción:
- El sistema debería ser fácil de iniciar por una persona no técnica.
- Un acceso de inicio ayudaría a levantar TeleECOE sin usar comandos manuales.
- Debe mostrar la URL que deben abrir las tablets.

Resultado esperado:
- Existe un mecanismo simple para iniciar TeleECOE.
- Al iniciar, se verifica configuración básica.
- Se muestra la URL local del sistema.
- Si algo falla, se indica el problema.

Criterios de aceptación:
- [ ] El usuario puede iniciar TeleECOE con una acción simple.
- [ ] Se muestra que el servidor está activo.
- [ ] Se muestra URL para PC maestra.
- [ ] Se muestra URL para tablets.
- [ ] Se informa si falta configuración.
- [ ] Se informa si la base de datos no existe.

Notas / contexto:
- Esto puede ser un archivo de inicio o una solución más formal en el futuro.
- No debe incluir secretos.

Preguntas / dudas:
- Definir si la primera versión será un acceso simple, un script o un instalador.

---

## 45. Crear guía rápida de operación

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Documentación / Operación  
Archivo o función si la conoces: `docs/` documentación nueva o existente

Descripción:
- Además de la guía completa, se necesita una guía corta para el día de la evaluación.
- Debe ser entendible para administrador, evaluador y técnico.
- Debe listar pasos antes, durante y después de la jornada.

Resultado esperado:
- Existe una guía rápida con pasos concretos.
- Incluye preparación, verificación, uso en tablets, RCP, backups y cierre.
- No contiene datos sensibles.

Criterios de aceptación:
- [ ] Incluye pasos para encender y abrir TeleECOE.
- [ ] Incluye cómo verificar red local.
- [ ] Incluye cómo probar cámara RCP.
- [ ] Incluye cómo entregar URL a tablets.
- [ ] Incluye cómo crear respaldo.
- [ ] Incluye qué hacer si falla RCP.
- [ ] Incluye cierre de jornada.

Notas / contexto:
- Esta guía debe ser corta y práctica.
- Puede llamarse `GUIA_RAPIDA_OPERACION.md`.

Preguntas / dudas:
- Definir si la guía será para administrador, evaluador, técnico o una versión por rol.

---

# Fase 8: Auditoría y trazabilidad

## 46. Registrar fecha y hora de evaluaciones

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Evaluaciones / Base de datos / Reportes  
Archivo o función si la conoces: Modelo de evaluación

Descripción:
- Las evaluaciones deben registrar cuándo fueron creadas y modificadas.
- Esto mejora trazabilidad y permite reportes por fecha.
- También ayuda a investigar problemas.

Resultado esperado:
- Cada evaluación registra fecha y hora de creación.
- Cada evaluación registra fecha y hora de última edición.
- Si aplica, se registra hora de inicio y fin de evaluación.

Criterios de aceptación:
- [ ] Se guarda fecha/hora de creación.
- [ ] Se guarda fecha/hora de última edición.
- [ ] Se muestra esta información en vistas administrativas.
- [ ] Se puede usar para filtros o reportes futuros.
- [ ] No rompe evaluaciones existentes.

Notas / contexto:
- Puede requerir migración de base de datos.
- Debe definirse cómo tratar evaluaciones antiguas sin fecha.

Preguntas / dudas:
- Definir si se usará hora local de la PC maestra.

---

## 47. Registrar quién evaluó

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Evaluaciones / Seguridad / Reportes  
Archivo o función si la conoces: Modelo de evaluación y usuarios

Descripción:
- Si se agregan usuarios o roles, cada evaluación debe registrar quién la realizó.
- Esto permite trazabilidad académica.
- También ayuda a resolver dudas posteriores.

Resultado esperado:
- Cada evaluación puede asociarse a un evaluador.
- Los reportes pueden mostrar evaluador cuando corresponda.
- La edición de evaluaciones también queda trazable.

Criterios de aceptación:
- [ ] Una evaluación nueva guarda evaluador responsable.
- [ ] Una edición registra quién editó.
- [ ] La información aparece en vista administrativa.
- [ ] Los evaluadores no pueden modificar identidad manualmente.
- [ ] No se expone información innecesaria en tablets.

Notas / contexto:
- Depende de la implementación de login y roles.
- Puede hacerse en una segunda etapa de seguridad.

Preguntas / dudas:
- Definir si cada tablet tendrá un evaluador asignado o si se elegirá al ingresar.

---

## 48. Crear historial de cambios de evaluaciones

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Evaluaciones / Auditoría  
Archivo o función si la conoces: Historial de evaluación

Descripción:
- Cuando una evaluación se edita, debería quedar registro del cambio.
- Esto protege la trazabilidad de resultados.
- Es especialmente útil si se permite editar después de guardar.

Resultado esperado:
- Se registra cuándo se editó una evaluación.
- Se registra quién la editó.
- Se registra motivo de edición si se solicita.
- Se puede consultar historial básico desde administración.

Criterios de aceptación:
- [ ] Se registra evento de edición.
- [ ] Se registra usuario responsable cuando existan usuarios.
- [ ] Se registra fecha y hora.
- [ ] Se puede agregar motivo.
- [ ] El historial no puede editarse desde interfaz común.
- [ ] El historial no rompe reportes actuales.

Notas / contexto:
- Puede implementarse después de login y timestamps.
- Ayuda a auditoría académica.

Preguntas / dudas:
- Definir si se guardarán valores anteriores completos o solo eventos de cambio.

---

## 49. Registrar datos específicos de grabación RCP

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: RCP / Evaluaciones / Videos  
Archivo o función si la conoces: Modelo de evaluación o modelo de video

Descripción:
- Además de la ruta del video, conviene registrar datos de grabación.
- Esto ayuda a validar evidencia y resolver fallos.

Resultado esperado:
- Para RCP se registra hora de inicio de grabación.
- Se registra hora de fin.
- Se registra duración estimada.
- Se registra estado de validación del video.
- Se registra mensaje técnico si falla.

Criterios de aceptación:
- [ ] Se guarda hora de inicio de grabación.
- [ ] Se guarda hora de fin de grabación.
- [ ] Se guarda duración del video si está disponible.
- [ ] Se guarda estado de validación.
- [ ] Se guarda error técnico resumido si falla.
- [ ] La vista administrativa muestra estado de forma clara.

Notas / contexto:
- Esta mejora complementa la robustez de RCP.
- Debe cuidarse no mostrar mensajes técnicos innecesarios al evaluador.

Preguntas / dudas:
- Definir si estos campos vivirán en Evaluación o en una tabla separada de Video.

---

# Fase 9: Experiencia visual y mensajes

## 50. Renombrar visualmente toda la app a TeleECOE

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Interfaz general / Documentación visible  
Archivo o función si la conoces: Templates y textos visibles

Descripción:
- El proyecto antes se llamaba `SistemaEvaluacion v2`.
- La interfaz debe usar consistentemente el nombre TeleECOE.
- Esto mejora identidad y reduce confusión.

Resultado esperado:
- El nombre TeleECOE aparece en encabezados, títulos, navegación y mensajes.
- No quedan textos visibles con el nombre anterior.
- La documentación operativa usa el nombre actual.

Criterios de aceptación:
- [ ] Título de la aplicación dice TeleECOE.
- [ ] Encabezados principales dicen TeleECOE.
- [ ] Páginas Master usan TeleECOE.
- [ ] Páginas Tablet usan TeleECOE.
- [ ] Reportes usan TeleECOE.
- [ ] No queda el nombre anterior en la interfaz visible.

Notas / contexto:
- Debe revisarse que no se cambien nombres técnicos internos si no es necesario.
- El cambio visual no debe romper rutas ni archivos.

Preguntas / dudas:
- Definir si el nombre anterior debe quedar mencionado solo en documentación histórica.

---

## 51. Mejorar mensajes de error para usuarios

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Interfaz general / Errores  
Archivo o función si la conoces: Manejo de errores y mensajes flash

Descripción:
- Los usuarios no deben ver errores técnicos crudos.
- Los mensajes deben explicar qué pasó y qué hacer.
- El detalle técnico debe quedar para diagnóstico.

Resultado esperado:
- El evaluador ve mensajes simples y accionables.
- El administrador ve mensajes claros.
- El técnico puede revisar detalles en diagnóstico o logs.
- No se exponen rutas, credenciales ni trazas internas.

Criterios de aceptación:
- [ ] Error de cámara muestra mensaje amigable.
- [ ] Error de FFmpeg muestra mensaje amigable.
- [ ] Error de base de datos muestra mensaje amigable.
- [ ] Error de guardado muestra mensaje amigable.
- [ ] Los detalles técnicos quedan registrados.
- [ ] No se muestran secretos ni rutas sensibles innecesarias.

Notas / contexto:
- Esto mejora mucho la operación durante una jornada.
- Debe aplicarse especialmente en RCP y guardado de evaluaciones.

Preguntas / dudas:
- Definir tono final de mensajes: formal, breve, técnico o mixto.

---

## 52. Estandarizar colores y estados visuales

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Interfaz general / Dashboard / Tablet / Analytics  
Archivo o función si la conoces: Templates y estilos

Descripción:
- Los estados del sistema deben tener una representación visual consistente.
- Esto ayuda a interpretar rápidamente pendientes, completados y errores.

Resultado esperado:
- Se define una convención visual para estados.
- La misma convención se usa en Master, Tablet y Analytics.
- Se usa texto además de color para accesibilidad.

Criterios de aceptación:
- [ ] Pendiente tiene estilo consistente.
- [ ] Evaluado tiene estilo consistente.
- [ ] Error tiene estilo consistente.
- [ ] En proceso tiene estilo consistente.
- [ ] Inactivo o archivado tiene estilo consistente.
- [ ] La interfaz no depende solo del color.

Notas / contexto:
- Puede hacerse junto con mejora del dashboard principal.
- Debe mantenerse sobrio y claro.

Preguntas / dudas:
- Definir paleta visual final y nombres de estados.

---

# Fase 10: Gestión de alumnos, jornadas y datos

## 53. Importar alumnos desde CSV o Excel

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Master / Alumnos / Importación  
Archivo o función si la conoces: Gestión de alumnos

Descripción:
- Cargar alumnos manualmente puede ser lento y propenso a errores.
- El sistema debería permitir importar una lista desde CSV o Excel.
- Deben validarse duplicados y campos obligatorios.

Resultado esperado:
- El administrador puede subir una lista de alumnos.
- El sistema muestra vista previa antes de importar.
- Se detectan duplicados.
- Se informa cuántos alumnos se crearán o actualizarán.

Criterios de aceptación:
- [ ] Se permite cargar archivo de alumnos.
- [ ] Se validan columnas necesarias.
- [ ] Se muestra vista previa.
- [ ] Se detectan duplicados por identificador o nombre.
- [ ] Se confirma antes de importar.
- [ ] Se crea respaldo antes de importación.
- [ ] Se muestra resumen final.

Notas / contexto:
- Esta mejora es útil para jornadas con muchos alumnos.
- Debe definirse formato oficial de importación.

Preguntas / dudas:
- Definir si el formato inicial será CSV, Excel o ambos.

---

## 54. Agregar concepto de jornada, cohorte o evento ECOE

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Modelo de datos / Administración / Reportes  
Archivo o función si la conoces: Modelos y filtros

Descripción:
- Si TeleECOE se usa varias veces, conviene separar evaluaciones por jornada o evento.
- Esto evita mezclar resultados de distintas fechas o cohortes.
- Puede mejorar reportes y archivo histórico.

Resultado esperado:
- Existe una entidad o campo para jornada, cohorte o evento.
- Alumnos, estaciones o evaluaciones pueden asociarse a una jornada.
- Los reportes pueden filtrarse por jornada.
- Se puede cerrar una jornada sin afectar otras.

Criterios de aceptación:
- [ ] Se puede crear una jornada.
- [ ] Se puede seleccionar jornada activa.
- [ ] Las evaluaciones quedan asociadas a una jornada.
- [ ] Los reportes filtran por jornada.
- [ ] El dashboard muestra la jornada activa.
- [ ] No se mezclan resultados de jornadas distintas.

Notas / contexto:
- Esta mejora puede requerir cambios significativos en base de datos.
- Conviene implementarla después de respaldos, reportes y seguridad mínima.

Preguntas / dudas:
- Definir nombre final: jornada, evento, cohorte o evaluación.

---

## 55. Crear función de cierre de jornada ECOE

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Administración / Cierre de jornada  
Archivo o función si la conoces: Nueva función operativa

Descripción:
- Al terminar una jornada, el administrador debería poder ejecutar un cierre.
- El cierre debe verificar pendientes, respaldar datos y generar exportaciones.
- Esto ayuda a formalizar el fin del proceso.

Resultado esperado:
- El sistema revisa evaluaciones completas e incompletas.
- Crea respaldo final.
- Genera exportaciones principales.
- Verifica videos RCP.
- Muestra resumen de cierre.

Criterios de aceptación:
- [ ] Se listan evaluaciones pendientes.
- [ ] Se listan evaluaciones completadas.
- [ ] Se revisan videos RCP.
- [ ] Se crea respaldo final.
- [ ] Se generan exportaciones clave.
- [ ] Se muestra resumen final.
- [ ] El administrador confirma el cierre.

Notas / contexto:
- Puede combinarse con modo solo lectura.
- Debe definirse si cerrar jornada bloquea ediciones.

Preguntas / dudas:
- Definir si el cierre será reversible o no.

---

## 56. Crear modo solo lectura después del cierre

Estado: Idea  
Prioridad: Media  
Área/Pantalla: Administración / Seguridad / Jornadas  
Archivo o función si la conoces: Control de edición

Descripción:
- Después de cerrar una jornada, los resultados deberían quedar protegidos.
- El modo solo lectura evita modificaciones accidentales.
- Las correcciones posteriores, si se permiten, deberían quedar auditadas.

Resultado esperado:
- Una jornada cerrada no permite editar evaluaciones normalmente.
- Los reportes siguen disponibles.
- Las exportaciones siguen disponibles.
- Solo un administrador autorizado puede reabrir o corregir.

Criterios de aceptación:
- [ ] Se puede marcar una jornada como cerrada.
- [ ] Las evaluaciones cerradas no se editan desde flujo normal.
- [ ] Los reportes siguen accesibles.
- [ ] Las exportaciones siguen accesibles.
- [ ] Cualquier reapertura requiere confirmación.
- [ ] La corrección posterior queda registrada.

Notas / contexto:
- Depende de implementar jornadas o un mecanismo equivalente.
- Mejora trazabilidad académica.

Preguntas / dudas:
- Definir si el modo solo lectura será por jornada o global.

---

# Fase 11: GitHub, documentación y mantenimiento

## 57. Preparar repositorio privado en GitHub

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Git / GitHub / Mantenimiento  
Archivo o función si la conoces: Configuración de repositorio

Descripción:
- El proyecto ya tiene Git local, pero GitHub aún no está creado ni conectado.
- El repositorio remoto debe ser privado.
- Antes del primer push, hay que confirmar que no se suban datos sensibles.

Resultado esperado:
- Existe repositorio privado en GitHub.
- El remoto está conectado correctamente.
- El primer push no incluye base de datos, videos, secretos ni archivos pesados.
- La documentación indica cómo trabajar con el repositorio.

Criterios de aceptación:
- [ ] Repositorio creado como privado.
- [ ] Remoto agregado correctamente.
- [ ] Rama principal sincronizada.
- [ ] `.gitignore` protege archivos sensibles.
- [ ] No se sube `evaluaciones.db`.
- [ ] No se suben videos.
- [ ] No se sube `.env`.
- [ ] No se sube `go2rtc.yaml` real.

Notas / contexto:
- Se recomienda revisar historial antes de subir.
- Si hubo secretos en commits anteriores, deben limpiarse antes del push.

Preguntas / dudas:
- Definir nombre final del repositorio en GitHub.

---

## 58. Revisar secretos y archivos sensibles antes del primer push

Estado: Pendiente  
Prioridad: Alta  
Área/Pantalla: Git / Seguridad / Repositorio  
Archivo o función si la conoces: `.gitignore`, historial Git

Descripción:
- Antes de publicar el repositorio privado, hay que revisar que no existan secretos o datos reales en archivos versionados.
- Aunque el repositorio sea privado, no debe contener datos sensibles innecesarios.

Resultado esperado:
- Se revisan archivos versionados.
- Se revisa historial básico.
- Se confirma que no hay credenciales, base de datos, videos ni logs.
- Se documenta el resultado.

Criterios de aceptación:
- [ ] `.env` no está versionado.
- [ ] `go2rtc.yaml` real no está versionado.
- [ ] `evaluaciones.db` no está versionado.
- [ ] MP4 no están versionados.
- [ ] Logs no están versionados.
- [ ] Backups no están versionados.
- [ ] Scripts con credenciales no están versionados.
- [ ] Solo quedan ejemplos seguros.

Notas / contexto:
- Este cambio debe ejecutarse antes del primer push a GitHub.
- Los archivos de ejemplo sí pueden quedar si no contienen secretos.

Preguntas / dudas:
- Definir si se usará alguna herramienta adicional de revisión de secretos.

---

## 59. Mantener documentación viva del proyecto

Estado: Pendiente  
Prioridad: Media  
Área/Pantalla: Documentación / `docs/`  
Archivo o función si la conoces: Documentos del proyecto

Descripción:
- La documentación debe actualizarse junto con los cambios importantes.
- Esto permite que el proyecto sea mantenible.
- Los documentos actuales ya son una buena base.

Resultado esperado:
- Cada cambio importante actualiza documentación relevante.
- El estado del proyecto se mantiene actualizado.
- Las decisiones técnicas quedan registradas.
- Las instrucciones de uso reflejan la versión real.

Criterios de aceptación:
- [ ] Cambios funcionales actualizan guía o especificación.
- [ ] Cambios técnicos actualizan plan o estado.
- [ ] Decisiones importantes se registran.
- [ ] Cambios de seguridad se documentan.
- [ ] Cambios de operación se incluyen en guía rápida.
- [ ] La documentación no contiene secretos.

Notas / contexto:
- Documentos relevantes:
  - Guía completa.
  - Cambios solicitados.
  - Product spec.
  - Decision log.
  - Implementation plan.
  - Project status.
  - GitHub setup.

Preguntas / dudas:
- Definir quién actualiza documentación después de cada implementación.

---

## 60. Crear checklist de verificación antes de cada commit importante

Estado: Idea  
Prioridad: Baja  
Área/Pantalla: Git / Mantenimiento / Calidad  
Archivo o función si la conoces: Documentación de flujo de trabajo

Descripción:
- Antes de cada commit importante, conviene revisar que no se introduzcan errores o archivos sensibles.
- Un checklist simple ayuda a mantener calidad.

Resultado esperado:
- Existe una lista breve de verificación antes de commitear.
- Incluye pruebas básicas, revisión de secretos, documentación y estado del proyecto.

Criterios de aceptación:
- [ ] Checklist documentado.
- [ ] Incluye revisar `.gitignore`.
- [ ] Incluye revisar que no haya base de datos ni videos.
- [ ] Incluye probar flujo afectado.
- [ ] Incluye actualizar documentación si aplica.
- [ ] Incluye describir claramente el commit.

Notas / contexto:
- Esto mejora disciplina del proyecto sin complicarlo demasiado.

Preguntas / dudas:
- Definir si el checklist vivirá en `docs/` o en el propio `CAMBIOS_SOLICITADOS.md`.

---

## En análisis

_Cambios que LUCINA está leyendo o convirtiendo en plan._

---

## En implementación

_Cambios que ya están siendo trabajados._

---

## Completados

_Cuando un cambio quede implementado y commiteado, mover aquí con referencia al commit._
