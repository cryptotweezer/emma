# Fuentes de señal — Análisis profundo
**Fecha:** 2026-03-21
**Investigadas en vivo:** Polysights, Inside Edge, HashDive

---

## Resumen ejecutivo
Existen 3 herramientas de análisis que pueden actuar como
fuentes de señal para nuestro bot sin construir nada desde cero.
La combinación de las tres cubre todos los tipos de edge que buscamos.

---

## 1. Inside Edge ⭐ PRIORITARIA — señal principal

**URL:** https://inside.fyi
**Tipo:** AI probability vs Polymarket price comparison
**Acceso:** Login con Google (gratuito)

### Qué hace exactamente
Compara estimaciones de probabilidad de IA independiente
vs precio actual de Polymarket.
Cuando hay divergencia → oportunidad de trading.

### Métricas en vivo (verificadas 2026-03-21)
- Mercados analizados: 2,900+
- Edge promedio encontrado: 13.7%
- Ejemplo real: SpaceX IPO → Mercado 63% vs IA 91% = +28% edge

### Por qué es perfecta para nuestra estrategia
- Hace exactamente lo que queremos hacer manualmente
- 13.7% de edge promedio > nuestro umbral del 5%
- Cero fees en mercados de política/eventos = EV puro
- Confidence scoring incluido (High/Medium/Low)

### Limitaciones
- Requiere login para ver el screener completo
- No tiene API pública documentada (a verificar)
- El modelo de IA no está documentado públicamente

### Cómo usarla en nuestro bot
Opción A: Scraping del screener (si no hay API)
Opción B: Usar como validación manual de señales
Opción C: Contactar para acceso API

---

## 2. HashDive ⭐ PRIORITARIA — smart money + insider tracking

**URL:** https://hashdive.com
**Tipo:** Analytics completo + whale/insider tracking
**Acceso:** Free básico, Pro con más features

### Módulos disponibles (verificados en vivo)
- **Screener:** mercados por volumen, precio delta, liquidez
- **Smart Scores:** rating -100 a +100 de traders por performance
- **Smart Trades Live:** trades de wallets con Smart Score alto
- **Smart Trader Explorer:** explorar wallets rentables
- **Whale Positions:** posiciones grandes en tiempo real
- **Whale Trades:** trades de ballenas al momento
- **Unusual Trades:** trades anormales flaggeados automáticamente
- **Insider Detection:** detecta actividad insider
- **Potential Insiders Dashboard:** NUEVO — wallets sospechosas

### Dato clave del screener (vivo hoy)
Mercados con mayor volumen ahora mismo:
Kansas Jayhawks vs Baptist: $3.36M, 127 traders
UCLA vs UCF: $2.17M, 264 traders
Raptors vs Nuggets: $2.16M, 192 traders

### Por qué es valiosa como fuente de señal
- Smart Scores identifica quién gana consistentemente
- Insider Detection = señal de información privilegiada
- Unusual Trades = alguien sabe algo antes que el mercado
- Todo público y gratuito

### API
- Tiene API documentada: https://hashdive.com/api
- A investigar en detalle

### Cómo usarla en nuestro bot
Señal secundaria: cuando una wallet con Smart Score > 80
entra a un mercado donde Inside Edge muestra edge > 10%
→ señal de alta confianza para entrar

---

## 3. Polysights — análisis + workflows + insider finder

**URL:** https://app.polysights.xyz (redirige a polysights.xyz)
**Tipo:** Plataforma completa de analytics con 4 módulos
**Acceso:** BETA — signup requerido, versión V1 anunciada

### Módulos (verificados en vivo)
- **Discover:** agrega mercados activos + analiza sharp traders
- **Intelligence:** Insider Finder con montos ($802K, $163K detectados)
- **Workflows:** automatización de señales → acciones
- **Terminal:** ejecución institucional

### Recently Flagged (datos en vivo 2026-03-21)
- Wallet 0x1fd4... → "Putin out as President by Dec 2026?" — $11,297
- Wallet Goober3 → "Trump ends military ops against Iran by March 31" — $5,562
- Wallet 0x8072... → "Iran x Israel/US conflict ends by June 30" — $1,563
Estas wallets están siendo monitoreadas por actividad inusual

### Diferenciador clave
El módulo Workflows permite crear cadenas automáticas:
señal detectada → acción definida (alerta, trade, etc.)
Esto es automatización de señales sin código

