# Polymarket Trading Bot — Estado del Proyecto

## Qué es este proyecto
Emma OS — Sistema multi-agente comandado por Emma.
Bot de trading en Polymarket es solo el primer módulo.
Visión: Emma como comandante de múltiples agentes especializados, cada uno con memoria y workspace propio.

Capital inicial trading: $1,000 USD (paper trading primero).
Objetivo largo plazo: sistema autónomo de inteligencia operacional — trading, research, desarrollo y más.

## Arquitectura Multi-Agente (visión Sprint 3+)

### Agentes planificados

| Agente | Rol | Estado |
|--------|-----|--------|
| Emma | Comandante — orquesta todos los agentes, punto de contacto principal via Telegram | ✅ Activa |
| Tweezer | Trading specialist — ejecuta bot.py, analiza señales, reporta P&L | 🔨 Sprint 2 |
| Dev | Developer — escribe código, debug, mejoras del sistema | 🔨 Sprint 3 |
| Lucho | Research — mercados, noticias, señales externas, análisis | 🔨 Sprint 3 |

### Principios de la arquitectura
- Emma es el único punto de contacto con Andrés via Telegram
- Cada agente tiene su propio SOUL.md, memoria semántica y workspace
- Los agentes nunca mezclan información entre sí
- Cada agente reporta resultados a Emma
- Emma orquesta vía ACP (Agent Communication Protocol) de OpenClaw
- Router automático: Emma detecta qué agente debe manejar cada tarea

### Stack del dashboard (Sprint 3)
- Supabase (free tier) — logs de actividad de agentes, Kanban
- Dashboard web en /root/.openclaw/workspace/agent-dashboard/
- Puerto 45680, acceso via SSH tunnel
- Single HTML file con Tailwind CDN + Chart.js + Supabase JS SDK
- Tablas Supabase: agent_logs, todos

### Referencia de implementación
Tutorial base: https://komputermechanic.com/tutorials/openclaw-dashboard
Adaptar agentes del tutorial (Alex/Maya/Jordan/Dev/Sam) a los agentes del proyecto (Emma/Tweezer/Dev/Lucho).

## Stack técnico (decisiones fijas)
- Lenguaje: Python 3.9+
- Capa de ejecución: Simmer SDK (módulo simmer_sdk, usar SimmerClient) — paper trading + producción
- SDK control avanzado: py-clob-client (pip install py-clob-client)
- Cadena: Polygon (chain ID 137) — colateral USDC
- Wallet: EOA signature_type=0
- Paper trading venue: Simmer $SIM (antes de capital real)
- Primera señal: Metaculus API (metaculus.com/api2/questions/ — requiere API key en header Authorization, devuelve 7013 questions)
- Segunda señal: Manifold Markets API (api.manifold.markets — 500 req/min, gratis)
- Tercera señal: NOAA API (api.weather.gov — sin key, gratis, weather markets)
- Smart money: HashDive (hashdive.com — partner oficial Polymarket)
- Skill: grimoire-polymarket (ver /skills/)
- MCP Server señales: Manifold MCP Server (github.com/bmorphism/manifold-mcp-server)
- Producción 24/7: OpenClaw (fase final)
- Infraestructura VM: Contabo VPS10 ($4.95/mes) — 4 vCPU, 8 GB RAM
- Backups: snapshots manuales gratis (paper trading) → Auto Backup activado en Sprint 2
- OpenClaw: instalación manual vía Docker (~10 min con ayuda de Claude)
- Paper trading: Simmer venue=sim 24/7 en VM (3 semanas mínimo)
- Criterio para dinero real: win rate ≥ 55% sostenido con ≥ 30 trades
- Acceso dashboard: ssh openclaw (tunnel) → http://127.0.0.1:18789/#token=a37fc88d89ea9e5eea21c561a14da0d97c0d7ac4ddf65f10
- Acceso shell servidor: ssh openclaw-shell
- Memoria semántica: Gemini text-embedding-001 (gratis, 1000 req/day)
- Emma: @emma_openclawbot en Telegram
- PolyClaw: ~/.openclaw/skills/polyclaw (Chainstack, verificado)
- Alchemy: Polygon mainnet node activo
- Simmer SDK: instalado y primer trade ejecutado en venue=sim
- .env servidor: 20 variables configuradas en /root/.env
- Notificaciones: Telegram Bot API directa vía aiohttp (sin librerías)
- Persistencia local: SQLite (data/emma.db) — trades, snapshots, signals
- Service manager: systemd (emma-bot.service) — restart automático
- Variables config bot: BOT_INTERVAL, BOT_MIN_EDGE, BOT_MAX_KELLY, BOT_MAX_DAILY_LOSS, BOT_MAX_DRAWDOWN, BOT_MAX_POSITIONS

