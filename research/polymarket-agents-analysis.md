# Polymarket/agents — Análisis profundo

**Repo:** https://github.com/Polymarket/agents
**Stars:** 2,600+ | **Forks:** 604 | **Licencia:** MIT
**Fecha análisis:** Marzo 2026
**Versión analizada:** branch main, py_clob_client 0.17.5

---

## Qué es exactamente

Framework oficial de Polymarket para construir agentes de trading con IA. Combina:
- **Gamma API** para descubrir mercados
- **ChromaDB** como capa RAG (Retrieval-Augmented Generation) para filtrar mercados por relevancia semántica
- **OpenAI GPT** como motor de decisión (superforecaster + trade decision)
- **py-clob-client** para firmar y enviar órdenes al CLOB

**Importante:** La ejecución real de órdenes está **comentada** en el código. El bot calcula cuánto apostar pero no hace submit. Hay un comentario TOS que sugiere que esto es intencional para el repo público.

---

## Arquitectura del sistema (componentes y cómo se conectan)

```
polymarket-agents/
├── agents/
│   ├── application/
│   │   ├── trade.py       ← Trader: entry point, orquesta el loop completo
│   │   ├── executor.py    ← Executor (alias: Agent): LLM + RAG orchestration
│   │   ├── prompts.py     ← Prompter: todos los templates de prompts
│   │   ├── creator.py     ← Creator: variante para crear nuevos mercados (no tradear)
│   │   └── cron.py        ← TradingAgent: scheduler semanal (con bugs graves)
│   ├── connectors/
│   │   ├── chroma.py      ← PolymarketRAG: embed + persist + similarity search
│   │   ├── news.py        ← News: NewsAPI connector
│   │   └── search.py      ← Tavily web search (proof-of-concept, no integrado)
│   ├── polymarket/
│   │   ├── polymarket.py  ← Polymarket: CLOB client + Web3 + ejecución on-chain
│   │   └── gamma.py       ← GammaMarketClient: REST API para discovery
│   └── utils/
│       └── objects.py     ← Pydantic models: SimpleMarket, SimpleEvent, Trade, etc.
```

**Dependencias entre módulos:**
```
Trader
  └── Polymarket (gamma_url, clob_url, Web3 Polygon)
  └── GammaMarketClient (Gamma REST API)
  └── Executor
        └── ChatOpenAI (gpt-3.5-turbo-16k, temperature=0)
        └── PolymarketRAG
              └── OpenAIEmbeddings (text-embedding-3-small)
              └── ChromaDB (local persistence)
        └── Prompter (templates estáticos, sin deps externas)
        └── GammaMarketClient
        └── Polymarket
```

---

## Cómo conecta LLMs con el CLOB (flujo completo)

### Paso 1 — Discovery de mercados
```
Polymarket.get_all_tradeable_events()
  → httpx.GET https://gamma-api.polymarket.com/events
  → filtra: active=True, restricted=False, archived=False, closed=False
  → retorna list[SimpleEvent]
```

### Paso 2 — Filtrado RAG de eventos
```
Executor.filter_events_with_rag(events)
  → prompt estático: "Filter these events for the ones you will be best at trading on profitably."
  → PolymarketRAG.events(events, prompt)
      • escribe JSON a ./local_db_events/events.json
      • JSONLoader con jq_schema=".[]", content_key="description"
      • OpenAIEmbeddings("text-embedding-3-small") embeds descriptions
      • Chroma.from_documents() persiste en ./local_db_events/chroma
      • similarity_search_with_score(query=prompt)
  → retorna list[tuple(Document, float_score)]
```

### Paso 3 — Mapeo de eventos a mercados
```
Executor.map_filtered_events_to_markets(filtered_events)
  → por cada evento: metadata["markets"].split(",") → lista de market IDs
  → GammaMarketClient.get_market(market_id)
      → httpx.GET https://gamma-api.polymarket.com/markets/{market_id}
  → Polymarket.map_api_to_market(data) → SimpleMarket
  → retorna list[SimpleMarket] (flat)
```

### Paso 4 — Filtrado RAG de mercados
```
Executor.filter_markets(markets)
  → mismo patrón: prompt estático + PolymarketRAG.markets()
  → metadata capturada: id, outcomes, outcome_prices, question, clob_token_ids
  → retorna list[tuple(Document, float_score)]
```

