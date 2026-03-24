---
name: session-end
description: Cierra la sesión — Claude documenta todo solo sin preguntar al usuario
---

Ejecuta el cierre de sesión del proyecto Polymarket de manera AUTÓNOMA.
Tú estuviste presente en toda la sesión — sabes exactamente qué pasó.
NO le preguntes nada al usuario. Documenta tú solo basándote en lo que ocurrió.

PASO 1 — Analiza la sesión completa
Revisa toda la conversación de esta sesión e identifica:
- Qué goals tenía esta sesión (los del CLAUDE.md al inicio)
- Qué se completó efectivamente
- Qué quedó pendiente y por qué
- Qué problemas surgieron y cómo se resolvieron (o si quedaron abiertos)
- Qué decisiones técnicas importantes se tomaron y el razonamiento

PASO 2 — Determina el próximo paso exacto
Basándote en:
- Lo que quedó pendiente de esta sesión
- El plan en research/next-steps.md
- El sprint actual

Define cuál es la primera tarea concreta y específica de la próxima sesión.

PASO 3 — Actualiza CLAUDE.md
Actualiza ÚNICAMENTE la sección "ESTADO ACTUAL" con:
- Fecha de hoy
- Sprint actual (actualizar si cambió)
- Lista de Completado actualizada (agrega lo de hoy con fecha)
- Próximo paso EXACTO (primer task de la próxima sesión, muy específico)
- Problemas conocidos abiertos (los que no se resolvieron)
- Goals de la próxima sesión (3-5 tasks concretos y medibles)
- Nueva fila en la tabla Historial de sesiones

PASO 4 — Crea dev_logs/YYYY-MM-DD.md con la fecha de hoy

Usa exactamente este formato:

# Session Log — [FECHA]

## Sprint
[nombre del sprint]

## Goals que teníamos para esta sesión
[los goals que estaban en CLAUDE.md al inicio]

## Completado hoy
[lista detallada con notas técnicas de cada item]

## Quedó pendiente
[lo que no se completó y por qué exactamente]

## Problemas encontrados
[problema → solución aplicada → si quedó abierto o cerrado]

## Decisiones técnicas tomadas
[decisión → razonamiento → impacto en el proyecto]

## Goals para la próxima sesión
[3-5 tasks concretos en orden de prioridad]

## Estimación próxima sesión
[tiempo estimado en horas]

PASO 5 — Presenta el resumen al usuario

---
## Sesión cerrada

### Completado hoy
[lista]

### Quedó pendiente
[lista — si no hay, escribir "Todo completado"]

### Problemas abiertos
[lista — si no hay, escribir "Ninguno"]

### La próxima sesión arranca con
[el primer task exacto y específico]

### Goals próxima sesión
[lista]

---

PASO 6 — Pregunta una sola vez:
"¿Hay algo que corregir antes de guardar?"

Si el usuario dice que no o no responde en su siguiente mensaje,
guarda los archivos tal como están.
Si corrige algo, aplica la corrección y guarda.
