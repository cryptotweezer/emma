# Polymarket Trading Bot — Emma OS

## Qué es este proyecto
Emma OS — Sistema multi-agente comandado por Emma.
Bot de trading en Polymarket es solo el primer módulo.
Visión: Emma como comandante de múltiples agentes especializados, cada uno con memoria y workspace propio.

Capital inicial trading: $1,000 USD (paper trading primero).
Objetivo largo plazo: sistema autónomo de inteligencia operacional — trading, research, desarrollo y más.

## Estado actual del sistema

INFRAESTRUCTURA:
- Servidor: Contabo VPS10, Ubuntu 24.04, Seattle, IP 85.239.236.154
- SSH aliases (Windows ~/.ssh/config):
  - ssh emma → tunnel al dashboard puerto 18789
  - ssh emma-shell → shell directo al servidor
- Repo GitHub: https://github.com/cryptotweezer/emma
- Bot Telegram: @Emma_Tweezer_Bot (token en /root/.env)

SERVICIOS CORRIENDO (auto-start habilitado):
- emma-bot.service → bot de trading 24/7
- openclaw-gateway.service → Emma OS gateway 24/7
- agent-dashboard.service → dashboard web puerto 45680 24/7

ACCESO AL DASHBOARD:
- Abrir tunnel: ssh emma
- URL: http://localhost:45680
- URL OpenClaw: http://localhost:18789
- Token OpenClaw: 1903582673fa86f899b966d8962fbefbd5b19246e8d25386

## Bot de trading — estado actual

ARCHIVOS:
- Entry point: /root/emma/bot.py
- Database: /root/emma/data/emma.db (SQLite)
- Logs: /root/emma/logs/bot.log
- Service: systemctl status emma-bot

CONFIGURACIÓN:
- Ciclo: cada 300s (5 minutos)
- Edge mínimo: 8%
- Kelly máximo: 15%
- Balance inicial: $10,000 SIM
- Modo: Paper Trading en Simmer SDK
- Venue: Simmer (no Polymarket directo todavía)

ESTRATEGIA:
- Edge = (Metaculus × 0.6 + Manifold × 0.4) - Polymarket_price
- Si edge ≥ 8% → ejecutar trade
- Kelly Criterion para sizing, máximo 15% por posición

LOGGING EN SUPABASE:
- agent_name: "Trading_Bot" (NO "Tweezer" — son entidades separadas)
- Loggea cada ciclo completado sin oportunidades
- Loggea cada trade ejecutado
- Módulo: storage/supabase_logger.py

## OpenClaw — Emma OS

CONFIGURACIÓN:
- Versión: 2026.3.24
- Modelo default: openai/gpt-4o-mini
- Providers adicionales: groq, openrouter, nvidia
- Memoria semántica: agents.defaults.memorySearch = gemini/gemini-embedding-001
- 17 variables de entorno cargadas desde /root/.env

AGENTES CREADOS:

| Agente | ID | Default | Emoji | Rol |
|--------|----|---------|-------|-----|
| Emma | emma | ✅ | 👑 | Comandante y orquestadora |
| Tweezer | tweezer | ❌ | 📈 | Trading & Markets Specialist |
| Dev | dev | ❌ | 💻 | Senior Software Developer |
| Otto | otto | ❌ | 🔍 | Research & Intelligence |

ARCHIVOS DE WORKSPACE POR AGENTE:
Cada agente tiene configurados: SOUL.md, IDENTITY.md, AGENTS.md,
TOOLS.md, USER.md, HEARTBEAT.md (vacío), BOOTSTRAP.md (vacío),
MEMORY.md (vacío — lo llena Gemini automáticamente)

IMPORTANTE — Trading_Bot vs Tweezer:
- Trading_Bot = el proceso bot.py corriendo en systemd. Loggea en
  Supabase como "Trading_Bot". Es autónomo, no usa OpenClaw.
- Tweezer = el agente de OpenClaw. Es el especialista de trading
  que Andrés puede consultar via chat. Usa las APIs de AI.
- Son entidades SEPARADAS que comparten la tabla agent_logs de
  Supabase pero con agent_name diferente.

## Supabase

CONFIGURACIÓN:
- Plan: Free tier
- Cliente Python: supabase==2.28.3
- Variables: SUPABASE_URL y SUPABASE_ANON_KEY en /root/.env

TABLAS:

agent_logs (6 columnas):
- id, agent_name, task_description, model_used, status, created_at
- Alimenta el Agent Monitor del dashboard
- Quién loggea: Trading_Bot (automático), Emma/Tweezer/Dev/Otto
  (via Supabase Protocol en SOUL.md)

todos (9 columnas):
- id, title, category, priority, due_date, completed, status,
  track_status, created_at
- Alimenta el Kanban board del dashboard

SUPABASE PROTOCOL (en SOUL.md de cada agente):
Cada agente tiene una regla mandatoria al final de su SOUL.md
que los obliga a ejecutar un INSERT en agent_logs después de
cada tarea, registrando: agent_name, task_description,
model_used (dinámico según modelo usado), status.

## Dashboard Web

ARCHIVO: /root/emma/dashboard/index.html
TAMBIÉN EN: /root/.openclaw/workspace/agent-dashboard/index.html
PUERTO: 45680 (solo localhost, acceso via SSH tunnel)
SERVICIO: agent-dashboard.service (auto-start habilitado)

