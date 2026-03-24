# APIs de Polymarket — Referencia técnica

**Última verificación:** Marzo 2026
**Fuente:** https://agentbets.ai/guides/polymarket-api-guide/

## Arquitectura general

| API | URL Base | Auth | Propósito |
|-----|----------|------|-----------|
| CLOB | clob.polymarket.com | Parcial | Order book, precios, órdenes |
| Gamma | gamma-api.polymarket.com | No | Discovery de mercados, metadata |
| Data | data-api.polymarket.com | No | Posiciones, historial, leaderboards |
| Bridge | bridge.polymarket.com | Sí | Depósitos y retiros |

## WebSockets

| Canal | Endpoint | Auth | Propósito |
|-------|----------|------|-----------|
| Market | wss://ws-subscriptions-clob.polymarket.com/ws/market | No | Updates de order book |
| User | wss://ws-subscriptions-clob.polymarket.com/ws/user | Sí | Fills, cancelaciones |
| Sports | wss://sports-api.polymarket.com/ws | No | Scores en vivo |
| RTDS | wss://ws-live-data.polymarket.com | Opcional | Precios crypto, baja latencia |

> IMPORTANTE: WebSocket NO cuenta contra rate limits REST.

## Rate Limits

| API | Límite general | Endpoints clave |
|-----|---------------|-----------------|
| CLOB | 9,000 / 10s | /book 1,500/10s — /price 1,500/10s — POST /order 3,500/10s |
| Gamma | 4,000 / 10s | /markets 300/10s |
| Data | 1,000 / 10s | /trades 200/10s |

## Cómo funciona Polymarket (bajo el capó)
- Corre sobre Polygon blockchain (chain ID 137)
- Usa Conditional Token Framework (CTF) — ERC-1155
- CLOB es híbrido: matching off-chain, settlement on-chain
- Las órdenes son mensajes firmados con EIP-712
- USDC es el colateral en todas las posiciones
- Precios van de 0.00 a 1.00 (= probabilidad)
- YES + NO siempre suman ~$1.00 — cualquier desviación es arbitraje

## Tipos de wallet y firma

| Tipo | signature_type | funder requerido |
|------|---------------|-----------------|
| EOA (MetaMask) | 0 | No |
| Email / Magic wallet | 1 | Sí |
| Browser wallet proxy | 2 | Sí |

## SDKs oficiales

| Lenguaje | Paquete | Instalación |
|----------|---------|-------------|
| Python | py-clob-client | pip install py-clob-client |
| TypeScript | @polymarket/clob-client | npm install @polymarket/clob-client |
| Rust | polymarket-client-sdk | cargo add polymarket-client-sdk |

## Conceptos clave

### Token IDs
Cada outcome de mercado tiene un token_id único. Se obtienen desde Gamma API.

### Neg-Risk Markets
Mercados multi-outcome que comparten un pool de colateral. Requieren `negRisk: true` en las órdenes. SIEMPRE verificar el campo `neg_risk` antes de operar.

### Split / Merge
- Split: 1 USDC → 1 YES token + 1 NO token
- Merge: 1 YES + 1 NO → 1 USDC
- Redeem: 1 token ganador → 1 USDC (post-resolución)

### Fees
- Se aplican sobre el output (ganancias)
- Makers reciben rebates — cambia el cálculo de EV
- Verificar Builder Program para tasas actuales

## Datos de mercado — jerarquía
Series (ej: "US Presidential Election")
└── Event (ej: "2028 Presidential Election Winner")
    └── Market (ej: "Will X win?")
        └── Outcomes: YES / NO — cada uno con su token_id