### Estado actual
- En BETA, signup para V1 abierto
- Usando Vertex AI + Gemini + Perplexity internamente
- Sin API pública documentada aún

---

## 4. Fuentes de señal externas complementarias

### Metaculus
- **URL:** https://metaculus.com
- **Tipo:** Plataforma de forecasting con probabilidades de referencia
- **API:** Requiere API key en el header Authorization (403 sin auth desde VPS)
- **Edge:** Sus probabilidades agregadas son más precisas que Polymarket en eventos de largo plazo
- **Uso:** Comparar Metaculus prob vs Polymarket precio = señal directa

### NOAA (National Oceanic and Atmospheric Administration)
- **URL:** https://api.weather.gov
- **Tipo:** Datos oficiales de clima de EEUU
- **API:** Gratuita, sin key requerida
- **Edge:** Weather markets en Polymarket frecuentemente mal pricados
- **Uso:** Comparar forecast NOAA vs precio del bracket = señal directa
- **Ya implementado en:** polymarket-weather-trader skill de Simmer

### RSS feeds de noticias
- Reuters, AP, BBC: feeds RSS públicos y gratuitos
- **Edge:** Noticias que mueven mercados llegan antes que el repricing
- **Uso:** Detectar eventos relevantes → identificar mercados afectados
- **Ya implementado en:** polymarket-signal-sniper skill de Simmer

### Manifold Markets
- **URL:** https://manifold.markets
- **API:** Pública, 500 req/min, sin costo
- **Edge:** Plataforma de play money con probabilidades independientes
- **Uso:** Tercera fuente de probabilidad para triangular con Metaculus e Inside Edge

---

## Stack de señales recomendado para el bot

### Señal primaria (mayor confianza)
Inside Edge edge > 10% + confidence "High"
→ IA independiente detecta mispricing significativo

### Señal secundaria (confirmación)
HashDive Smart Score wallet > 80 entra al mismo mercado
→ Smart money confirma la dirección

### Señal terciaria (contexto)
Metaculus probability diverge > 8% de Polymarket
→ Forecasters expertos también ven el mispricing

### Señal de nicho (weather markets)
NOAA forecast diverge > 15% del bracket de Polymarket
→ Datos oficiales vs precio del mercado

### Señal de alerta roja (NO entrar)
HashDive Insider Detection flaggea el mercado
→ Puede haber información privilegiada en el otro lado

---

## Prioridad de implementación

### Sprint 1 (primero)
- [ ] Crear cuenta en Inside Edge (Google login)
- [ ] Verificar si tiene API o requiere scraping
- [ ] Crear cuenta en HashDive
- [ ] Verificar API de HashDive

### Sprint 2 (después)
- [ ] Integrar Metaculus API (documentada y pública)
- [ ] Integrar NOAA API (gratuita, sin key)
- [ ] Explorar Polysights V1 cuando salga

### Pendiente de investigar
- [ ] Polyseer (open source, Bayesian aggregation)
- [ ] Alphascope (señales en tiempo real)
- [ ] PolyRadar (múltiples modelos con confidence)

---

## Investigación de APIs — Resultados (2026-03-21)

### Inside Edge — Sin API pública
**Hallazgo:** No tiene API pública documentada.
Network requests analizados: solo Google Analytics + Stripe (pagos).
Todo el procesamiento es server-side sin endpoints expuestos.

**Opciones para automatizar:**
1. Contactar equipo en inside.fyi/contact para solicitar acceso API
2. Scraping autenticado (requiere Google login — riesgo de ToS)
3. **MEJOR OPCIÓN: Replicar la lógica nosotros mismos**
   - Inside Edge hace: Metaculus prob vs Polymarket precio = delta
   - Podemos hacer exactamente lo mismo con APIs públicas
   - Resultado: nuestro propio "Inside Edge" sin depender de terceros

### HashDive — API existe, documentación limitada
**Hallazgo:** Tiene sección /api en la web pero sin docs públicas detalladas.
Partnership oficial con Polymarket desde Septiembre 2025 → datos confiables.
Contacto para API: contact@hashdive.com

**Datos disponibles sin API (públicos en la web):**
- Smart Scores de cualquier wallet (endpoint web scrappeable)
- Screener de mercados con filtros
- Unusual Trades en tiempo real
- Insider Detection dashboard

### Conclusión estratégica más importante

