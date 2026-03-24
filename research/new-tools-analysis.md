# Nuevas Herramientas y Arsenal de Emma — Análisis (2026-03-24)

## Resumen ejecutivo
Investigación de nuevas herramientas basada en el tweet de @LunarResearcher
"I Mass-Built a Polymarket Trading Bot in 2 Weeks" y búsqueda adicional del ecosistema.
Resultado: encontramos PolyClaw (skill oficial OpenClaw para Polymarket) y Binance MCP
que cambian significativamente nuestro stack.

---

## Hallazgo crítico: PolyClaw ya existe

URL: https://github.com/chainstacklabs/polyclaw
Mantenido por: Chainstack (empresa de infraestructura blockchain, fuente confiable)
Estado: INSTALAR — es una skill oficial para OpenClaw, corre directo en Emma

### Qué puede hacer PolyClaw
- Buscar mercados en Polymarket por tema en lenguaje natural
- Ejecutar trades on-chain en Polygon (split + CLOB execution)
- Detectar oportunidades de hedge via lógica LLM (contrapositive logic)
- Trackear posiciones con entrada, precio actual y P&L
- Escanear trending markets para arbitrage lógico
- Coverage tiers: T1 (≥95%), T2 (90-95%), T3 (85-90%)

### Cómo se integra con Emma
- Lenguaje natural: "Find hedging opportunities on Polymarket" → Emma lo ejecuta
- Requiere: CHAINSTACK_NODE (Polygon RPC gratis), POLYCLAW_PRIVATE_KEY, OPENROUTER_API_KEY
- Chainstack ofrece nodo Polygon gratuito en chainstack.com

### Variables de entorno adicionales necesarias
CHAINSTACK_NODE=https://polygon-mainnet.core.chainstack.com/TU_KEY
POLYCLAW_PRIVATE_KEY=0x...  (wallet MetaMask)

---

## Binance MCP Server

URL: https://github.com/danishashko/binance-mcp-server
Estado: INSTALAR en Sprint 1

### Por qué es relevante para Polymarket
Los mercados crypto de Polymarket (BTC $100K, ETH price, etc.) dependen de
precios en tiempo real de exchanges. Binance tiene datos antes que Polymarket.

Estrategia de señal adicional:
- Binance precio BTC en tiempo real
- Comparar con probabilidad implícita en mercado de Polymarket
- Si Binance muestra momentum fuerte pero Polymarket no lo refleja → edge detectado

### Costo
- Datos de mercado públicos: GRATIS (sin API key)
- Trading con tu cuenta Binance: requiere API key personal

### Herramientas disponibles
- binance_get_ticker: precio actual + estadísticas 24h
- binance_get_order_book: profundidad del mercado
- binance_get_klines: datos OHLCV para análisis técnico
- binance_get_price: precio simple (lightweight, rápido)
- binance_search_symbols: buscar pares de trading

---

## Herramientas del tweet de @LunarResearcher — análisis

### Lo que ya teníamos cubierto
| Su herramienta | Lo nuestro | Estado |
|---|---|---|
| Polymarket CLOB API | py-clob-client | ✅ planificado |
| Python 3.11+ + asyncio | Python 3.9+ | ✅ planificado |
| VPS $5/mes + systemd | Contabo $4.95 + systemd | ✅ funcionando |
| Telegram bot | Emma @emma_openclawbot | ✅ funcionando |
| Git | GitHub repo | ✅ funcionando |
| Kelly Criterion | Documentado en estrategia | ✅ planificado |

### Lo que nos falta agregar al bot (código Python)

#### Alta prioridad — Sprint 1
- **asyncio**: bot completamente asíncrono para escanear 50+ mercados en paralelo
  Sin esto el bot es 10x más lento por ciclo
- **SQLite positions tracker**: registrar cada trade abierto localmente
  Campos: market_id, side, entry_price, size, timestamp, status, pnl
  Sin esto hay que consultar blockchain en cada ciclo (lento y costoso)
- **GTC orders (no FOK)**: fill rate 95% vs 60%
  FOK orders se cancelen en markets con poca liquidez
  GTC orders esperan en el orderbook hasta llenarse
- **Alchemy RPC (Polygon)**: endpoint gratis para verificar balances USDC
  Necesario para balance pre-check antes de cada trade
  URL: alchemy.com — free tier suficiente
- **httpx**: cliente HTTP async (más rápido que requests para múltiples llamadas API)
- **Balance pre-check**: verificar balance on-chain antes de cada trade
  Evita errores "not enough balance" a las 3 AM
