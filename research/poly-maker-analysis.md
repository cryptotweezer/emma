# poly-maker — Análisis profundo

**Repo:** https://github.com/warproxxx/poly-maker
**Stars:** 633 | **Forks:** 279
**Lenguaje:** 77.5% Python, 22.5% JavaScript
**Fecha análisis:** Marzo 2026

> ⚠️ **ADVERTENCIA DEL PROPIO AUTOR (README):**
> "In today's market, this bot is not profitable and will lose money."

---

## Qué es exactamente

Bot de **market making pasivo** para Polymarket. Mantiene órdenes limit en ambos lados del libro (BID y ASK) en múltiples mercados simultáneamente, capturando el spread y los **maker rebates** del programa de incentivos de Polymarket.

**Arquitectura general:**
```
update_markets.py     → corre en proceso separado, IP separada, cada 1 hora
                        lee Polymarket API → escribe a Google Sheets

main.py               → proceso principal de trading
                        lee Google Sheets al arranque y cada 30s
                        WebSocket market + user (event-driven)
                        per-market asyncio locks

poly_merger/merge.js  → Node.js subprocess para fusionar posiciones YES+NO
                        llama contratos CTF directamente en Polygon

data_updater/         → scripts de scoring y ranking de mercados
poly_stats/           → seguimiento de P&L y ganancias de rewards
```

**Usa Gnosis Safe wallet** (`signature_type=2`) — no EOA. `BROWSER_ADDRESS` es la Safe address, `PK` es la clave del firmante.

---

## Cómo implementa el market making (flujo completo paso a paso)

### Startup

1. `PolymarketClient()` — autentica: `ClobClient(signature_type=2, funder=BROWSER_ADDRESS)`
2. `update_once()`:
   - `update_markets()` → lee Google Sheets ("Selected Markets" + "All Markets" + "Hyperparameters") → `global_state.df`, `global_state.params`, `global_state.REVERSE_TOKENS`
   - `update_positions()` → REST `data-api.polymarket.com/positions` → `global_state.positions`
   - `update_orders()` → `client.get_all_orders()` → `global_state.orders`
3. Thread background cada 5s: `update_positions(avgOnly=True)` + `update_orders()`; cada 30s: `update_markets()`
4. `asyncio.gather(connect_market_websocket(all_tokens), connect_user_websocket())`

### Loop event-driven (por cada tick)

Cada mensaje WebSocket (book snapshot, price change, trade fill, order event) dispara `asyncio.create_task(perform_trade(market))`.

`perform_trade(market)` adquiere `asyncio.Lock` por mercado y ejecuta:

```
1. CHECK MERGE: min(pos_YES, pos_NO) > 20 USDC → ejecutar merge on-chain
2. FOR EACH TOKEN (YES y NO):
   a. Leer order book desde all_data (SortedDict en memoria)
   b. Calcular best_bid, best_ask, mid_price, liquidez cercana
   c. Calcular bid_price y ask_price (con lógica de mejora/join)
   d. Calcular buy_amount y sell_amount según posición actual
   e. Evaluar stop-loss, take-profit, condiciones de compra
   f. Cancelar y re-poner órdenes si cambiaron price/size
3. gc.collect() + asyncio.sleep(2)
```

---

## Cómo calcula el spread y los precios de las órdenes

### Funciones clave: `get_best_bid_ask_deets` + `get_order_prices`

**Paso 1 — Encontrar mejor precio con tamaño mínimo:**
```python
# Busca el primer nivel del libro con size >= min_size (primero intenta 100, luego 20)
best_bid = primer precio en bids (descendente) con size >= min_size
best_ask = primer precio en asks (ascendente) con size >= min_size
mid_price = (best_bid + best_ask) / 2

# Liquidez acumulada dentro del 10% del mid:
bid_sum = suma de sizes donde best_bid <= price <= mid * 1.1
ask_sum = suma de sizes donde mid * 0.9 <= price <= best_ask
overall_ratio = bid_sum / ask_sum  # usado como señal direccional
```

**Paso 2 — Token2 (NO side) — inversión de precios:**
```python
# El token NO tiene precios espejo: p_NO = 1 - p_YES
best_bid_NO = 1 - best_ask_YES
best_ask_NO = 1 - best_bid_YES
# Tamaños también se cruzan (bid↔ask)
```

