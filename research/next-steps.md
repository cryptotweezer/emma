# Plan de desarrollo — Polymarket Trading Bot

**Fecha:** Marzo 2026
**Capital inicial:** $1,000 USD
**Objetivo:** Máxima rentabilidad — crecer la cuenta agresivamente

---

## Decisión estratégica final

### Estrategia elegida: Híbrida en 2 fases

**Fase 1 — $1K a $5K: Arbitrage de información**
- Mercados: política, eventos macro, long-term (CERO fees)
- Edge: detectar mispricing usando fuentes externas antes que el mercado
- Por qué primero: fees cero = EV puro, capital pequeño no es desventaja
- Meta: doblar o triplicar el capital en 30-60 días

**Fase 2 — $5K+: Agregar Market Making en crypto**
- Mercados: crypto 15min, 1H, 4H (maker rebates diarios en USDC)
- Edge: rebates + spread en mercados con volatilidad controlada
- Por qué después: con $1K los rebates (~$3/día) no cubren inventory risk
- Con $5K: rebates ~$15-20/día, compuesto = exponencial

---

## Arquitectura del sistema (lo que vamos a construir)

### Stack de ejecución (actualizado 2026-03-21)
1. **Simmer SDK** — capa principal de ejecución y paper trading
   - pip install simmer-sdk
   - Paper trading nativo con $10K $SIM virtual
   - Safety rails automáticos ($100/trade, $500/día)
   - Integración nativa con OpenClaw
   - Ver: research/simmer-markets-analysis.md
2. **py-clob-client** — control directo para operaciones avanzadas
   - pip install py-clob-client
   - Usar cuando Simmer no tenga el control necesario
3. **grimoire-polymarket skill** — para operaciones desde agentes Claude

### Stack de señales (nuevo — definido 2026-03-21)
1. **Metaculus API** — probabilidad primaria (sin auth, gratis)
   - URL: metaculus.com/api/
   - Dato clave: community_prediction.full.q2
2. **Manifold Markets API + MCP Server** — probabilidad secundaria (sin auth, gratis)
   - URL: api.manifold.markets — 500 req/min
   - MCP Server: github.com/bmorphism/manifold-mcp-server → integración directa con Claude Code
3. **NOAA API** — weather markets (sin key, gratis)
   - URL: api.weather.gov
   - Forecast temperatura para NYC, Miami, Chicago, LA, Seattle
4. **HashDive** — smart money tracking y confirmación
   - URL: hashdive.com — partner oficial Polymarket
   - Smart Scores: rating -100 a +100 de traders
5. **Inside Edge** — lógica a replicar internamente
   - No tiene API pública → construir nuestro propio detector
   - URL: inside.fyi — referencia de qué detectar

### Lógica del detector de mispricing (nuestro propio "Inside Edge")
- edge = (Metaculus × 0.6) + (Manifold × 0.4) - Polymarket_precio
- Si edge ≥ 8% Y ambas fuentes coinciden en dirección → señal válida
- Confirmación: HashDive Smart Score wallet > 70 entra al mismo mercado
- Alerta roja: HashDive Insider Detection flaggea → NO entrar
- Ver detalle: research/signal-sources-analysis.md

### Componentes confirmados

**Motor de ejecución**
- SDK principal: Simmer SDK (paper trading + producción via OpenClaw)
- SDK avanzado: py-clob-client (cuando necesitemos control total)
- Skill: grimoire-polymarket (para operaciones desde agentes)
- Tipos de orden: GTC para entradas, FOK para salidas rápidas
- Gestión de capital: Kelly Criterion para sizing (nunca más del 15% por posición)

**Infraestructura**
- WebSocket: market channel para datos en tiempo real (no consume rate limit)
- Polygon wallet: EOA (MetaMask) — linkeada a Simmer dashboard
- Monitoreo 24/7: alertas + logs + dashboard simple

### Componentes que reutilizamos de repos analizados

| Componente | Fuente | Estado |
|------------|--------|--------|
| polymarket.py (contract addresses) | Polymarket/agents | Reusar — corregir bug divisor USDC |
| gamma.py (cliente discovery) | Polymarket/agents | Reusar — estable |
| objects.py (modelos Pydantic) | Polymarket/agents | Reusar — completo |
| websocket_handlers.py | warproxxx/poly-maker | Reusar — patrón dual market+user |
| data_processing.py (SortedDict orderbook) | warproxxx/poly-maker | Reusar — eficiente |
| find_markets.py (scoring mercados) | warproxxx/poly-maker | Adaptar — cambiar criterio |

### Componentes que construimos desde cero

| Componente | Por qué nuevo |
|------------|---------------|
| Signal detector | No existe en ningún repo — es nuestro edge |
| Information aggregator | Integra fuentes externas — único para nuestra estrategia |
| Kelly sizing engine | Los repos existentes no tienen base cuantitativa |
| Market selector | Criterio diferente al de poly-maker |

---

## Plan de desarrollo por sprints

## Sprint 0 — Setup completo (1 semana)

