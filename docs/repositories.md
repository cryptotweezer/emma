# Repositorios analizados

## Repositorios oficiales de Polymarket

### Polymarket/agents
- **URL:** https://github.com/Polymarket/agents
- **Stars:** 1.7K | **Forks:** 440 | **Licencia:** MIT
- **Descripción:** Framework oficial de Polymarket para bots con IA
- **Stack:** Python 3.9, ChromaDB (RAG), LLMs, CLOB + Gamma API
- **Relevancia:** Blueprint oficial — integra noticias, LLMs y ejecución de órdenes
- **Instalar:** `pip install -r requirements.txt`
- **Ejecutar:** `python agents/application/trade.py`

### Polymarket/py-clob-client
- **URL:** https://github.com/Polymarket/py-clob-client
- **Descripción:** SDK oficial Python para CLOB
- **Instalar:** `pip install py-clob-client`

## Repositorios de estrategias (comunidad)

### warproxxx/poly-maker ⭐ PRIORITARIO
- **URL:** https://github.com/warproxxx/poly-maker
- **Stars:** 633 | **Forks:** 279
- **Estrategia:** Market making — mantiene órdenes en ambos lados del libro
- **Features:** WebSocket real-time, position management, Google Sheets para parámetros, poly_merger para consolidar posiciones
- **Nota del autor:** Publicó su experiencia real corriendo este bot

### ent0n29/polybot
- **URL:** https://github.com/ent0n29/polybot
- **Descripción:** Infraestructura completa de trading
- **Stack:** Spring Boot, Kafka, ClickHouse, Grafana
- **Uso:** Referencia para arquitectura de producción (overkill para $1K)

### dev-protocol/copytrading-bot-sport
- **URL:** https://github.com/dev-protocol/polymarket-copytrading-bot-sport
- **Estrategia:** Copy trading — replica trades de wallets exitosas
- **Features:** WebSocket mode para mercados rápidos, filtros por tipo de mercado

### dev-protocol/polymarket-arbitrage-bot
- **URL:** https://github.com/dev-protocol/polymarket-arbitrage-bot
- **Estrategia:** Arbitrage dump-and-hedge en mercados UP/DOWN de 15 minutos
- **Assets:** BTC, ETH, SOL, XRP

## Frameworks de trading que soportan Polymarket

### NautilusTrader
- **URL:** https://nautilustrader.io/docs/latest/integrations/polymarket/
- **Descripción:** Framework profesional de trading con integración Polymarket
- **Uso:** Evita reinventar infraestructura — útil en fases avanzadas