**Paso 3 — Calcular bid_price y ask_price:**
```python
# BID: mejorar en 1 tick
bid_price = best_bid + tick_size
# EXCEPCIÓN: si el nivel tiene poca liquidez (< min_size * 1.5) → join (no mejorar)
if best_bid_size < min_size * 1.5:
    bid_price = best_bid

# ASK: mejorar en 1 tick
ask_price = best_ask - tick_size
# EXCEPCIÓN: si el nivel tiene poca liquidez (< 375 USDC) → join
if best_ask_size < 250 * 1.5:
    ask_price = best_ask

# Protección anti-cruce:
if bid_price >= top_ask: bid_price = top_bid
if ask_price <= top_bid: ask_price = top_ask
if bid_price == ask_price:
    bid_price = top_bid
    ask_price = top_ask

# Floor: nunca vender por debajo del costo promedio
if ask_price <= avgPrice and avgPrice > 0:
    ask_price = avgPrice
```

**El spread que captura** = `ask_price - bid_price` (típicamente 1-2 ticks). La estrategia no intenta capturar spreads grandes — busca volumen de fills para acumular maker rebates.

---

## Cómo gestiona el riesgo de inventario

### Mecanismo 1 — Límites de posición

```python
max_size = row['max_size']       # de Google Sheets, por mercado
trade_size = row['trade_size']   # tamaño por orden, de Google Sheets
ABS_MAX = 250                    # hardcoded: nunca > 250 USDC por token

# Nunca comprar si:
# - position >= max_size
# - position >= 250
# - price < 0.10 o price > 0.90 (guarda de precio)
# - price > 5¢ de divergencia con precio de referencia en Sheet
```

### Mecanismo 2 — Reverse position check

```python
# Si tenemos posición en el lado opuesto (YES mientras intentamos comprar NO):
if rev_pos['size'] > min_size:
    if orders['buy']['size'] > MIN_MERGE_SIZE:
        client.cancel_all_asset(token)  # cancelar orden de compra existente
    continue  # no colocar nueva orden de compra
```

El merge automático resuelve esto cuando ambos lados superan 20 USDC.

### Mecanismo 3 — Stop-loss

Archivo de estado: `positions/<condition_id>.json`

```python
pnl = (mid_price - avgPrice) / avgPrice * 100

# TRIGGER si:
#   PnL < stop_loss_threshold (param de Sheets, ej: -15%)
#   Y spread <= spread_threshold (param, ej: ≤ 0.04 — mercado líquido)
# O:
#   volatilidad 3h > volatility_threshold (param, ej: > 5%)

# ACCIÓN:
#   Vender TODO al best bid (market sell)
#   Cancelar todas las órdenes del mercado
#   Escribir sleep_till = ahora + sleep_period horas
#   No volver a comprar hasta que pase el cooldown
```

### Mecanismo 4 — Volatility filter

```python
if row['3_hour'] > params['volatility_threshold']:
    client.cancel_all_asset(order['token'])
    # No coloca orden de compra
```

### Mecanismo 5 — Merge automático (conversión de inventario a USDC)

Cuando `pos_YES > 20 AND pos_NO > 20`:
```
YES + NO → 1 USDC (via CTF mergePositions)
# Reduce exposure bilateral y recupera colateral
```

### Mecanismo 6 — Take-profit

```python
tp_price = avgPrice * (1 + take_profit_threshold/100)  # param de Sheets
ask_price_final = max(tp_price, ask_price)             # nunca por debajo del TP

# Re-envía la orden si:
# - precio desvió > 2% del TP
# - tamaño de la orden < 97% de la posición
```

---

## Cómo usa WebSockets (qué datos consume en tiempo real)

### Canal Market: `wss://ws-subscriptions-clob.polymarket.com/ws/market`

```python
# Suscripción:
{"type": "market", "assets_ids": [<todos los token IDs>]}

# Ping cada 5 segundos
# Reconexión: 5 segundos tras cualquier desconexión
```

**Mensajes recibidos:**

| Tipo | Estructura | Acción |
|------|------------|--------|
| `book` | Snapshot completo `{asset_id, bids: [{price, size}], asks: [...]}` | Reemplaza SortedDict completo → dispara `perform_trade` |
| `price_change` | `{price_changes: [{side, price, size, asset_id}]}` | Actualiza nivel individual; `size=0` → delete → dispara `perform_trade` |

**Storage en memoria:**
```python
# SortedDict (sortedcontainers) — acceso O(log n)
all_data[asset]['bids'] = SortedDict()   # precio → size
all_data[asset]['asks'] = SortedDict()
```