### Objetivo
Tener todo el stack funcionando antes de escribir código de trading.

### Infraestructura
- [x] Crear cuenta en Contabo y activar VPS10 — Contabo VPS10 activo, IP 85.239.236.154
- [x] Instalar OpenClaw vía Docker en la VM — OpenClaw 2026.3.13 daemon systemd 24/7
- [x] Conectar Telegram a OpenClaw — @emma_openclawbot activo (ID: 6509551753)
- [x] Agregar Groq API key en configuración de OpenClaw — todas las APIs inyectadas en openclaw.json
- [x] SSH seguro con clave ed25519 y alias configurado — ssh openclaw + ssh openclaw-shell
- [x] SOUL.md personalizado para Emma — identidad completa en inglés
- [x] Memoria semántica con Gemini embeddings activa — provider=gemini, model=gemini-embedding-001
- [x] Wizard de onboarding desactivado

### Cuentas y APIs (trámite manual — hacerlo ANTES de esta sesión)
- [ ] MetaMask instalado y wallet EOA creada
- [ ] Simmer Markets: registrar agente → SIMMER_API_KEY
- [ ] Groq: console.groq.com → API key gratis
- [ ] Metaculus: crear cuenta
- [ ] Manifold Markets: crear cuenta → API key
- [ ] Inside Edge: login con Google
- [ ] OpenRouter: cuenta → API key gratis (fallback)

### Setup técnico en la VM
- [ ] pip install simmer-sdk en el servidor
- [ ] Crear .env en el servidor con todas las API keys
- [ ] Instalar Manifold MCP Server en Claude Code local
- [ ] Conectar wallet EOA a Simmer dashboard
- [ ] Primer trade manual en Simmer venue=sim para verificar conexión

### Al final del Sprint 0
El bot puede ejecutar un trade manualmente en Simmer.
Todo conectado: VM → OpenClaw → Groq → Simmer → Telegram.

## Sprint 1 — Paper trading 24/7 en VM con OpenClaw (3 semanas)

### Decisión tomada
Hacer el paper trading directamente en VM con OpenClaw desde el día 1.
NO en local, NO solo mostrando señales en pantalla.
Razón: historial 100% representativo, valida el stack completo de producción,
detecta problemas de APIs y costos reales antes de arriesgar capital.

### Infraestructura seleccionada: Contabo VPS10

| Proveedor | CPU | RAM | Disco | Precio/mes | OpenClaw | Veredicto |
|-----------|-----|-----|-------|-----------|----------|-----------|
| Hostinger KVM2 | 2 vCPU | 8 GB | 100 GB | ~USD $23 | 1-click | ❌ Descartado — precio injustificado |
| Contabo VPS10 | 4 vCPU | 8 GB | 75 GB | USD $4.95 | manual (Docker, 10 min) | ✅ ELEGIDO |
| Contabo VPS20 | 6 vCPU | 12 GB | 100 GB | USD $7.95 | manual | Plan de escala |
| Hetzner CPX21 | 3 vCPU | 4 GB | 80 GB | USD $9.49 | manual | Alternativa |

URL: contabo.com — Cloud VPS10, mes a mes sin contrato
Setup fee único: ~$5 USD (one-time)

### Backups en Contabo
- Snapshots manuales: GRATIS, incluidos en el plan, retención 30 días
- Auto Backup diario: add-on de pago, primer mes gratis, guarda 10 restore points
- Estrategia para paper trading: snapshots manuales antes de cambios importantes
- Estrategia para producción real (Sprint 2+): activar Auto Backup (1er mes gratis)
- El código del bot vive en GitHub → no depende del servidor
- Los logs de trades los guarda Simmer → no depende del servidor
- Las API keys están en .env local y en el servidor → snapshot cubre esto

### Por qué Contabo sobre Hostinger
El 1-click OpenClaw de Hostinger es su versión simplificada sin control total.
Nosotros necesitamos SSH completo, nuestra propia Groq API key, y libertad de instalar.
OpenClaw en Contabo = 3 comandos Docker con ayuda de Claude. ~10 minutos.
Ahorro: ~USD $18/mes = USD $216/año.

### Advertencia conocida sobre Contabo
A veces asignan IPs recicladas con historial de abuse.
Si eso ocurre: contactar soporte y pedir IP nueva — es raro pero documentado.

### Por qué no solo mostrar señales en pantalla
- Guardar logs manualmente es trabajo tedioso y propenso a errores
- Los cálculos de win rate hechos a mano no son confiables
- Simmer registra cada trade automáticamente con timestamp y P&L
- El paper trading 24/7 captura oportunidades de madrugada y fines de semana
- Valida que el stack completo funciona antes de dinero real

