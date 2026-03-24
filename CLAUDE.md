# Polymarket Trading Bot — Estado del Proyecto

## Qué es este proyecto
Bot de trading automatizado para Polymarket con EV positivo sostenible.
Estrategia híbrida en 2 fases: arbitrage de información → market making.
Capital inicial: $1,000 USD. Objetivo: máxima rentabilidad.

## Stack técnico (decisiones fijas)
- Lenguaje: Python 3.9+
- Capa de ejecución: Simmer SDK (pip install simmer-sdk) — paper trading + producción
- SDK control avanzado: py-clob-client (pip install py-clob-client)
- Cadena: Polygon (chain ID 137) — colateral USDC
- Wallet: EOA signature_type=0
- Paper trading venue: Simmer $SIM (antes de capital real)
- Primera señal: Metaculus API (metaculus.com/api/ — sin auth, gratis)
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

## Decisiones de arquitectura (no cambiar sin documentar)
- Fees: mercados política/eventos = CERO fees → estrategia Fase 1
- Fees: mercados crypto/deportivos = fees variables → estrategia Fase 2
- Kelly Criterion para sizing — nunca más del 15% por posición
- WebSocket para datos en tiempo real (no consume rate limit REST)
- Paper trading OBLIGATORIO antes de capital real
- Subagentes de Claude Code: implementar solo en fase de producción
- OpenClaw: operador 24/7 en producción, no durante desarrollo

## Bugs críticos documentados (NO ignorar)
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

**Sprint:** 0 — Setup inicial
**Fecha última actualización:** 2026-03-24
**Estado general:** VM activa — OpenClaw 24/7 — Emma con identidad + memoria semántica Gemini operativa — SSH con alias y clave ed25519 — pendiente USER.md + simmer-sdk + primer trade Simmer

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
- [x] Modelo OpenClaw: openrouter/auto (free tier) (2026-03-24) (2026-03-23)

### Próximo paso EXACTO
SPRINT 1 — Tarea 1: Instalar simmer-sdk y ejecutar primer trade de prueba

Primer paso exacto:
SSH al servidor: `ssh openclaw-shell`
pip install simmer-sdk en el servidor + verificar con python -c "import simmer"
Crear .env en el servidor con todas las API keys.
Ejecutar primer trade manual en Simmer venue=sim para verificar pipeline completo.

### Problemas conocidos abiertos
- Ninguno

### Goals de la próxima sesión
- [ ] pip install simmer-sdk en el servidor + verificar con python -c "import simmer"
- [ ] Crear .env en el servidor con todas las API keys
- [ ] USER.md con información de Andres
- [ ] Primer trade de prueba en Simmer venue=sim para verificar pipeline completo
- [ ] Configurar routing de modelos por tarea en el código del bot
- [ ] Agregar créditos a OpenRouter (~$5) para modelos específicos

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