### Paso 5 — Decisión LLM (2 calls secuenciales)
```
Executor.source_best_trade(market_object)

  LLM Call 1 — Superforecaster:
    SystemMessage = Prompter.superforecaster(question, description, outcomes)
    ChatOpenAI(gpt-3.5-turbo-16k, temperature=0).invoke(messages)
    Output: "I believe {question} has a likelihood 0.73 for outcome of Yes."

  LLM Call 2 — Trade decision:
    SystemMessage = Prompter.one_best_trade(forecast, outcomes, outcome_prices)
    ChatOpenAI.invoke(messages)
    Output: "price:0.73, size:0.1, side:BUY,"
```

### Paso 6 — Formateo del trade
```
Executor.format_trade_prompt_for_execution(best_trade)
  → split(",") → extrae size con regex: re.findall("\d+\.\d+", data[1])[0]
  → Polymarket.get_usdc_balance()
      → usdc.functions.balanceOf(wallet).call() / 10e5
  → retorna size * usdc_balance (monto en USD)
```

### Paso 7 — Ejecución (COMENTADA)
```python
# trade = self.polymarket.execute_market_order(market, amount)
#   → token_id = clob_token_ids[1]  ← siempre toma el índice 1 (NO token)
#   → MarketOrderArgs(token_id, amount)
#   → client.create_market_order(order_args) → signed_order
#   → client.post_order(signed_order, orderType=OrderType.FOK)
#   → orden Fill-or-Kill al CLOB: https://clob.polymarket.com
```

---

## Fuentes de datos que usa para tomar decisiones

| Fuente | Cómo se usa | Estado de integración |
|--------|-------------|----------------------|
| Gamma API (`gamma-api.polymarket.com`) | Discovery de eventos y mercados activos | Integrado y funcionando |
| CLOB API (`clob.polymarket.com`) | Order book, precios, ejecución | Integrado (ejecución comentada) |
| NewsAPI | Headlines para analizar sentimiento de mercado | Integrado en `news.py`, NO llamado en el pipeline principal de `trade.py` |
| Tavily search | Búsqueda web general | Script standalone, se ejecuta en import, NO integrado en pipeline |
| ChromaDB (local) | Vector store de embeddings de descripciones de mercados/eventos | Integrado (persiste en disco local) |
| OpenAI Embeddings | `text-embedding-3-small` para el RAG | Integrado |

**Conclusión:** El pipeline real solo usa Gamma API + ChromaDB RAG + GPT. NewsAPI y Tavily están en el código pero no conectados al flujo de decisión.

---

## Estrategia que implementa por defecto

**No es market making ni arbitraje.** Es **direccional con LLM como oráculo:**

1. Descarga todos los mercados activos de Polymarket
2. Filtra semánticamente los mercados más "tradeables" (criterio: similitud con prompt estático genérico)
3. El LLM actúa como superforecaster y estima probabilidad del evento
4. Compara esa probabilidad con el precio actual del mercado
5. Si hay discrepancia, genera una orden de compra/venta en la dirección de la discrepancia
6. El tamaño es un porcentaje del balance total (fracción del capital)

**Tipo de orden:** FOK (Fill-or-Kill) — si no hay liquidez suficiente, la orden muere.
**Sin gestión de posiciones:** No hay lógica para salir de posiciones, gestionar P&L ni stop-loss.
**Sin gestión de riesgo real:** Kelly Criterion ausente. El sizing es arbitrario (porcentaje que devuelve el LLM).

---

## Stack de dependencias (requirements.txt completo)

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `langchain` | 0.2.11 | Orquestación LLM |
| `langchain-openai` | 0.1.19 | Integración OpenAI |
| `langchain-chroma` | 0.1.2 | Vector store |
| `langchain-community` | 0.2.10 | JSONLoader |
| `langchain-core` | 0.2.26 | HumanMessage, SystemMessage |
| `langgraph` | 0.1.17 | Incluido, NO usado en pipeline principal |
| `openai` | 1.37.1 | SDK OpenAI raw |
| `chromadb` | 0.5.5 | Base de datos vectorial local |
| `py_clob_client` | 0.17.5 | SDK CLOB oficial Polymarket |
| `py_order_utils` | 0.3.2 | Firma y construcción de órdenes |
| `poly_eip712_structs` | 0.0.1 | EIP-712 typed data |
| `web3` | 6.11.0 | Ethereum/Polygon blockchain |
| `eth-account` | 0.13.1 | Gestión de claves |
| `newsapi-python` | 0.2.7 | Noticias |
| `tavily-python` | 0.3.5 | Búsqueda web |
| `httpx` | 0.27.0 | HTTP sync client |
| `pydantic` | 2.8.2 | Modelos de datos |
| `scheduler` | 0.8.7 | Cron scheduling |
| `python-dotenv` | 1.0.1 | Variables de entorno |
| `fastapi` | 0.111.0 | Incluido, NO usado en pipeline principal |