### Canal User: `wss://ws-subscriptions-clob.polymarket.com/ws/user`

```python
# Auth:
{"type": "user", "apiKey": ..., "secret": ..., "passphrase": ...}
```

**Mensajes recibidos:**

| Evento | Acción |
|--------|--------|
| `trade` MATCHED | Añadir a `performing`, actualizar posición en memoria, disparar `perform_trade` |
| `trade` CONFIRMED | Remover de `performing`, disparar `perform_trade` |
| `trade` FAILED | Sleep 2s + `update_positions()` completo desde API |
| `trade` MINED | Remover de `performing` |
| `order` event | Actualizar `global_state.orders` con nuevo size/price |

**`performing` tracking:** Dict `{token_side: set(trade_ids)}` + timestamps. Trades sin confirmar en >15s se eliminan automáticamente.

---

## Cómo funciona el poly_merger (consolidación de posiciones)

### Trigger

```python
# En perform_trade(), antes de cualquier orden:
pos_YES = get_position(token1)['size']  # de global_state.positions
pos_NO  = get_position(token2)['size']
amount_to_merge = min(pos_YES, pos_NO)

if amount_to_merge > MIN_MERGE_SIZE:  # > 20 USDC
    # Verificar on-chain (raw units, antes de /1e6):
    pos_YES_raw = client.get_position(token1)[0]  # conditional_tokens.balanceOf()
    pos_NO_raw  = client.get_position(token2)[0]
    amount_raw = min(pos_YES_raw, pos_NO_raw)
    scaled = amount_raw / 10**6

    if scaled > MIN_MERGE_SIZE:
        client.merge_positions(amount_raw, condition_id, is_neg_risk)
```

### Implementación (Node.js subprocess)

```python
# Python llama:
subprocess.run(f'node poly_merger/merge.js {amount} {condition_id} {is_neg_risk}', shell=True)
```

```javascript
// merge.js
if (isNegRiskMarket) {
    tx = negRiskAdapter.mergePositions(conditionId, amountToMerge)
} else {
    tx = conditionalTokens.mergePositions(
        USDC_ADDRESS,              // colateral
        ethers.constants.HashZero, // parentCollectionId = 0x0
        conditionId,
        [1, 2],                    // partition (YES=1, NO=2)
        amountToMerge
    )
}
// Gas limit hardcodeado: 10,000,000
// chainId: 137 (Polygon)
```

**Por qué Node.js:** El autor usa Gnosis Safe, y la librería de Gnosis Safe más madura era JS en el momento de escribirlo.

**Efecto:** min(YES, NO) tokens → misma cantidad de USDC. Actualiza `global_state.positions` localmente:
```python
set_position(token1, 'SELL', scaled_amt, 0, 'merge')
set_position(token2, 'SELL', scaled_amt, 0, 'merge')
```

---

## Parámetros configurables y qué controla cada uno

### Google Sheets — "Selected Markets" (por mercado)

| Columna | Tipo | Qué controla |
|---------|------|--------------|
| `question` | str | Identificador del mercado (join key) |
| `trade_size` | float | Tamaño de cada orden individual (USDC) |
| `max_size` | float | Máxima exposición por token (USDC). Cap absoluto: 250 USDC |
| `param_type` | str | Clave para buscar hyperparams en sheet "Hyperparameters" |
| `multiplier` | int/str | Multiplicador de tamaño para tokens < 10¢ (vacío = sin multiplicador) |

### Google Sheets — "All Markets" (calculado por update_markets.py)

| Columna | Tipo | Qué controla |
|---------|------|--------------|
| `tick_size` | float | Incremento mínimo de precio; determina decimales de redondeo |
| `min_size` | float | Tamaño mínimo de orden (del CLOB) |
| `max_spread` | float | Spread máximo del programa de incentivos (%) |
| `3_hour` | float | Volatilidad anualizada de 3h (log-returns de precios de 1min) |
| `best_bid`, `best_ask` | float | Precios de referencia para detectar divergencia > 5¢ |
| `neg_risk` | str | `'TRUE'`/`'FALSE'` — determina tipo de contrato en órdenes y merges |
| `token1`, `token2` | str | IDs de tokens YES y NO |
| `condition_id` | str | ID de mercado para WebSocket y merge |
| `gm_reward_per_100` | float | Reward geometrico esperado por $100 — métrica de selección |
| `volatility_sum` | float | Suma de volatilidades (filtro: < 20 para "Volatility Markets") |

