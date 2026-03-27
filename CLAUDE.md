# Polymarket Trading Bot — Estado del Proyecto

## Qué es este proyecto
Emma OS — Sistema multi-agente comandado por Emma.
Bot de trading en Polymarket es solo el primer módulo.
Visión: Emma como comandante de múltiples agentes especializados, cada uno con memoria y workspace propio.

Capital inicial trading: $1,000 USD (paper trading primero).
Objetivo largo plazo: sistema autónomo de inteligencia operacional — trading, research, desarrollo y más.

## Arquitectura Multi-Agente (visión Sprint 3+)

### OpenClaw — Estado actual
- Versión: 2026.3.24
- Reinstalado limpio el 2026-03-27
- Gateway corriendo en: http://127.0.0.1:18789
- Token dashboard: 1903582673fa86f899b966d8962fbefbd5b19246e8d25386
- Modelo: openai/gpt-4o-mini (OPENAI_API_KEY configurada en env)
- Telegram: @Emma_Tweezer_Bot conectado con dmPolicy: allowlist, allowFrom: [6509551753]
- Memoria semántica: agents.defaults.memorySearch = gemini / gemini-embedding-001
- 17 variables de entorno cargadas desde /root/.env

### Los 4 agentes están creados y completamente configurados

| Agente | ID | Default | Emoji | Rol |
|--------|----|---------|-------|-----|
| Emma | emma | ✅ | 👑 | Comandante y orquestadora |
| Tweezer | tweezer | ❌ | 📈 | Trading & Markets Specialist |
| Dev | dev | ❌ | 💻 | Senior Software Developer |
| Otto | otto | ❌ | 🔍 | Research & Intelligence |

### Archivos configurados por agente
Cada agente tiene en su workspace:
- SOUL.md — system prompt completo y detallado
- IDENTITY.md — nombre, emoji, personalidad
- AGENTS.md — descripción del equipo y cómo colaborar
- TOOLS.md — infraestructura y comandos específicos del agente
- USER.md — perfil de Andrés personalizado por agente
- HEARTBEAT.md — vacío (sin heartbeat por ahora)
- BOOTSTRAP.md — vacío (onboarding completado)
- MEMORY.md — vacío (Gemini lo llena automáticamente)

### Supabase — Estado actual
- Plan: Free tier
- Proyecto: activo y healthy
- Cliente Python instalado: supabase==2.28.3
- Variables configuradas en /root/.env y openclaw.json:
  - SUPABASE_URL
  - SUPABASE_ANON_KEY

### Tablas creadas

| Tabla | Columnas | Propósito |
|-------|----------|-----------|
| agent_logs | 6 | Registra actividad de agentes — alimenta Agent Monitor |
| todos | 9 | Kanban board de tareas |

### Qué se loggea en agent_logs
- bot.py → loggea automáticamente cada ciclo de trading (agent_name: Tweezer)
- Emma, Tweezer, Dev, Otto → loggean cada tarea via Supabase Protocol en SOUL.md

### Supabase Protocol (en SOUL.md de cada agente)
Cada agente tiene al final de su SOUL.md una regla mandatoria que los obliga
a ejecutar un python3 INSERT en agent_logs después de cada tarea completada,
registrando: agent_name, task_description, model_used (dinámico), status.

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
### SSH aliases (máquina local Windows, ~/.ssh/config)
- ssh emma → tunnel SSH al puerto 18789 (dashboard OpenClaw)
- ssh emma-shell → shell directo al servidor

Nota: anteriormente eran ssh openclaw y ssh openclaw-shell.
Actualizados en sesión 13.
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

## bot.py

### Cambios recientes en bot.py
- Integrado supabase_logger: from storage.supabase_logger import log_agent_activity
- Loggea en Supabase en dos puntos:
  1. Línea 156: cuando ejecuta un trade exitoso
  2. Línea 165: cuando completa un ciclo sin oportunidades
- Fix aplicado: sim_balance en executor.py para leer balance correcto
- DeprecationWarning pendiente: datetime.utcnow() → datetime.now(timezone.utc)

### Nuevo archivo: storage/supabase_logger.py
- Módulo de logging para Supabase
- Función: log_agent_activity(agent_name, task_description, model_used, status)
- Diseño fail-safe: nunca rompe el bot si Supabase falla
- Compatible con ImportError si supabase no está instalado

---

## ESTADO ACTUAL

**Sprint:** 1 — Paper trading 24/7 en VM
**Fecha última actualización:** 2026-03-26
**Estado general:** SPRINT 1 COMPLETADO — Bot completo listo para deploy — 20 archivos Python, 1119 líneas — Pending: git pull en servidor + bash deploy.sh

### Completado ✅
- Bot de trading corriendo 24/7 como systemd service
- OpenClaw reinstalado limpio con 4 agentes
- Supabase configurado con tablas agent_logs y todos
- Supabase logging integrado en bot.py y SOUL.md de agentes
- Telegram @Emma_Tweezer_Bot conectado con whitelist
- Memoria semántica Gemini configurada

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
| 12 | Sprint 2 | 2026-03-27 | OpenClaw reinstalado limpio. 4 agentes creados (Emma👑, Tweezer📈, Dev💻, Otto🔍). Todos los archivos de workspace configurados (SOUL, IDENTITY, AGENTS, TOOLS, USER, HEARTBEAT, BOOTSTRAP, MEMORY). Modelo cambiado a gpt-4o-mini. Telegram @Emma_Tweezer_Bot conectado con whitelist. SSH aliases actualizados a ssh emma y ssh emma-shell. Memoria semántica Gemini configurada. 17 env vars cargadas en OpenClaw. |
| 13 | Sprint 2 | 2026-03-28 | Supabase configurado (free tier). Tablas agent_logs y todos creadas. supabase_logger.py creado y commiteado al repo. bot.py integrado con Supabase logging. Supabase Protocol agregado al SOUL.md de los 4 agentes. GitHub Personal Access Token configurado para push desde servidor. |