**Modelo LLM:** GPT-3.5-turbo-16k por defecto (o GPT-4-1106-preview). `temperature=0`.
**Embedding:** `text-embedding-3-small` vía OpenAI.
**Blockchain:** Web3 → Polygon (`https://polygon-rpc.com`, chain ID 137).

---

## Limitaciones identificadas

### Bugs críticos

**1. Ejecución comentada**
```python
# trade = self.polymarket.execute_market_order(market, amount)
```
El bot no ejecuta órdenes. Es un simulador.

**2. USDC balance incorrecto (bug matemático)**
```python
return float(balance_res / 10e5)  # 10e5 = 100,000
# USDC tiene 6 decimales → el divisor correcto es 1e6 = 1,000,000
# Con 10e5: 1 USDC real aparece como $0.10 → sizing 10x más pequeño de lo real
```

**3. Market order siempre compra el token NO**
```python
token_id = ast.literal_eval(market[0].dict()["metadata"]["clob_token_ids"])[1]
# [1] = segundo token = NO outcome siempre
# Si el LLM dice BUY y el mercado tiene 70% YES, compra NO
```

**4. Recursión infinita en error**
```python
except Exception as e:
    self.one_best_trade()  # sin profundidad máxima ni backoff
```

**5. Bugs en cron.py**
```python
# Scheduler.__init__ se llama a sí mismo recursivamente:
self.schedule = Scheduler()  # → StackOverflow
# TradingAgent llama super() sin args → __init__ de Scheduler nunca corre
```

**6. search.py se ejecuta al importar**
```python
# Código module-level con query hardcodeada:
context = tavily_client.get_search_context(query="Will Biden drop out of the race?")
```

### Limitaciones de diseño

- **RAG filter no filtra semánticamente**: el prompt de búsqueda es estático (`"Filter these events for the ones you will be best at trading on profitably."`). Todos los mercados tienen embeddings similares a este query — la selección es casi aleatoria.
- **Sin fuentes externas reales en el loop**: NewsAPI y Tavily no alimentan las decisiones del LLM. El LLM decide sin información actual.
- **Sin memory de posiciones**: el bot no sabe qué tiene en cartera. Podría duplicar posiciones indefinidamente.
- **Sin gestión de riesgo**: no hay Kelly Criterion, no hay límite de concentración por mercado, no hay stop-loss.
- **Sin validación de neg-risk**: no verifica `neg_risk` antes de operar — las órdenes en esos mercados requieren `negRisk: true` o fallan.
- **LLM genera tamaños arbitrarios**: el `size` del trade es "percentage_of_total_funds" que devuelve el LLM — sin restricción cuantitativa.
- **GPT-3.5 como superforecaster**: el modelo tiene knowledge cutoff y no puede acceder a información reciente. Predicciones sin grounding real.
- **Reinicia DB en cada run**: `pre_trade_logic()` borra `local_db_events/` y `local_db_markets/` — re-embeds todo desde cero cada vez, sin caché.

---

## Qué podemos reusar para nuestro proyecto

### Reusar directamente

**`agents/polymarket/gamma.py` — GammaMarketClient**
- Funciona bien para discovery: `get_all_current_markets()`, `get_current_events()`
- Paginación implementada correctamente en `get_all_current_markets()`
- Parseo de Pydantic models robusto