### Google Sheets — "Hyperparameters" (por param_type)

| Param | Descripción |
|-------|-------------|
| `stop_loss_threshold` | % de PnL por debajo del cual se activa el stop-loss (ej: -15) |
| `spread_threshold` | Spread máximo permitido para ejecutar stop-loss (ej: 0.04) |
| `volatility_threshold` | Volatilidad 3h máxima para permitir compras (ej: 5.0) |
| `sleep_period` | Horas de cooldown tras un stop-loss antes de volver a comprar |
| `take_profit_threshold` | % sobre avgPrice para colocar la orden de take-profit |

### Hardcoded (no configurables sin tocar el código)

| Valor | Significado |
|-------|-------------|
| `250 USDC` | Cap absoluto de posición por token |
| `0.10 / 0.90` | Rango de precios válido para colocar buy orders |
| `0.005` | Diferencia de precio (0.5¢) para cancelar y recolocar orden |
| `0.10` (10%) | Diferencia de tamaño para cancelar y recolocar orden |
| `MIN_MERGE_SIZE = 20` | USDC mínimo para trigger de merge |
| `0.05` | Divergencia máxima (5¢) entre precio calculado y precio de Sheets |
| `15 segundos` | TTL de trades en estado MATCHED antes de limpiar |

---

## Experiencia real del autor (resultados, problemas encontrados, lecciones)

La URL de X.com (`x.com/defiance_cr/status/1906774862254800934`) no fue accesible con las herramientas disponibles — X.com requiere sesión autenticada y no devuelve contenido estático. **No se pudo obtener el tweet.**

Lo que sí se extrae directamente del README y del código:

- El autor declara explícitamente: **"In today's market, this bot is not profitable and will lose money."** Esto sugiere que fue rentable en algún momento anterior (cuando los rebates eran más altos o la competencia menor) pero ya no lo es.
- La estructura del código sugiere meses de iteración real: el manejo de casos edge (dust positions, stale trades, merge logic, IP separation) no se escribe sin haber visto esos problemas en producción.
- Usa **IP separada** para `update_markets.py` — indica que experimentó rate limiting.
- Tiene lógica de **sleep cooldown post stop-loss** — indica pérdidas reales por retención de inventario en mercados con movimiento unidireccional.
- La limitación de precio `[0.10, 0.90]` para buys — indica que probó operar en extremos y perdió (tokens a 5¢ pueden ir a 0 sin bounce).
- El cap de `250 USDC` hardcodeado probablemente refleja pérdidas máximas aceptadas en backtesting o producción.

---

## Qué funciona bien y qué tiene limitaciones

### Funciona bien

**Arquitectura event-driven con WebSocket:**
- `asyncio.Lock` por mercado evita race conditions
- SortedDict en memoria para el order book — O(log n) para updates
- Separación clara: canal market (book) + canal user (fills) + thread de sync (REST fallback)

**Lógica de merge automática:**
- Detecta posiciones simétricas y las convierte a USDC on-chain
- Doble verificación (memoria + on-chain) antes de ejecutar

**Scoring de mercados (data_updater):**
- Replica la fórmula real de rewards de Polymarket (`S = ((v-s)/v)^2`)
- Métrica `gm_reward_per_100` es una buena proxy para seleccionar mercados con buen reward/risk

**Google Sheets como configuración:**
- Permite cambiar parámetros sin reiniciar el bot
- Actualiza mercados cada 30s desde Sheets
- Bueno para gestión manual de qué mercados tradear

**Gestión de posición promedio (`avgPrice`):**
- Fórmula de VWAP correcta para compras acumulativas
- Floor de venta en avgPrice evita cristalizar pérdidas accidentalmente

### Limitaciones

**1. Rentabilidad cuestionable:**
El propio autor lo confirma. Los maker rebates de Polymarket no compensan el inventory risk en mercados con movimiento direccional fuerte.

**2. Sin señal direccional:**
El bot es completamente neutral — no usa ninguna información externa para decidir en qué lado del mercado tiene edge. Hace market making "ciego".

**3. Google Sheets como base de datos:**
- Latencia de lectura (HTTP a Google API)
- Límite de rate en el API de Google Sheets
- Punto único de fallo
- La Sheet del autor es pública y cualquiera puede ver qué mercados está tradeando