### Tareas del Sprint 1
- [x] Crear cuenta en Contabo y activar VPS10 — activo
- [x] Instalar OpenClaw vía Docker en la VM — daemon systemd 24/7
- [x] Configurar Groq API key en OpenClaw — inyectada
- [x] Conectar OpenClaw con Telegram para recibir alertas — @emma_openclawbot
- [x] Registrar agente en Simmer y guardar SIMMER_API_KEY — $10K SIM listo
- [ ] pip install simmer-sdk en el servidor
- [ ] Crear .env en el servidor con todas las API keys
- [ ] USER.md con información de Andres
- [ ] Script: consultar Metaculus API → probabilidades de mercados abiertos
- [ ] Script: consultar Manifold API → probabilidades de los mismos mercados
- [ ] Script: calcular edge = promedio(Metaculus, Manifold) - precio_Polymarket
- [ ] Script NOAA forecast vs weather brackets en Simmer
- [ ] Conectar señales con Simmer SDK → ejecutar en venue=sim automáticamente
- [ ] Incluir reasoning en cada trade (requerido por Simmer)
- [ ] OpenClaw corre el bot 24/7, alertas por Telegram

### Cómo funciona el flujo completo
VM Contabo (OpenClaw corriendo 24/7)
↓ cada 10-15 minutos
↓ consulta Metaculus + Manifold → calcula edge
↓ si edge ≥ 8% → ejecuta trade en Simmer venue=sim
↓ Simmer registra el trade automáticamente
↓ OpenClaw → Telegram → tu teléfono recibe alerta

### Criterios para avanzar al Sprint 2 (dinero real)
- Mínimo 30 trades ejecutados
- Mínimo 3 semanas de operación continua 24/7
- Win rate ≥ 55% sostenido
- Edge promedio por trade ≥ 6%
- Sin drawdown mayor al 20% del capital $SIM en ninguna semana
- Sin errores de API críticos ni rate limits problemáticos

### Métricas a revisar diariamente (via Simmer briefing en Telegram)
- Balance $SIM actual vs $10,000 inicial
- Win rate acumulado
- Número de trades ejecutados hoy y total
- Costo real de APIs (Groq tokens consumidos)
- Rank en leaderboard de agentes de Simmer

### Qué hacer si los criterios NO se cumplen
- Analizar qué señales fallaron y por qué
- Ajustar umbral de edge (subir de 8% a 10% si hay ruido)
- Probar otras fuentes de señal
- NO pasar a dinero real bajo ninguna circunstancia

### Sprint 2 — Bot mínimo viable
- [ ] Integrar detector de señales con ejecución en Simmer
- [ ] Kelly Criterion para sizing automático
- [ ] Sistema de stop conceptual por posición (max pérdida por trade)
- [ ] Primer trade real — tamaño mínimo ($10-20)
- [ ] Graduación de venue=sim a venue=polymarket

### Sprint 3 — Producción con OpenClaw
- [ ] Instalar OpenClaw en VM o local
- [ ] Configurar Simmer skill en OpenClaw
- [ ] Bot corriendo 24/7 con alertas por Telegram
- [ ] Dashboard de monitoreo simple
- [ ] Escalar sizing si win rate > 55%

---

## Criterios de éxito por fase

### Fase 1 (arbitrage información)
- Win rate objetivo: > 55% (con Kelly esto es rentable)
- Trades por semana: 5-15 (calidad sobre cantidad)
- Max drawdown aceptable: 20% del capital ($200 max)
- Meta de capital: $3,000 en 60 días

### Fase 2 (+ market making)
- Rebates diarios objetivo: $20+/día con $5K capital
- Win rate trades direccionales: > 55%
- Compuesto mensual objetivo: 15-25%

---

## Decisiones tomadas (actualizado 2026-03-21)

1. **Wallet type:** EOA (MetaMask) ✅ DECIDIDO
   - Razón: control total, linkeada a Simmer dashboard

2. **Primera fuente de señal:** Metaculus + Manifold en paralelo ✅ DECIDIDO
   - Razón: ambas públicas y gratuitas, lógica simple de combinar
   - Noticias en tiempo real: Sprint 3 via polymarket-signal-sniper skill

3. **Capa de ejecución:** Simmer SDK primero ✅ DECIDIDO
   - Paper trading nativo sin construirlo, safety rails automáticos
   - py-clob-client se mantiene para control avanzado

4. **Infraestructura 24/7:** Contabo VPS10 + OpenClaw Docker desde Sprint 1 ✅ DECIDIDO
   - Contabo VPS10: $4.95/mes, 4 vCPU 8 GB RAM, OpenClaw vía Docker ~10 min
   - Paper trading 24/7 en VM desde el día 1 del Sprint 1
   - Descartado: Hostinger (precio injustificado ~$23/mes, control limitado)
   - Descartado: Hetzner (menos specs por más precio que Contabo)

---

## Lo que NO vamos a hacer (lecciones aprendidas)

- NO usar Polymarket/agents sin corregir los 3 bugs críticos
- NO hacer market making con $1K — los rebates no cubren el riesgo
- NO dejar que Claude Code haga búsquedas libres en internet durante research
- NO copiar estrategias que dependan de programas de rewards externos
- NO escalar capital antes de validar win rate en paper trading
