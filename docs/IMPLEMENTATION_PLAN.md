# Plan de implementación

Este documento se usa para convertir cambios solicitados en trabajo técnico concreto.

## Flujo recomendado

1. El usuario edita `docs/CAMBIOS_SOLICITADOS.md`.
2. LUCINA revisa el diff contra Git.
3. LUCINA resume qué cambió y separa:
   - requisitos claros,
   - dudas/bloqueos,
   - riesgos,
   - archivos/funciones probablemente afectados.
4. Si no hay bloqueos, LUCINA implementa.
5. LUCINA verifica con prueba mínima.
6. LUCINA actualiza documentación si aplica.
7. LUCINA hace commit con mensaje claro.

## Estados de trabajo

- `Pendiente`: escrito pero aún no analizado.
- `En análisis`: interpretándose y convirtiéndose en plan.
- `En implementación`: código/documentación en cambio.
- `Bloqueado`: falta decisión, credencial, dato o aprobación.
- `Completado`: implementado, verificado y commiteado.

## Plantilla de plan técnico

```md
## Cambio: <título>

Origen:
- `docs/CAMBIOS_SOLICITADOS.md`, sección: `<nombre>`

Resumen:
- 

Archivos probablemente afectados:
- 

Criterios de aceptación técnicos:
- [ ] 
- [ ] 

Plan:
1. 
2. 
3. 

Pruebas/verificación:
- 

Riesgos:
- 

Estado:
- Pendiente
```

---

## Cambios en curso

_No hay cambios en curso._