No necesitamos APIs de terceros para replicar el edge de Inside Edge.
La lógica es pública y simple:
edge = metaculus_probability - polymarket_price
si edge > 0.08 (8%) Y confidence > "Medium" → señal de entrada

Podemos construir nuestro propio detector con:
- Metaculus API (pública, gratuita) → probabilidad de referencia
- Polymarket Gamma API (pública, gratuita) → precio actual
- Delta calculation → edge %
- Threshold filter → solo señales con edge > 8%

Esto nos da independencia total y podemos añadir más fuentes:
- Manifold Markets API (pública, 500 req/min) → segunda referencia
- NOAA API (pública, sin key) → weather markets
- HashDive Smart Scores (web scraping o contactar API) → confirmación

## Stack de señales final recomendado

### Señal primaria — nuestro propio detector de mispricing
FUENTES:    Metaculus API + Manifold API
LÓGICA:     promedio_externo - polymarket_precio = edge %
UMBRAL:     edge > 8% con alta confianza → señal
MERCADOS:   política, eventos, macro (cero fees)

### Señal secundaria — confirmación de smart money
FUENTE:     HashDive Smart Trades / Whale Trades (web o API)
LÓGICA:     wallet con Smart Score > 70 entra al mismo mercado
ACCIÓN:     aumenta confianza de la señal primaria

### Señal de nicho — weather markets
FUENTE:     NOAA API weather.gov (gratuita, sin key)
LÓGICA:     NOAA forecast vs precio del bracket en Polymarket
UMBRAL:     diferencia > 15% → señal
MARKETS:    temperatura NYC/Miami/Chicago en Simmer/Polymarket

### Señal de alerta roja — NO entrar
FUENTE:     HashDive Insider Detection / Unusual Trades
LÓGICA:     mercado flaggeado como posible insider → evitar
RAZÓN:      estamos en el lado equivocado de información privilegiada

## Próximas acciones concretas
- [ ] Crear cuenta en Inside Edge (Google) — ver screener completo
- [ ] Contactar HashDive para acceso API: contact@hashdive.com
- [ ] Explorar Metaculus API en profundidad (Sprint 1)
- [ ] Explorar Manifold API como segunda fuente (Sprint 1)
- [ ] Evaluar NOAA API para weather markets (Sprint 1)

---

## APIs verificadas — research completo 2026-03-21

### Metaculus API ⭐ FUENTE PRIMARIA

**Base URL:** https://www.metaculus.com/api2/
**Auth:** Requiere API key en header (403 sin auth desde VPS)
**Docs:** metaculus.com/api/ (OpenAPI 3.0)
**Framework oficial Python:** github.com/Metaculus/forecasting-tools

Endpoints clave:
- GET /api2/questions/ — lista preguntas con filtros
- GET /api2/questions/{id}/ — pregunta específica con probabilidad actual
- Parámetros: status (open/closed/resolved), search, ordering

Datos que provee:
- community_prediction.full.q2 → mediana de probabilidad de la comunidad
- question.title → título de la pregunta
- question.resolution_criteria → criterios de resolución
- question.close_time → cuándo cierra

Cómo usarlo como señal:
```python
import requests
# Requiere auth header
headers = {"Authorization": f"Token {METACULUS_API_KEY}"}
r = requests.get("https://www.metaculus.com/api2/questions/", headers=headers,
    params={"status": "open", "search": "election"})
for q in r.json()["results"]:
    prob = q["community_prediction"]["full"]["q2"]
    print(f"{q['title']}: {prob:.1%}")
```

Relevancia para nuestro bot: CRÍTICA
Metaculus tiene forecasters expertos con track record demostrable.
Sus probabilidades son más precisas que Polymarket en eventos de largo plazo.

---

### Manifold Markets API ⭐ FUENTE SECUNDARIA + MCP SERVER

**Base URL:** https://api.manifold.markets
**Auth:** No requerida para lectura pública
**Rate limit:** 500 req/min — el más generoso de todos
**Docs:** docs.manifold.markets/api
**MCP Server:** github.com/bmorphism/manifold-mcp-server (MIT)

HALLAZGO CRÍTICO: Manifold tiene MCP Server oficial
Se conecta directamente a Claude Code sin código de integración.
Configuración en .mcp.json:
```json
{
  "mcpServers": {
    "manifold": {
      "command": "node",
      "args": ["/path/to/manifold-mcp-server/build/index.js"],
      "env": { "MANIFOLD_API_KEY": "tu_key_aqui" }
    }
  }
}
```