## Decisiones de arquitectura (no cambiar sin documentar)
- Fees: mercados política/eventos = CERO fees → estrategia Fase 1
- Fees: mercados crypto/deportivos = fees variables → estrategia Fase 2
- Kelly Criterion para sizing — nunca más del 15% por posición
- WebSocket para datos en tiempo real (no consume rate limit REST)
- Paper trading OBLIGATORIO antes de capital real
- Subagentes de Claude Code: implementar solo en fase de producción
- OpenClaw: operador 24/7 en producción, no durante desarrollo

## Bugs críticos documentados (NO ignorar)
- simmer-sdk: el módulo se importa como `simmer_sdk`, la clase es `SimmerClient`, el método `get_markets()` NO acepta argumento `venue`, y los objetos `Market` tienen atributos directos (no es un dict).
- metaculus: el endpoint correcto es `/api2/questions/` (el antiguo `/api/questions/` da 404).
- Polymarket/agents: divisor USDC usa 10e5 en vez de 1e6 → sizing 10x mal
- Polymarket/agents: market order siempre compra token[1] = NO outcome
- Polymarket/agents: recursión infinita en error handler → crash garantizado
- poly-maker: estrategia obsoleta sin programa de rewards masivo
- simmer_sdk.SimmerClient.trade(): argumento `side` acepta 'YES'/'NO', NO acepta 'buy'/'sell'. El argumento `action` es separado ('buy').
- simmer_sdk.SimmerClient.execute_trade() es SÍNCRONO (no async) — no usar await al llamarlo desde bot.py.

### Incidente de seguridad — sesión 10 (2026-03-26)
Durante el health check, el dashboard de OpenClaw mostró el contenido completo del /root/.env en el chat. Todo el contenido del chat pasa por OpenRouter y los LLMs de terceros (Groq, NVIDIA). Las siguientes API keys deben considerarse comprometidas y deben rotarse:

KEYS A ROTAR (pendiente — Andrés las rota manualmente):
- GROQ_API_KEY — groq.com → API Keys → Regenerate
- OPENROUTER_API_KEY — openrouter.ai → Settings → Keys
- NVIDIA_API_KEY — build.nvidia.com → API Keys
- GEMINI_API_KEY — aistudio.google.com → API Keys
- METACULUS_API_KEY — metaculus.com → Profile → API
- MANIFOLD_API_KEY — manifold.markets → Profile → API
- ALCHEMY_API_KEY — alchemy.com → Apps → View Key → Regenerate
- SIMMER_API_KEY — simmer.markets → Settings → Regenerate
- CHAINSTACK_NODE — chainstack.com → Project → Regenerate

WALLET A REGENERAR ANTES DE DINERO REAL:
- POLYMARKET_PRIVATE_KEY — generar wallet nueva en MetaMask antes de cualquier operación con USDC real. La actual pasó por OpenRouter y debe considerarse comprometida.

KEYS SEGURAS (no expuestas o ya rotadas):
- CONTABO_ROOT_PASSWORD — no se mostró en el chat ✅
- TELEGRAM_BOT_TOKEN — se compartió en chat privado con Claude claude.ai, no pasó por OpenRouter ✅

REGLA PERMANENTE PARA EMMA:
Emma tiene en su SOUL.md la regla de nunca mostrar keys completas en el chat. Siempre usar grep -q o --count.

## Arquitectura de señales (decisión fija)
- Señal primaria: edge = promedio(Metaculus × 0.6, Manifold × 0.4) - Polymarket_precio
- Umbral: edge ≥ 8% con ambas fuentes de acuerdo → señal válida
- Confirmación: HashDive Smart Score wallet > 70 entra al mismo mercado → alta confianza
- Alerta roja: HashDive Insider Detection flaggea el mercado → NO entrar
- Weather: NOAA forecast diverge > 15% del bracket → señal de nicho
- Ver detalle: research/signal-sources-analysis.md