**4. Node.js subprocess para merge:**
- Spawn de proceso externo en cada merge es lento y frágil
- Sin manejo de errores robusto en el subprocess call
- Requiere instalar Node.js además de Python

**5. Límite de 250 USDC hardcodeado:**
Con $1K de capital, si se distribuye en 4+ mercados el cap es innecesariamente restrictivo y deja capital sin usar.

**6. Sin gestión de riesgo de cartera:**
El stop-loss y take-profit operan por mercado de forma aislada. No hay correlación entre mercados, ni límite de drawdown total de la cuenta.

**7. Sin manejo de neg-risk markets adecuado:**
Aunque detecta `neg_risk == 'TRUE'`, la lógica de pricing no ajusta por el hecho de que en neg-risk markets los outcomes no son independientes binarios.

**8. IP separation manual:**
Requiere infraestructura adicional — dos VPS o configuración de red para separar el scraper del bot.

---

## Qué podemos reusar directamente para nuestra estrategia

### Reusar íntegramente

**`poly_data/websocket_handlers.py`**
- Patrón de conexión dual (market + user channels)
- Manejo de reconexión con ping cada 5s
- Formato exacto de mensajes de suscripción y autenticación

**`poly_data/data_processing.py`**
- SortedDict para order book en memoria
- Manejo de mensajes `book` y `price_change`
- Lógica de `performing` para trades en vuelo

**`poly_data/polymarket_client.py`**
- Setup de `ClobClient` con `signature_type=2` y `funder`
- `get_position()`, `get_all_positions()`, `get_usdc_balance()`
- `cancel_all_asset()`, `cancel_all_market()`
- Addresses de contratos verificadas y correctas

**`poly_data/trading_utils.py` — `get_best_bid_ask_deets()`**
- Lógica de inversión de precio para token2 (NO side)
- Cálculo de liquidez dentro del N% del mid
- `find_best_price_with_size()` con min_size filtering

**`data_updater/find_markets.py` — scoring**
- Fórmula de reward de Polymarket replicada correctamente
- Cálculo de volatilidad anualizada desde precios de 1min
- `gm_reward_per_100` como métrica de selección

**`poly_merger/merge.js`**
- Lógica de merge completa para ambos tipos de mercado (normal y neg-risk)
- ABI mínimos correctos para los contratos relevantes

### Reusar con adaptaciones

**`poly_data/data_utils.py` — gestión de posiciones**
- La fórmula de `avgPrice` VWAP es correcta → reusar
- El throttle de 5s para `update_positions` → reusar
- La lógica de `update_orders` (dedup + cancel duplicates) → reusar

**`trading.py` — estructura de `perform_trade()`**
- El patrón de lock por mercado → reusar
- La lógica de merge trigger → reusar
- Stop-loss y take-profit como punto de partida → adaptar con parámetros propios

---

## Qué mejoraríamos

### 1. Eliminar la dependencia de Google Sheets
Sustituir por un archivo YAML/TOML local + hot-reload con `watchfiles` o similar. Elimina latencia, rate limits y exposición pública de la estrategia.

### 2. Añadir señal direccional
El market making puro es subóptimo con $1K. Combinar con:
- **Order flow imbalance**: `bid_sum / ask_sum` ya está calculado — usarlo para sesgar el tamaño BID vs ASK
- **Precio de referencia externo**: si tenemos señal de que el precio justo es diferente al mid del CLOB, poner más tamaño en el lado favorable

### 3. Reemplazar Node.js subprocess por Python puro
`web3.py` puede ejecutar `mergePositions` directamente. Elimina la dependencia de Node.js y el overhead del subprocess.

### 4. Kelly Criterion para sizing
```python
# Sustituir max_size fijo por sizing dinámico:
f = (p * (1/price - 1) - (1-p)) / (1/price - 1)
position_size = bankroll * f * kelly_fraction  # kelly_fraction = 0.25 conservador
```

### 5. Gestión de riesgo de cartera
- Límite de drawdown diario de la cuenta (no por mercado)
- Correlación entre mercados: no hacer market making en ambos lados de mercados correlacionados

### 6. Reemplazar `asyncio.sleep(2)` por sleep adaptativo
Con $1K en pocos mercados, 2s de sleep es innecesario. Para mercados de alta liquidez podría reducirse; para mercados de baja liquidez aumentarse.

### 7. Fix del divisor USDC
El bug de `10e5` del repo oficial de Polymarket/agents no está presente aquí — `polymarket_client.py` usa `/ 10**6` correctamente. Confirmar esto antes de usar.

