# Polymarket Trading Bot — Estado del Proyecto

## Qué es este proyecto
Bot de trading automatizado para Polymarket con EV positivo sostenible.
Estrategia híbrida en 2 fases: arbitrage de información → market making.
Capital inicial: $1,000 USD. Objetivo: máxima rentabilidad.

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
**Fecha última actualización:** 2026-03-24
**Estado general:** VM activa — OpenClaw 24/7 — Emma con identidad + memoria semántica Gemini operativa — SSH con alias y clave ed25519 — simmer-sdk y PolyClaw instalados en el servidor, pendientes de test por Simmer API 502

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

### Próximo paso EXACTO
Escribir bot.py base con asyncio usando simmer_sdk.SimmerClient y Metaculus /api2/questions/

### Problemas conocidos abiertos
- Ninguno

### Pendiente Sprint 1
- [x] Health check implícito de APIs completado
- [ ] Escribir bot.py base con asyncio + señales Metaculus/Manifold
- [ ] Configurar lógica de edge detection (edge ≥ 8%)
- [ ] Conectar señales con Simmer para trades automáticos
- [ ] USER.md con información de Andres

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
