---
name: session-start
description: Inicia la sesión — Claude lee todo el contexto y presenta el briefing completo
---

Ejecuta el inicio de sesión del proyecto Polymarket de manera AUTÓNOMA.
Tú eres quien sabe el estado del proyecto — no esperes instrucciones del usuario.

PASO 1 — Lee todo el contexto
- Lee CLAUDE.md completo
- Lee el dev_log más reciente en dev_logs/ (si existe)
- Lee research/next-steps.md
- Identifica si hay problemas abiertos sin resolver

PASO 2 — Presenta el briefing exactamente así:

---
## Bienvenido de vuelta — [FECHA HOY]

### Dónde estamos
**Sprint:** [sprint actual]
**Última sesión:** [fecha de última actualización en CLAUDE.md]

### Qué hicimos la sesión anterior
[resumen de los últimos items completados del CLAUDE.md y del último dev_log]

### Problemas pendientes
[problemas abiertos del CLAUDE.md — si no hay, escribir "Ninguno"]

### Primer paso de hoy
[el "Próximo paso EXACTO" del CLAUDE.md — muy específico]

### Goals completos de esta sesión
[lista de goals de la próxima sesión del CLAUDE.md]

---
Arrancamos con: [primer task exacto]. ¿Empezamos?

PASO 3 — Si el usuario dice que sí o no dice nada, arranca directamente
con el primer task. No esperes más confirmación.