### 8. Logging estructurado
El bot no tiene logging. Para producción con $1K real, necesitamos al menos:
- Cada orden colocada/cancelada con precio y tamaño
- Fills recibidos con P&L por fill
- Estado de posiciones cada N minutos

### 9. Tests unitarios para `get_order_prices` y `get_buy_sell_amount`
La lógica de pricing tiene muchos casos edge. Sin tests es difícil modificarla con confianza.

### 10. Soporte para múltiples wallets EOA
El bot usa Gnosis Safe obligatoriamente. Para $1K, una EOA standard es suficiente y más simple (`signature_type=0`, sin `funder`).

---

## Contexto crítico — hilo del autor en X (Abril 2025)

**Fuente:** https://x.com/defiance_cr/status/1906774862254800934
**Autor:** Daniel Sapkota (@defiance_cr) — co-founder de @lightconexyz

### Lo que realmente pasó (10 tweets)

**(1/10)** Durante la elección presidencial de EEUU 2024, Polymarket distribuía más de $25K DIARIOS en market maker rewards. El autor se convirtió en top 5 recipient midiendo volatilidad — algo que nadie más hacía sistemáticamente.

**(2/10)** Insight clave: "Cuando nuevos mercados son dominados por retail, emergen oportunidades fáciles. Las oportunidades duran más cuando el consenso es que el mercado es único. Pero cualquier precio que se mueve es lo mismo — puede ser modelado, su volatilidad calculada, y las estrategias backtested."

**(3/10)** Decodificó la fórmula de rewards de Polymarket:
- Los rewards se multiplican si posteas en ambos lados (bid/ask)
- Cuanto más cerca del midpoint, exponencialmente más rewards
- Fórmula: S(v,s) = ((v-s)/v)² · b

**(4/10)** Su sistema calculaba volatilidad en vivo. Cuando pidió datos históricos frecuentemente, **crasheó el servidor de Polymarket** — señal alcista: nadie más analizaba este dato sistemáticamente.

**(5/10)** Upgradeo a WebSockets y seleccionó mercados con mejor risk-reward: **baja volatilidad + alto reward esperado**. La gente proveía la misma liquidez en un mercado de 500% de volatilidad que en uno de 100% — por el mismo reward. Ese era el edge.

**(6/10)** El bot ponía órdenes YES y NO un tick sobre el nivel de 200 shares. Risk management:
- Salidas de posición dinámicas
- Stop-losses dinámicos
- Monitoreo continuo de trade flow
- Checks de imbalance del order book para proteger capital

**(7/10)** Los backtests revelaron algo poderoso: **señales de mercado estaban embebidas en la dinámica del order book y volúmenes acumulados ANTES de moverse en el precio.**

**(8/10)** Clasificó los mercados en **4 tipos** según patrones de liquidez y comportamiento. Cada tipo compartía los mismos parámetros para volatility thresholds y stop-losses — haciendo el sistema sorprendentemente escalable.

**(9/10)** "Esta estrategia demuestra que mientras la mayoría de makers se enfocan en news-based MMing, estrategias de market making más simples y bien aceptadas funcionaron bien en Polymarket."

**(10/10)** El repo incluye websocket handling, position merging, y performance tracking — lo que el SDK oficial no tenía.

---

## ⚠️ Por qué el autor dice que hoy no es rentable

El edge principal era el **programa de rewards de $25K/día** activo durante la elección de 2024.
- Sin ese programa activo, el market making ciego no cubre el inventory risk
- El spread solo NO es suficiente con capital pequeño y sin señal direccional

## ✅ Lo que sigue siendo válido y reutilizable

| Componente | Por qué sigue siendo válido |
|------------|----------------------------|
| Selección por volatilidad | El principio aplica a cualquier programa de rewards futuro |
| Señales en order book dynamics | Los backtests mostraron señales predictivas reales |
| WebSocket handlers | Infraestructura sólida independiente de la estrategia |
| Clasificación de mercados en 4 tipos | Framework escalable para cualquier estrategia |
| Stop-losses dinámicos | Risk management aplicable siempre |

## 🎯 Conclusión para nuestro proyecto

**El repo es referencia de infraestructura, no de estrategia.**
La estrategia que necesitamos para hoy debe tener su propio edge — no depender de rewards masivos.
El research 3/4 (fees y EV real 2026) definirá qué tiene EV positivo con $1K HOY.
