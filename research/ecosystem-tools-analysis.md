# Ecosistema de herramientas — Polymarket 2026

**Fuente principal:** https://defiprime.com/definitive-guide-to-the-polymarket-ecosystem
**Fuente secundaria:** https://github.com/aarora4/Awesome-Prediction-Market-Tools
**Fecha análisis:** 2026-03-21
**Total herramientas en ecosistema:** 170+

---

## Contexto importante
Simmer Markets NO es la única plataforma de este tipo.
Existe un ecosistema completo de 170+ herramientas en 19 categorías.
Este documento mapea las más relevantes para nuestro proyecto.

---

## Categoría 1 — Plataformas de ejecución para agentes IA

### Simmer Markets ⭐ SELECCIONADA
- **URL:** https://simmer.markets
- **Por qué:** Paper trading nativo, skills pre-hechas, OpenClaw nativo, safety rails
- **Ver:** research/simmer-markets-analysis.md

### FinFeedAPI
- **URL:** https://finfeedapi.com (a verificar)
- **Qué hace:** API unificada para Polymarket + Kalshi + Myriad + Manifold en una llamada
- **Relevancia:** ALTA — elimina múltiples integraciones
- **Estado:** Pendiente de investigar

### Oddpool
- **URL:** https://www.oddpool.com
- **Qué hace:** Agrega datos cross-venue, detecta arbitraje entre plataformas
- **Relevancia:** MEDIA — útil en Fase 2 cuando operemos en múltiples venues
- **Estado:** Pendiente de investigar

### Agentbets.ai
- **URL:** https://agentbets.ai
- **Qué hace:** MCP server, playground de APIs de Polymarket, guías para developers
- **Relevancia:** ALTA — ya usamos su guía de APIs, tiene MCP server para Claude
- **Estado:** Ya investigado parcialmente

---

## Categoría 2 — Fuentes de señales (CRÍTICO para nuestra estrategia)

### Polysights ⭐ PRIORITARIO
- **URL:** https://app.polysights.xyz
- **Qué hace:** 30+ métricas con Vertex AI + Gemini + Perplexity
  - AI-generated market summaries
  - Arbitrage Detection automática
  - Beta Insider Finder (wallets nuevas con trades inusuales)
  - User Portfolio Tracking con PnL
- **Relevancia:** MUY ALTA — detecta arbitraje automáticamente
- **Pricing:** Free básico, paid con AI insights

### Inside Edge ⭐ PRIORITARIO
- **URL:** https://inside.fyi
- **Qué hace:** Identifica ineficiencias con edge % cuantificado
- **Relevancia:** MUY ALTA — nos dice exactamente qué tan grande es el edge
- **Estado:** Pendiente de investigar en profundidad

### Alphascope
- **URL:** https://www.alphascope.app
- **Qué hace:** Señales en tiempo real, probability shifts, mispricings
- **Relevancia:** ALTA — señales accionables para arbitrage de información
- **Estado:** Pendiente de investigar

### PolyRadar
- **URL:** https://www.polyradar.io
- **Qué hace:** Múltiples modelos de IA independientes + confidence scoring
- **Relevancia:** ALTA — consensus de múltiples modelos reduce falsos positivos
- **Estado:** Pendiente de investigar

### Jatevo
- **URL:** https://jatevo.ai/agents/prediction-market
- **Qué hace:** Pipeline de 6 agentes de IA para análisis profundo
- **Relevancia:** MEDIA — para análisis complejo de eventos específicos
- **Estado:** Pendiente de investigar

### Sportstensor
- **URL:** https://www.sportstensor.com
- **Qué hace:** Predicciones deportivas con ensemble modeling y datos colectivos
- **Relevancia:** MEDIA — útil para mercados deportivos (Fase 2)
- **Estado:** Pendiente de investigar

### Polyseer
- **URL:** https://www.polyseer.xyz
- **Qué hace:** Open-source, multi-agent, Bayesian probability aggregation
- **Relevancia:** ALTA — open source = auditeable y gratuito
- **Estado:** Pendiente de investigar

---

## Categoría 3 — Analytics y whale tracking (señales secundarias)

### HashDive ⭐ PRIORITARIO
- **URL:** https://hashdive.com
- **Qué hace:**
  - Smart Scores: rating -100 a 100 de traders por performance histórico
  - Market Screener: filtrar por liquidez, volumen, whale activity
  - Wallet tracking de smart money
  - Charts con RSI, MACD, SMA
- **Relevancia:** MUY ALTA — nos dice quién gana consistentemente para copiar o seguir

### Polywhaler
- **URL:** https://www.polywhaler.com
- **Qué hace:** Whale tracker en tiempo real, trades $10K+, detecta actividad insider
- **Relevancia:** ALTA — señal de "dinero inteligente" entrando a un mercado

### Polyburg
- **URL:** https://polyburg.com
- **Qué hace:** Smart money tracking de cientos de wallets exitosas
- **Relevancia:** ALTA — complementa HashDive

### Betmoar ⭐ MÁS USADO
- **URL:** https://www.betmoar.fun
- **Qué hace:** Terminal web + analytics avanzados ($110M en volumen)
  - Análisis de perfiles de traders
  - Market position delta (flujo de dinero)
  - News feed integrado
  - Ejecución directa
- **Relevancia:** MUY ALTA — el terminal más usado de todo el ecosistema

---

## Categoría 4 — Alerts y monitoreo

### PolyAlertHub
- **URL:** https://polyalerthub.com
- **Qué hace:** Whale tracking + AI analytics + alertas por email/Telegram
  - Sin conexión de wallet requerida
  - No ejecuta trades — solo información
- **Relevancia:** ALTA — alertas automáticas de movimientos importantes

---

## Resumen — Stack de herramientas recomendado para nuestro proyecto

### Para ejecutar (ejecución de órdenes)
1. **Simmer Markets** — paper trading + producción vía OpenClaw
2. **py-clob-client** — control directo cuando necesitemos más poder

### Para generar señales (el cerebro del bot)
1. **Polysights** — detección automática de arbitraje + AI summaries
2. **Inside Edge** — edge cuantificado por mercado
3. **HashDive** — smart money tracking para copy signals
4. **Polywhaler / Polyburg** — whale alerts como señal secundaria

### Para monitoreo y contexto
1. **Betmoar** — terminal principal de análisis
2. **PolyAlertHub** — alertas automáticas

### Para datos externos de señal (fuentes primarias)
- Metaculus — probabilidades de referencia
- NOAA — datos de temperatura para weather markets
- RSS feeds de noticias — via polymarket-signal-sniper skill
- Simmer AI Divergence — donde IA diverge del precio de mercado

---

## Hallazgo crítico del ecosistema
Entre Abril 2024 y Abril 2025, traders sofisticados extrajeron
~$40 millones en profits de arbitraje solo en Polymarket.
Un bot documentado convirtió $313 en $414,000 en un mes
explotando arbitraje temporal en mercados de 15 minutos.
El gap entre bots y humanos: bots $206K con 85%+ win rate
vs humanos ~$100K con estrategias similares.

## Próximos pasos de investigación
- [ ] Investigar Polysights en profundidad — ¿tiene API pública?
- [ ] Investigar Inside Edge — ¿cómo cuantifica el edge?
- [ ] Investigar HashDive — ¿exporta datos de Smart Scores?
- [ ] Investigar FinFeedAPI — ¿reemplaza múltiples integraciones?
- [ ] Verificar seguridad de cada herramienta antes de conectar wallet