**`agents/polymarket/polymarket.py` — sección CLOB**
- `_init_api_keys()`: patrón correcto para inicializar `ClobClient` con `create_or_derive_api_creds()`
- `get_orderbook()`, `get_orderbook_price()`: wrappers funcionales
- `execute_order()`: signatura correcta con `OrderArgs(price, size, side, token_id)`
- `_init_approvals()`: referencia para setup on-chain con direcciones hardcodeadas correctas
- Todas las contract addresses verificadas:
  - CTF Exchange: `0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e`
  - Neg Risk Exchange: `0xC5d563A36AE78145C45a50134d48A1215220f80a`
  - USDC Polygon: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`

**`agents/utils/objects.py` — Modelos Pydantic**
- `SimpleMarket`, `SimpleEvent` son útiles como referencia de campos disponibles
- `Market` (full) tiene todos los campos que devuelve Gamma API

**`agents/application/prompts.py` — `superforecaster()` prompt**
- El prompt de superforecaster es sólido metodológicamente (base rates, probabilistic thinking)
- Usable como base si queremos incorporar LLM en la estrategia

### Reusar con modificaciones

**Estructura de módulos**: la separación `polymarket/` (datos + ejecución) vs `application/` (lógica) vs `connectors/` (fuentes externas) es buena arquitectura.

**Patrón de filtrado de mercados**: la idea de filtrar por `active`, `closed`, `archived`, `restricted` antes de operar es correcta.

---

## Qué haríamos diferente

### 1. Arreglar el bug crítico de balance USDC
```python
# Incorrecto:
return float(balance_res / 10e5)
# Correcto:
return float(balance_res / 1_000_000)  # 6 decimales USDC
```

### 2. Desacoplar la ejecución del LLM
El repo mezcla discovery (determinista), selección (semántica) y decisión (LLM) en el mismo loop. Separar en:
- **Capa de datos**: Gamma API + CLOB book data (determinista, testeable)
- **Capa de señal**: generación de edge (estrategia específica)
- **Capa de ejecución**: gestión de órdenes (independiente de la señal)

### 3. Sustituir RAG semántico por filtros deterministas
El filtro RAG con prompt estático es pseudoaleatorio. Para trading sistemático, usar filtros explícitos:
- `spread > threshold`
- `liquidity > min_liquidity`
- `volume_24h > min_volume`
- `end_date > now + min_horizon`

### 4. Integrar fuentes externas reales antes de la decisión LLM
Si se usa LLM: pasar noticias reales (NewsAPI), precios de casas de apuestas, o datos de Metaculus **dentro del prompt de decisión**, no solo para embeddings.

### 5. Implementar sizing cuantitativo
Sustituir el sizing arbitrario del LLM por Kelly Criterion:
```
f = (p * b - q) / b
# p = probabilidad estimada, b = odds netas, q = 1 - p
```
Con fracción de Kelly conservadora (0.25x o 0.5x para $1K).

### 6. Añadir gestión de posiciones
El repo no tiene ningún estado de cartera. Necesitamos:
- Rastrear posiciones abiertas (token_id → cantidad)
- Lógica de salida (tiempo, precio objetivo, resolución)
- Límite de concentración por mercado

### 7. Usar WebSocket en vez de polling
El repo usa `httpx.get()` síncrono para prices. Para estrategias sensibles a latencia (market making, arbitraje), usar `wss://ws-subscriptions-clob.polymarket.com/ws/market` que no cuenta contra rate limits.

### 8. Manejar neg-risk markets explícitamente
Antes de cualquier orden, verificar `market.negRisk == True` y ajustar el payload de la orden con `negRisk: true`. El repo no lo hace.

### 9. No usar FOK como orden por defecto
FOK muere si no hay fill completo disponible. Para capital pequeño ($1K), GTC (limit orders) da mejor fill y captura rebates de maker.

### 10. Sustituir GPT-3.5 por Claude si se usa LLM
Claude tiene mejor reasoning cuantitativo y contexto más largo. Si se incorpora LLM en el pipeline, usar `claude-sonnet-4-6` vía Anthropic SDK.

---

## ⚠️ Bugs críticos identificados (NO usar sin corregir)

### Bug 1 — Balance USDC con divisor incorrecto
- **Archivo:** polymarket.py
- **Problema:** Usa `10e5` en vez de `1e6` como divisor
- **Impacto:** El sizing de posiciones queda 10x más pequeño de lo calculado
- **Fix requerido:** Cambiar divisor a `1e6` (1,000,000)

### Bug 2 — Market order siempre compra el outcome INCORRECTO
- **Archivo:** Lógica de ejecución de órdenes
- **Problema:** Siempre compra el token `[1]` = outcome NO, sin importar lo que decida el LLM
- **Impacto:** El bot hace lo OPUESTO a lo que el modelo decide — pérdida garantizada
- **Fix requerido:** Leer correctamente el outcome que devuelve el LLM antes de ejecutar

### Bug 3 — Recursión infinita en error handler
- **Archivo:** Scheduler / error handler
- **Problema:** El handler de errores se llama a sí mismo recursivamente
- **Impacto:** Crash garantizado en el primer error — el bot no puede correr en producción
- **Fix requerido:** Reemplazar recursión con retry loop con backoff exponencial

## ✅ Componentes seguros para reusar

| Componente | Archivo | Por qué es valioso |
|------------|---------|-------------------|
| Addresses de contratos | polymarket.py | Verificadas y correctas |
| Patrón de init CLOB | polymarket.py | Auth + setup correcto |
| Cliente Gamma con paginación | gamma.py | Discovery correcto |
| Modelos Pydantic | objects.py | Todos los campos de la API |

## ❌ Componentes a descartar

| Componente | Razón |
|------------|-------|
| RAG filter | Pseudoaleatorio con prompt estático — no filtra nada real |
| Sizing por LLM | Sin base cuantitativa — no genera EV positivo |
| Scheduler | Bugs de recursión graves |
| Lógica de ejecución de órdenes | Bug crítico de token index |