AVATARES en dashboard/avatars/:
- logo.png — logo CryptoTweezer Command Center
- emma.png — avatar Emma
- tweezer.png — avatar Tweezer
- dev.png — avatar Dev
- otto.png — avatar Otto

TABS DEL DASHBOARD:
1. Overview — resumen del sistema, métricas generales, bot status
2. Trading — P&L, trades, win rate, ciclos completados
3. Agents — actividad por agente, switch de modelo, envío de tareas
4. Tasks — Kanban board (todo/in_progress/done) conectado a Supabase
5. Cron Jobs — servicios activos y log de ciclos recientes

FUNCIONALIDADES:
- Switch de modelo por agente individual (Emma, Tweezer, Dev, Otto)
- Modelo preferido se guarda en localStorage
- Envío de tareas directamente desde el dashboard a cualquier agente
- Drag & drop del Kanban board
- Auto-refresh de Overview cada 30 segundos
- Clock en AEST (Australia/Sydney UTC+11)
- Tema cyberpunk: negro, morado oscuro, azul

MODELOS DISPONIBLES (cheat sheet):
Gratis:
- nvidia/meta/llama-3.3-70b-instruct · nvidia
- nvidia/llama-3.1-nemotron-70b · nvidia
- nvidia/mistral-nemo-minitron-8b · nvidia
- groq/llama-3.3-70b-versatile
- groq/llama-3.1-8b-instant

De pago (OpenAI):
- openai/gpt-4o-mini ← default recomendado
- openai/gpt-4.1-nano ← más barato
- openai/gpt-4o ← cuando se necesita más calidad

## Sprints

### COMPLETADO ✅
- Bot de trading corriendo 24/7 con logging en Supabase
- OpenClaw reinstalado limpio con 4 agentes completamente configurados
- Supabase configurado (tablas agent_logs y todos)
- Dashboard web CryptoTweezer Command Center funcionando
- 3 servicios systemd con auto-start (emma-bot, openclaw-gateway,
  agent-dashboard)
- Memoria semántica Gemini configurada
- Múltiples providers de AI (OpenAI, Groq, NVIDIA, OpenRouter)
- SSH aliases actualizados (ssh emma / ssh emma-shell)
- GitHub Personal Access Token configurado en servidor
- Telegram @Emma_Tweezer_Bot con whitelist (solo Andrés)
- Trading_Bot separado de Tweezer en Supabase logs
- Fix datetime.utcnow() → datetime.now(timezone.utc)

### PENDIENTE Sprint 3
- [ ] Discord server — canal por agente, webhooks
- [ ] Integrar OpenAI usage API para ver costos en dashboard
- [ ] Limpieza automática de agent_logs > 90 días (cron job)
- [ ] Conectar modelo switch del dashboard con openclaw.json real
- [ ] Google Workspace para Emma (Gmail, Drive, Calendar)
- [ ] Moltbook y Twitter para Emma (fase futura)
- [ ] Analizar primeros 30 trades paper trading → decisión dinero real
- [ ] Wallet Polymarket nueva antes de dinero real (actual comprometida)
- [ ] Rotar POLYCLAW_PRIVATE_KEY en Chainstack

### PENDIENTE Sprint 4
- [ ] Evaluar resultados paper trading → decisión dinero real
- [ ] Conectar wallet real a Polymarket mainnet
- [ ] Activar Auto Backup en Contabo

## Variables de entorno (/root/.env)

Variables presentes en el servidor:
CONTABO_IP, TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID=6509551753,
SIMMER_API_KEY, POLYMARKET_PRIVATE_KEY (comprometida — no usar con
dinero real), GROQ_API_KEY, OPENROUTER_API_KEY, NVIDIA_API_KEY,
GEMINI_API_KEY, OPENAI_API_KEY, METACULUS_API_KEY, MANIFOLD_API_KEY,
ALCHEMY_API_KEY, ALCHEMY_NODE, CHAINSTACK_NODE, BOT_INTERVAL=300,
BOT_MIN_EDGE=0.08, SUPABASE_URL, SUPABASE_ANON_KEY

NOTA DE SEGURIDAD: Todas las API keys fueron rotadas después del
incidente de seguridad de la sesión 10. Las keys anteriores deben
considerarse comprometidas. POLYMARKET_PRIVATE_KEY no usar con
dinero real — generar wallet nueva antes del Sprint de dinero real.

## Historial de sesiones

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
| 14 | Sprint 2-3 | 2026-03-28 | Dashboard web completado: CryptoTweezer Command Center con 5 tabs (Overview, Trading, Agents, Tasks, Cron Jobs). Kanban board conectado a Supabase. Switch de modelo por agente. Avatares de los 4 agentes. Trading_Bot separado de Tweezer en Supabase. 3 servicios systemd habilitados. Fix datetime.utcnow(). |

## Próximo paso EXACTO

1. Verificar que el dashboard carga en http://localhost:45680 con avatares
2. Verificar que agent_logs en Supabase muestra "Trading_Bot" (no "Tweezer")
3. Sprint 3: Discord server y canales por agente
4. Sprint 3: Integrar OpenAI usage API para ver costos en dashboard
5. Cuando haya 30+ trades → analizar resultados y decidir dinero real
