# Emma — Polymarket Trading Bot

## Qué es
Bot de paper trading automatizado para Polymarket con EV positivo.
Estrategia: info arbitrage usando señales de Metaculus + Manifold.
Capital inicial: $10,000 SIM (paper trading).
Criterio para dinero real: win rate ≥ 55% sostenido en ≥ 30 trades.

## Arquitectura
- Señales: Metaculus /api2/questions/ + Manifold /v0/markets
- Edge: (Metaculus×0.6 + Manifold×0.4) - Polymarket_precio ≥ 8%
- Sizing: Kelly Criterion con cap 15% del portfolio por posición
- Ejecución: simmer_sdk.SimmerClient (paper trading 24/7)
- Persistencia: SQLite en data/emma.db
- Alertas: Telegram via @emma_openclawbot
- Monitoreo: OpenClaw dashboard (http://127.0.0.1:18789)

## Estructura del proyecto
```
polymarket/
├── bot.py                  ← loop principal asyncio 24/7
├── signals/
│   ├── metaculus.py        ← señales Metaculus API
│   └── manifold.py         ← señales Manifold API
├── trading/
│   ├── edge.py             ← calculate_edge + kelly_size
│   ├── risk.py             ← RiskManager + stop-loss
│   └── executor.py         ← TradeExecutor (simmer_sdk)
├── storage/db.py           ← SQLite: trades, snapshots, signals
├── notifications/
│   ├── telegram.py         ← alertas Telegram
│   └── discord.py          ← stub Sprint 2
├── utils/logger.py         ← logging stdout + archivo
├── requirements.txt
├── emma-bot.service        ← systemd service
├── deploy.sh               ← script de deploy al servidor
└── .env.example            ← variables requeridas
```

## Deploy — primera vez en el servidor

```bash
# SSH al servidor
ssh openclaw-shell

# Clonar repo
cd /root
git clone https://github.com/cryptotweezer/emma.git emma

# Agregar estas variables al /root/.env existente:
# TELEGRAM_BOT_TOKEN=<token de @BotFather>
# TELEGRAM_USER_ID=<tu user ID de Telegram>
# BOT_INTERVAL=300
# BOT_MIN_EDGE=0.08
# BOT_MAX_KELLY=0.15
# BOT_MAX_DAILY_LOSS=0.05
# BOT_MAX_DRAWDOWN=0.15
# BOT_MAX_POSITIONS=5
# DISCORD_WEBHOOK_URL=

# Ejecutar deploy
bash /root/emma/deploy.sh

# Verificar que está corriendo
journalctl -u emma-bot -f
```

## Updates posteriores (flujo normal)

```bash
# En tu PC — después de cualquier cambio:
git push

# En el servidor:
cd /root/emma && git pull && systemctl restart emma-bot
```

## Comandos útiles en el servidor

| Comando | Descripción |
|---------|-------------|
| `journalctl -u emma-bot -f` | Logs en vivo |
| `systemctl status emma-bot` | Estado del servicio |
| `systemctl stop emma-bot` | Parar el bot |
| `systemctl restart emma-bot` | Reiniciar |
| `tail -f /root/emma/logs/bot.log` | Bot logs propios |
| `sqlite3 data/emma.db "SELECT * FROM trades"` | Ver trades |

## Variables de entorno requeridas

Ver `.env.example` para la lista completa con descripciones.

Variables críticas para Sprint 1:
- `SIMMER_API_KEY` — ejecución de trades
- `METACULUS_API_KEY` — señal primaria (60%)
- `TELEGRAM_BOT_TOKEN` — alertas Emma
- `TELEGRAM_USER_ID` — tu ID de Telegram

Variables para Sprint 2 (dinero real):
- `POLYMARKET_API_KEY`, `POLYMARKET_API_SECRET`
- `POLYMARKET_API_PASSPHRASE`, `POLYMARKET_FUNDER`

## Risk Management
- Stop diario: si pérdida > 5% del balance → parar trades
- Stop total: si drawdown > 15% → parar trades
- Max posiciones simultáneas: 5
- Max Kelly por posición: 15%
- Edge mínimo requerido: 8%