## Componentes reutilizables verificados
- polymarket.py → contract addresses + patrón init CLOB (corregir bug divisor)
- gamma.py → cliente discovery con paginación correcta
- objects.py → modelos Pydantic completos
- websocket_handlers.py (poly-maker) → patrón dual market+user con reconexión

---

## ESTADO ACTUAL

**Sprint:** 1 — Paper trading 24/7 en VM
**Fecha última actualización:** 2026-03-26
**Estado general:** SPRINT 1 COMPLETADO — Bot completo listo para deploy — 20 archivos Python, 1119 líneas — Pending: git pull en servidor + bash deploy.sh

### Completado
- [x] Estructura del proyecto creada (2026-03-20)
- [x] Research completo: APIs, repos, fees, estrategia (2026-03-20)
- [x] Bugs críticos documentados (2026-03-20)
- [x] Estrategia definida: info arbitrage → market making (2026-03-20)
- [x] Sistema de workflow configurado (2026-03-20)
- [x] Custom skills corregidas a formato .claude/skills/ (2026-03-20)
- [x] Simmer Markets investigado — seleccionado como capa de ejecución (2026-03-21)
- [x] Ecosistema 170+ herramientas mapeado (2026-03-21)
- [x] Stack de señales definido: Metaculus + Manifold + NOAA + HashDive (2026-03-21)
- [x] Lógica del detector de mispricing definida — edge ≥ 8% (2026-03-21)
- [x] Manifold MCP Server identificado — integración directa con Claude Code (2026-03-21)
- [x] Infraestructura VM decidida: Contabo VPS10 $4.95/mes — 4 vCPU, 8 GB RAM (2026-03-22)
- [x] Paper trading 24/7 en VM definido — Sprint 1 reescrito con criterios de graduación (2026-03-21)
- [x] Infraestructura migrada a Contabo VPS10 — documentación completa en next-steps.md (2026-03-22)
- [x] Servidor Contabo VPS10 activo — IP 85.239.236.154, Seattle US West, OpenClaw preinstalado (2026-03-22)
- [x] Email Contabo recibido con credenciales confirmadas (2026-03-22)
- [x] Todas las APIs conseguidas: Groq, Metaculus, Manifold, Simmer, OpenRouter, Inside Edge (2026-03-22)
- [x] Simmer agente registrado, reclamado y con $10K SIM listos (2026-03-22)
- [x] .env template completo creado con todas las variables necesarias (2026-03-22)
- [x] .gitignore creado — .env y secrets protegidos del repo (2026-03-22)
- [x] SSH al servidor Contabo VPS10 exitoso — root@85.239.236.154 (2026-03-23)
- [x] OpenClaw 2026.3.13 instalado como daemon systemd 24/7 con lingering activado (2026-03-23)
- [x] Bot Telegram @emma_openclawbot creado, emparejado y respondiendo (ID: 6509551753) (2026-03-23)
- [x] Dashboard web accesible via tunnel SSH + token guardado (2026-03-23)
- [x] Todas las API keys inyectadas en ~/.openclaw/openclaw.json sección "env": OPENROUTER, GROQ, NVIDIA, SIMMER, METACULUS, MANIFOLD (2026-03-23)
- [x] Workspace files presentes: AGENTS.md, BOOTSTRAP.md, HEARTBEAT.md, IDENTITY.md, SOUL.md, TOOLS.md, USER.md (2026-03-23)
- [x] Stack AI actualizado: Kimi K2.5 (NVIDIA) + Kimi K2 0905 (Groq) añadidos a ai-model-strategy.md (2026-03-23)
- [x] SOUL.md personalizado — identidad Emma definida: directa, honesta, experta en trading/crypto/cybersecurity, autonomía calibrada por monto (2026-03-23)
- [x] Emma actualizó su propio SOUL.md — memoria persistente del agente confirmada operativa (2026-03-23)
- [x] Modelo ajustado a openrouter/auto (free tier) — acceso al mejor modelo disponible sin créditos
- [x] SSH config con alias: ssh openclaw (tunnel automático) y ssh openclaw-shell (shell normal) (2026-03-24)
- [x] Autenticación por clave ed25519 — sin contraseña (2026-03-24)
- [x] Wizard de onboarding desactivado (touch /var/lib/openclaw/onboarded-root) (2026-03-24)
- [x] SOUL.md personalizado para Emma — identidad completa en inglés (2026-03-24)
- [x] Memoria semántica configurada: provider=gemini, model=gemini-embedding-001 (2026-03-24)
- [x] Directorio ~/.openclaw/workspace/memory/ creado (2026-03-24)
- [x] GEMINI_API_KEY agregada al openclaw.json env section (2026-03-24)
- [x] Modelo OpenClaw: openrouter/auto (free tier) (2026-03-24)
- [x] pip install simmer-sdk instalado en el servidor (2026-03-24)
- [x] /root/.env creado con 20 variables (SIMMER, POLYMARKET, GROQ, OPENROUTER, NVIDIA, GEMINI, METACULUS, MANIFOLD, CONTABO, ALCHEMY_API_KEY, ALCHEMY_NODE, CHAINSTACK_NODE, POLYCLAW_PRIVATE_KEY) (2026-03-24)
- [x] Alchemy cuenta creada — Polygon mainnet node activo (gratis, 30M CU/mes) (2026-03-24)
- [x] PolyClaw de Chainstack instalado en ~/.openclaw/skills/polyclaw (2026-03-24)
- [x] uv instalado para ejecutar PolyClaw (2026-03-24)
- [x] PolyClaw verificado funcionando — mostrando mercados reales de Polymarket en tiempo real (2026-03-24)
- [x] Simmer SDK conectado y verificado — briefing devuelve mercados en tiempo real (2026-03-24)
- [x] PRIMER TRADE DE PAPER TRADING EJECUTADO en venue=sim: 163.93 shares por 14.92 $SIM (2026-03-24)
- [x] Health check completo ejecutado — 7/7 componentes verificados (2026-03-26)
- [x] Simmer SDK corregido: módulo `simmer_sdk`, clase `SimmerClient`, `get_markets()` sin argumento `venue`, objetos Market con atributos directos (2026-03-26)
- [x] Metaculus API corregida: endpoint `/api2/questions/` + API key en header Authorization, devuelve 7013 questions (2026-03-26)
- [x] Alchemy node verificado: block 84696663, Polygon mainnet activo (2026-03-26)
- [x] PolyClaw verificado: mercados reales en tiempo real (US/Iran, Netanyahu, etc.) (2026-03-26)
- [x] Manifold API verificada: funcionando sin auth (2026-03-26)
- [x] bot.py creado — loop asyncio 24/7 con ciclo completo fetch→match→edge→trade→log (2026-03-26)
- [x] signals/metaculus.py — fetch /api2/questions/ + fuzzy match con difflib (2026-03-26)
- [x] signals/manifold.py — fetch /v0/markets + fuzzy match con difflib (2026-03-26)
- [x] trading/edge.py — calculate_edge(), kelly_size(), determine_side() implementados (2026-03-26)
- [x] trading/risk.py — RiskManager: stop-loss diario 5%, drawdown 15%, max 5 posiciones (2026-03-26)
- [x] trading/executor.py — TradeExecutor con firmas reales verificadas de simmer_sdk.SimmerClient.trade() (2026-03-26)
- [x] storage/db.py — SQLite con tablas: trades, daily_snapshots, signal_log (2026-03-26)
- [x] notifications/telegram.py — notify_trade, notify_risk_limit, notify_daily_report, notify_startup (2026-03-26)
- [x] notifications/discord.py — stub listo para Sprint 2 (2026-03-26)
- [x] utils/logger.py — logging stdout + logs/bot.log rotación 7 días (2026-03-26)
- [x] requirements.txt — simmer-sdk, aiohttp, python-dotenv (2026-03-26)
- [x] emma-bot.service — systemd unit file para deploy 24/7 (2026-03-26)
- [x] deploy.sh — script de deploy: pip install + systemd + restart (2026-03-26)
- [x] Firmas reales de simmer_sdk verificadas en servidor: trade(), get_portfolio(), get_positions(), get_total_pnl(), get_held_markets() (2026-03-26)
- [x] 10/10 archivos .py compilados sin errores de sintaxis (2026-03-26)
- [x] git push completado — commit e920a0b, 20 archivos, +1119 líneas (2026-03-26)

