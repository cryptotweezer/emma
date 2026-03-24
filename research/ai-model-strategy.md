# Estrategia de modelos de IA — Plan definitivo

**Fecha:** 2026-03-21
**Conclusión principal:** Velocidad del LLM NO es factor crítico en Fase 1

---

## Dos usos distintos de IA en el proyecto

### Uso 1 — Desarrollo (Claude Code)
- Herramienta: Claude Code con plan Pro del usuario
- Costo: $0 — incluido en suscripción existente
- Uso: Escribir código, debuggear, planear, documentar
- NO consume tokens de API

### Uso 2 — Bot en producción (OpenClaw)
- Herramienta: Groq API (primario) + OpenRouter (fallback)
- Costo: $0 en free tier, máximo $5-10/mes en producción
- Uso: Analizar señales, tomar decisiones de trading, monitoreo

---

## Por qué la velocidad del LLM NO es crítica en Fase 1

Nuestra estrategia de Fase 1 opera en mercados de política y eventos
long-term donde los precios se mueven en horas o días, no en segundos.

El bot puede tardar 3-5 segundos en analizar y decidir sin impacto en el edge.

Lo que SÍ importa para la velocidad:
- Velocidad de ejecución de órdenes → manejada por Simmer SDK / CLOB
- Latencia de lectura del order book → manejada por WebSocket directo
- Ninguno de estos pasa por un LLM

El único caso donde la velocidad del LLM importaría:
- Mercados BTC 5-min (Fase 2) → pero ahí usaremos señales pre-calculadas

---

## Evaluación de opciones disponibles

### Plan Pro Claude (usuario) — Para desarrollo
- Uso: Claude Code para escribir y mantener el código
- Costo: Ya pagado, $0 adicional
- Limitación: No tiene API de tokens directa
- Conclusión: Perfecto para desarrollo, no usar para el bot

### Kimi K2 free API — Para análisis
- Free tier: 6 RPM, 3M tokens/día
- Suficiente para: Paper trading, Sprints 0-1
- Limitación: 6 RPM = cuello de botella en producción 24/7
- Conclusión: Usar via Groq es mejor que directo

### Plan Go OpenAI — NO aplica
- El plan Go es para uso en ChatGPT web, sin acceso a API
- Para API de OpenAI se necesita pagar por tokens separado
- Alternativas gratuitas son mejores
- Conclusión: No usar para el bot

### Groq ⭐ OPCIÓN PRINCIPAL
- Velocidad: 500-1000 tokens/segundo (LPU chips)
- Free tier: 1,000 req/día, sin costo
- Modelos disponibles: Llama 3.3 70B, Kimi K2, Qwen3 32B
- OpenAI compatible: sí, drop-in replacement
- OpenClaw compatible: sí, soporte nativo
- Costo producción: ~$0.59/M tokens → ~$3-5/mes con uso normal
- Conclusión: OPCIÓN PRINCIPAL para el bot

### OpenRouter — Fallback
- Free tier: 27+ modelos, 50 req/día gratis
- Modelos gratis: Gemini Flash, Llama 3.3 70B, DeepSeek V3.2
- $10 único → 1,000 req/día
- OpenClaw compatible: sí
- Conclusión: FALLBACK cuando Groq se limita

---

## Costo real del LLM — cálculo concreto

Bot de arbitrage de información — uso estimado:
- Escaneo de mercados: ~50 llamadas/día × ~2K tokens = 100K tokens/día
- Análisis de señales: ~20 llamadas/día × ~3K tokens = 60K tokens/día
- Total: ~160K tokens/día = ~5M tokens/mes

Costo con Groq:
- Free tier: $0/mes (hasta límite diario)
- Groq paid si necesario: 5M × $0.59/M = ~$3/mes

Comparación con alternativas costosas:
- Claude Opus 4.6 API: 5M × $15/M = $75/mes → NO viable
- Claude Sonnet 4.6 API: 5M × $3/M = $15/mes → aceptable si fuera necesario
- Groq Llama 3.3 70B: 5M × $0.59/M = $3/mes → OPCIÓN CORRECTA

---

## Arquitectura multi-modelo recomendada

| Rol | Modelo | Proveedor | API Key | Costo |
|-----|--------|-----------|---------|-------|
| Decisiones rápidas | Llama 3.3 70B | Groq | GROQ_API_KEY | Gratis |
| Análisis profundo | Kimi K2.5 (thinking) | NVIDIA | NVIDIA_API_KEY | Gratis |
| Fallback inteligente | Kimi K2 0905 | Groq | GROQ_API_KEY | Gratis |
| Fallback emergencia | Gemini Flash | OpenRouter | OPENROUTER_API_KEY | Gratis |

### Notas importantes
- Kimi K2 0905 reemplazó a Kimi K2 original en Groq (Sept 2025) — 262K contexto
- Llama 3.3 70B en Groq: 276 tokens/seg — el más rápido del mercado
- NVIDIA Kimi K2.5: modo thinking activado para análisis complejos de mercado
- Todo el stack es GRATIS en los volúmenes de paper trading

---

## Setup en OpenClaw — 5 minutos

OpenClaw soporta Groq nativamente.
Solo necesitas agregar al .env:
GROQ_API_KEY=gsk_...

Y en la configuración de OpenClaw seleccionar:
- Provider: Groq
- Model: llama-3.3-70b-versatile
- Fallback: openrouter/auto (free)

---

## ¿VPS con Ollama local? — No recomendado ahora

Kimi K2 completo pesa 595GB → necesita $50-100/mes de VPS
Groq es gratuito y más rápido que cualquier VPS consumer
Evaluar Ollama solo si en el futuro necesitamos privacidad total de datos

---

## Plan de implementación

### Sprint 0 (ahora)
- [ ] Crear cuenta en Groq: console.groq.com
- [ ] Obtener API key gratuita
- [ ] Configurar en OpenClaw: GROQ_API_KEY en .env
- [ ] Crear cuenta en OpenRouter como fallback
- [ ] Testear: llamada simple a Llama 3.3 70B via Groq

### Sprint 3 (producción)
- [ ] Si free tier de Groq no es suficiente → activar plan paid (~$5/mes)
- [ ] Configurar fallback automático a OpenRouter
- [ ] Monitorear costo mensual real vs proyectado

---

## Infraestructura VM — Decisión final

### Hostinger VPS + 1-Click OpenClaw — SELECCIONADO
- URL: hostinger.com/openclaw
- Precio: $6.99/mes (early access, 70% off)
- OpenClaw: instalado automáticamente, sin configuración manual
- Telegram/WhatsApp: listo en minutos
- Soporte 24/7
- Nuestro Groq API key reemplaza sus AI credits propios

### Por qué Hostinger sobre Hetzner
Hetzner es más barato ($4-8/mes) pero requiere instalar OpenClaw
manualmente desde cero — horas de trabajo técnico.
Hostinger tiene OpenClaw en 1-click — listo en minutos.
El tiempo ahorrado vale más que la diferencia de precio.

### Costo total mensual estimado
- Hostinger VPS + OpenClaw: $6.99/mes
- Groq API (free tier): $0/mes
- Simmer paper trading: $0/mes
- Total: ~$7/mes durante paper trading
- Total en producción real: ~$10-12/mes máximo