- **Slippage protection**: max 2% slippage en cualquier orden
  Si el orderbook es muy thin → skip the trade

#### Media prioridad — Sprint 2
- **Bayesian updating**: actualizar probabilidades cuando cae una noticia
  No mantener estimaciones viejas durante eventos en vivo
  Formula: P(H|E) = P(E|H) × P(H) / P(E)
- **Rotating log handlers**: logs que no llenen el disco
  python logging con RotatingFileHandler
- **Error recovery**: el bot no crashea en errores
  Catch exceptions → log → Telegram alert → continuar scanning
- **Log returns**: usar log returns para P&L correcto
  Arithmetic returns mienten, log returns se suman correctamente

#### Otras skills de OpenClaw a evaluar
- mvanhorn/clawdbot-skill-polymarket: order books, batch orders, price history, P&L dashboard
- Polymarket Autopilot: paper trading automático TAIL+BONDING+SPREAD strategies

---

## Estrategia de arbitrage MUERTA — importante documentar

### Exchange price delay arbitrage — ELIMINADO por Polymarket en marzo 2026
Bots monitoreaban precios de Binance/Coinbase y explotaban el delay de 500ms
en los mercados de 15 minutos de crypto de Polymarket.
En marzo 2026, Polymarket introdujo dynamic taker fees y eliminó el delay.
Esta estrategia ya no existe. NO perseguirla.

### Nuestra estrategia de info arbitrage — SIGUE VIGENTE
Comparar probabilidades de Metaculus+Manifold vs precios de Polymarket.
Esta estrategia no depende de delays técnicos sino de información pública
que el mercado no ha incorporado aún. Válida indefinidamente.

---

## Herramientas de analytics y whale tracking

### Ya en nuestro plan (confirmar)
- HashDive: Smart Score wallets, insider detection — partner oficial Polymarket
- Polysights: AI analytics con Gemini+Perplexity, 30+ métricas, alerts

### Nuevas a evaluar
- Oddpool (oddpool.com): cross-venue data Polymarket+Kalshi, arbitrage entre plataformas
- YN Signals: alerts 24/7 en Telegram, anomalías de odds, insider wallets
- Bitquery: datos on-chain via GraphQL, trades y settlements en tiempo real

---

## Advertencia de seguridad crítica — Skills maliciosas

Fuente: múltiples reportes marzo 2026
- 1,184 skills maliciosas detectadas en ClawHub distribuyendo malware
- Diseñadas para robar wallet private keys de bots de trading
- ClawHub respondió purgando 2,419 skills sospechosas + partnership con VirusTotal
- 21,639 instancias de OpenClaw expuestas públicamente en internet (Kaspersky)

### Regla de Emma: lista blanca de skills permitidas
Solo instalar skills de estas fuentes:
1. Chainstack (chainstacklabs) — PolyClaw y herramientas blockchain verificadas
2. Skills que construimos nosotros en este repo
3. Skills con código auditado personalmente antes de instalar
4. NUNCA instalar skills de fuentes desconocidas en ClawHub sin revisión del código

---

## Variables de entorno adicionales necesarias (agregar a .env.example)

CHAINSTACK_NODE=           # nodo Polygon gratis para PolyClaw
POLYCLAW_PRIVATE_KEY=      # wallet MetaMask private key (0x...)
ALCHEMY_API_KEY=           # Polygon RPC alternativo
BINANCE_API_KEY=           # opcional — solo si usamos cuenta propia Binance
BINANCE_API_SECRET=        # opcional — solo si usamos cuenta propia Binance

---

## Stack actualizado de señales (versión 2)

Señal 1 (ya planificada): edge = promedio(Metaculus × 0.6, Manifold × 0.4) - PM_precio
Señal 2 (nueva): Binance momentum → comparar vs mercados crypto de Polymarket
Señal 3 (ya planificada): NOAA forecast vs weather brackets
Señal 4 (ya planificada): HashDive Smart Score wallet > 70 confirma trade
Alerta roja (ya planificada): HashDive Insider Detection → NO entrar

---

## Próximos pasos concretos

Sprint 1 additions:
- [ ] Crear cuenta en Chainstack → obtener Polygon RPC gratis
- [ ] Instalar PolyClaw en Emma: openclaw install chainstacklabs/polyclaw
- [ ] Instalar Binance MCP server en Emma
- [ ] Agregar CHAINSTACK_NODE al .env del servidor
- [ ] Agregar asyncio, SQLite, httpx al plan de código del bot
- [ ] Revisar código de mvanhorn/clawdbot-skill-polymarket antes de instalar
