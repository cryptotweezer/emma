# Simmer Markets — Análisis completo

**URL:** https://simmer.markets
**Skill.md:** https://simmer.markets/skill.md
**Docs completos:** https://docs.simmer.markets/llms-full.txt
**SDK:** pip install simmer-sdk
**Fecha análisis:** 2026-03-21

## Qué es Simmer exactamente
Plataforma de prediction markets diseñada específicamente para agentes IA.
Abstrae Polymarket y Kalshi en una sola API con:
- Self-custody wallets (tú controlas tus keys)
- Safety rails configurables ($100/trade, $500/día por defecto)
- Smart context — pregunta "¿debería tradear esto?" y responde
- Múltiples venues: Simmer ($SIM virtual), Polymarket (USDC real), Kalshi (USD real)
- 9,074 agentes compitiendo actualmente

## Impacto en nuestra arquitectura

### Decisión crítica: Simmer vs py-clob-client directo

| Aspecto | Simmer SDK | py-clob-client directo |
|---------|-----------|----------------------|
| Setup | pip install simmer-sdk | pip install py-clob-client |
| Paper trading | Incluido ($10K $SIM gratis) | Hay que construirlo |
| Safety rails | Automáticos | Hay que construirlos |
| Skills pre-hechas | 7 estrategias instalables | No |
| Kalshi | Incluido | No |
| Control | Menor | Total |
| Fees | 2% sobre $SIM markets | Sin fee adicional |
| OpenClaw integración | Nativa | Manual |

**Veredicto: Simmer primero, py-clob-client cuando necesitemos control total**

## Skills pre-construidas disponibles (ClawHub)
Instalar con: clawhub install <slug>

| Skill | Estrategia | Relevancia |
|-------|------------|------------|
| polymarket-weather-trader | NOAA data → temperature brackets | ALTA — info arbitrage sin fee |
| polymarket-copytrading | Mirror top wallets | MEDIA — validar señal externa |
| polymarket-signal-sniper | RSS feeds + noticias | ALTA — info arbitrage |
| polymarket-fast-loop | BTC 5min momentum | MEDIA — Fase 2 |
| polymarket-ai-divergence | AI price vs Polymarket | ALTA — nuestro edge principal |
| polymarket-mert-sniper | Near-expiry skewed markets | MEDIA |
| prediction-trade-journal | Log de trades | ALTA — siempre útil |

## Venues disponibles
- **sim** — Paper trading con $SIM virtual (GRATIS, empezar aquí)
- **polymarket** — USDC.e en Polygon (real, requiere wallet setup)
- **kalshi** — USD via Solana (real, requiere KYC en dflow.net)

## Flujo de integración con OpenClaw
1. Registrar agente en Simmer → obtener API key
2. Instalar simmer-sdk en OpenClaw
3. Conectar wallet EOA a Simmer dashboard
4. Empezar en venue=sim (paper trading)
5. Instalar skills de ClawHub
6. Graduar a venue=polymarket cuando win rate > 55%

## API endpoints clave
- POST /api/sdk/agents/register — registrar agente
- GET /api/sdk/briefing — estado completo en una llamada
- GET /api/sdk/context/{market_id} — análisis antes de tradear
- POST /api/sdk/trade — ejecutar trade
- GET /api/sdk/skills — listar skills disponibles
- GET /api/leaderboard/all — leaderboard de agentes

## Safety rails por defecto (configurables)
- Max por trade: $100
- Max por día: $500
- Max trades por día: 50
- Stop-loss: 50% automático en cada compra
- Take-profit: desactivado por defecto (mercados resuelven solos)

## Paper trading en Simmer ($SIM)
- $10,000 $SIM virtuales al registrar
- Mismos precios reales de Polymarket
- Target: edge > 5% en $SIM antes de ir a real
- Métrica clave: rank en leaderboard de 9,074 agentes

## Conexión con NOAA (fuente de señal para weather)
El skill polymarket-weather-trader ya integra NOAA automáticamente.
Esto cubre nuestra primera fuente de señal sin construirla desde cero.

## ⚠️ Seguridad — Skills de ClawHub

### El problema
ClawHub es un repositorio abierto — cualquier persona puede publicar skills.
Se han reportado skills con código malicioso que pueden:
- Robar private keys del archivo .env
- Drenan wallets ejecutando trades no autorizados
- Exfiltrar API keys a servidores externos
- Ejecutar comandos arbitrarios en el sistema

### Regla de oro — solo instalamos skills que cumplan LOS TRES criterios
1. Están listadas en https://simmer.markets/skill.md (oficial de Simmer) — O —
2. Son de autores verificados con miles de estrellas y código abierto
3. El código fuente es público y fue revisado antes de instalar

### Skills APROBADAS para este proyecto (oficiales de Simmer/SpartanLabs)
Estas están listadas en el skill.md oficial de Simmer:
- polymarket-weather-trader — oficial Spartan Labs
- polymarket-copytrading — oficial Spartan Labs
- polymarket-signal-sniper — oficial Spartan Labs
- polymarket-fast-loop — oficial Spartan Labs
- polymarket-ai-divergence — oficial Spartan Labs
- prediction-trade-journal — oficial Spartan Labs

### Skills de comunidad — revisar código antes de instalar
Hay 31,000+ skills en ClawHub. Muchas son legítimas pero sin auditar.
Antes de instalar cualquier skill de comunidad:
1. Verificar repo GitHub del autor
2. Leer el código completo
3. Buscar: llamadas a URLs externas, lectura de .env, comandos bash sospechosos
4. Si hay dudas → NO instalar

### Skills de comunidad con potencial (pendiente de revisión)
- polymarket-analysis by @hiehoo (5.4K installs, 142 estrellas) — solo análisis, sin ejecución
- polymarket-odds by @deanpress (9.9K installs, 531 estrellas) — solo lectura

### NUNCA instalar sin revisar
- Skills con pocas estrellas y autor desconocido
- Skills que piden private key o wallet access sin justificación clara
- Skills con código ofuscado o URLs de dominios sospechosos

## Próximos pasos con Simmer
1. Registrar agente via API
2. Instalar simmer-sdk
3. Paper trading con polymarket-weather-trader
4. Validar edge en $SIM antes de capital real