Endpoints clave:
- GET /v0/markets — lista mercados con filtros
- GET /v0/market/{slug} — mercado específico con probabilidad
- GET /v0/search-markets?term=X — buscar por término

Cómo usarlo como señal:
```python
r = requests.get("https://api.manifold.markets/v0/markets",
    params={"limit": 50, "sort": "liquidity"})
for m in r.json():
    prob = m["probability"]  # 0.0 a 1.0
    print(f"{m['question']}: {prob:.1%}")
```

Nota importante: Manifold usa play money (Mana).
Sus probabilidades son válidas como referencia — traders compiten
por prestigio, lo que genera incentivos reales para ser precisos.

---

### NOAA API ⭐ FUENTE PARA WEATHER MARKETS

**Base URL:** https://api.weather.gov
**Auth:** Sin API key, sin registro
**Rate limit:** Razonable para uso normal
**Docs:** weather.gov/documentation/services-web-api

Endpoints clave:
- GET /points/{lat},{lon} — obtener forecast URL para una ubicación
- GET /gridpoints/{office}/{x},{y}/forecast — forecast de 7 días
- GET /gridpoints/{office}/{x},{y}/forecast/hourly — forecast por hora

Ciudades principales para weather markets:
- NYC: lat=40.71, lon=-74.00
- Miami: lat=25.77, lon=-80.19
- Chicago: lat=41.85, lon=-87.65
- Los Angeles: lat=34.05, lon=-118.24
- Seattle: lat=47.61, lon=-122.33

Cómo generar señal:
1. Obtener forecast NOAA para la ciudad y fecha del mercado
2. Comparar temperatura predicha vs bracket de Polymarket
3. Si el bracket está mal pricado → señal de entrada

---

## Lógica del detector de mispricing (nuestra versión de Inside Edge)
```python
def calculate_edge(metaculus_prob, manifold_prob, polymarket_price):
    # Promedio ponderado de fuentes externas
    external_consensus = (metaculus_prob * 0.6) + (manifold_prob * 0.4)

    # Edge = diferencia entre consenso externo y precio de mercado
    edge = external_consensus - polymarket_price

    # Confianza alta si ambas fuentes apuntan en la misma dirección
    sources_agree = (metaculus_prob > polymarket_price) == (manifold_prob > polymarket_price)

    return {
        "edge": edge,
        "edge_pct": f"{edge:.1%}",
        "high_confidence": sources_agree and abs(edge) >= 0.08,
        "signal": "BUY YES" if edge > 0.08 and sources_agree else
                  "BUY NO" if edge < -0.08 and sources_agree else "NO SIGNAL"
    }
```

Umbral mínimo: 8% de edge con ambas fuentes de acuerdo
Por qué 8%: Inside Edge muestra 13.7% promedio en el mercado,
pero nosotros solo entramos en las mejores oportunidades.

---

## Stack de señales completo y definitivo

| Prioridad | Fuente | Auth | Costo | Uso |
|-----------|--------|------|-------|-----|
| 1 | Metaculus API | No | Gratis | Probabilidad primaria |
| 2 | Manifold API | No* | Gratis | Probabilidad secundaria |
| 3 | NOAA API | No | Gratis | Weather markets |
| 4 | HashDive | Contactar | TBD | Smart money confirmación |
| 5 | Simmer AI Divergence | Registro | Gratis/$SIM | Validación adicional |

*Manifold requiere API key solo para operaciones autenticadas (betting)

## Próximos pasos concretos — Sprint 1

### Semana 1 — Sin código, solo setup
- [ ] Crear cuenta en Metaculus y obtener API key (opcional, mejora rate limit)
- [ ] Crear cuenta en Manifold y obtener API key
- [ ] Instalar Manifold MCP Server en Claude Code
- [ ] Crear cuenta en Inside Edge (Google login) — ver screener completo
- [ ] Contactar HashDive: contact@hashdive.com para acceso API

### Semana 2 — Primer código de señal
- [ ] Script Python: consultar Metaculus + Manifold para mercados abiertos
- [ ] Script Python: calcular edge vs Polymarket Gamma API
- [ ] Script Python: NOAA forecast vs weather brackets en Polymarket
- [ ] Paper trade: ejecutar señales en Simmer $SIM venue