### Próximo paso EXACTO
PRÓXIMOS PASOS (en orden de prioridad):
1. Andrés rota todas las API keys comprometidas (ver sección seguridad)
2. Completar USER.md de Emma con información de Andrés
3. Verificar bot.py corriendo y acumulando trades reales
4. Cuando haya 30+ trades → analizar resultados y planificar Sprint 3
5. Sprint 3: crear agentes Tweezer, Dev, Lucho en OpenClaw

### Problemas conocidos abiertos
- Ninguno

### Pendiente Sprint 1
- [x] Health check implícito de APIs completado
- [x] Escribir bot.py base con asyncio + señales Metaculus/Manifold
- [x] Configurar lógica de edge detection (edge ≥ 8%)
- [x] Conectar señales con Simmer para trades automáticos
- [ ] USER.md con información de Andrés

### Pendiente Sprint 2 — Setup inmediato
- [ ] Andrés rota todas las API keys comprometidas (ver lista arriba)
- [ ] Andrés genera wallet Polymarket nueva para Sprint de dinero real
- [ ] Completar USER.md en workspace de Emma con info de Andrés: nombre, timezone (verificar), proyectos activos, cómo prefiere comunicarse, qué espera de Emma
- [ ] Verificar bot.py corriendo: journalctl -u emma-bot -f
- [ ] Confirmar fix sim_balance en executor.py también en repo local
- [ ] Fix datetime.utcnow() DeprecationWarning → datetime.now(timezone.utc)
- [ ] Verificar whitelist Telegram activo (test con cuenta diferente)
- [ ] Acumular primeros 30 trades de paper trading con datos reales

### Pendiente Sprint 3 — Multi-agente
- [ ] Crear cuenta Supabase gratuita y configurar tablas agent_logs + todos
- [ ] Crear agente Tweezer en OpenClaw con SOUL.md especializado en trading
- [ ] Crear agente Dev en OpenClaw con SOUL.md especializado en código
- [ ] Crear agente Lucho en OpenClaw con SOUL.md especializado en research
- [ ] Configurar router en Emma para despacho automático de tareas
- [ ] Discord server para Emma + canal por agente
- [ ] Emma responde preguntas consultando emma.db en tiempo real

### Pendiente Sprint 4 — Dashboard
- [ ] Servidor dashboard en puerto 45680 (systemd service)
- [ ] Dashboard HTML/JS con Supabase: Agent Monitor + Kanban
- [ ] Emma orquesta pipeline completo: Lucho research → Tweezer señales
- [ ] Análisis primer mes de paper trading — decidir si pasar a dinero real

### Historial de sesiones
| Sesión | Sprint | Fecha | Completado |
|--------|--------|-------|------------|
| 1 | Planificación | 2026-03-20 | Research, estrategia, arquitectura, workflow |
| 2 | Sprint 0 | 2026-03-20 | Verificación workflow, corrección skills a formato .claude/skills/ |
| 3 | Sprint 0 | 2026-03-21 | Research Simmer, ecosistema, APIs señal, estrategia IA, VM Hostinger decidida |
| 4 | Sprint 0 | 2026-03-22 | Contabo VPS10 activo (IP 85.239.236.154), todas las APIs conseguidas, Simmer $10K SIM listo, .env template, .gitignore |
| 5 | Sprint 0 | 2026-03-23 | SSH exitoso, OpenClaw 2026.3.13 daemon systemd, Telegram @emma_openclawbot funcionando, OpenRouter configurado, stack AI actualizado |
| 6 | Sprint 0 | 2026-03-23 | SOUL.md personalizado con identidad Emma, memoria persistente operativa, modelo ajustado a openrouter/auto |
| 7 | Sprint 0 | 2026-03-24 | SSH alias ed25519, onboarding desactivado, memoria semántica Gemini activa, GEMINI_API_KEY inyectada |
| 8 | Sprint 1 | 2026-03-24 | simmer-sdk, .env creado, Alchemy node, PolyClaw instalado y funcionando, Simmer API 502 |
| 9 | Sprint 1 | 2026-03-26 | Health check completo: Simmer SDK corregido (SimmerClient, sin venue), Metaculus endpoint /api2/, todos los componentes verificados OK |
| 10 | Sprint 1 | 2026-03-26 | Sistema completo: bot.py, señales, edge, risk, SQLite, Telegram, deploy scripts — commit e920a0b, 20 archivos, +1119 líneas. Sprint 1 COMPLETADO. |
| 11 | Sprint 2 | 2026-03-26 | Bot live con mensaje Telegram confirmado. Fix sim_balance aplicado. Whitelist Telegram configurado (dmPolicy=allowlist, allowFrom=[6509551753]). Incidente seguridad documentado — API keys a rotar. Visión multi-agente definida: Emma + Tweezer + Dev + Lucho. Arquitectura dashboard con Supabase planificada. |
