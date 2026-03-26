"""
Emma Trading Bot — loop principal asyncio
Corre 24/7 como proceso independiente.
"""
import asyncio
import os
import signal
from datetime import datetime, timedelta

import aiohttp
from dotenv import load_dotenv

# En servidor usa /root/.env; en local usa .env del directorio actual
if os.path.exists('/root/.env'):
    load_dotenv('/root/.env')
else:
    load_dotenv()

from utils.logger import get_logger
from storage.db import init_db, save_trade, save_signal, get_daily_stats
from signals.metaculus import get_questions, find_match as meta_match
from signals.manifold import get_markets, find_match as mani_match
from trading.edge import calculate_edge, kelly_size, determine_side
from trading.risk import RiskManager
from trading.executor import TradeExecutor
import notifications.telegram
import notifications.discord

logger = get_logger()

INTERVAL = int(os.getenv('BOT_INTERVAL', 300))   # 5 minutos
MIN_EDGE = float(os.getenv('BOT_MIN_EDGE', 0.08))


async def run_cycle(
    executor: TradeExecutor,
    risk_manager: RiskManager,
    metaculus_session: aiohttp.ClientSession,
    manifold_session: aiohttp.ClientSession,
):
    """Un ciclo completo de análisis y trading."""
    logger.info("=== INICIANDO CICLO ===")

    # 1. Estado actual
    balance = executor.get_balance()
    open_pos = executor.get_open_positions()
    today = datetime.utcnow().strftime('%Y-%m-%d')
    daily_stats = get_daily_stats(today)
    daily_pnl = daily_stats.get('daily_pnl', 0.0)

    # 2. Verificar risk limits
    can_trade, reason = risk_manager.can_trade(
        balance, daily_pnl, len(open_pos)
    )
    if not can_trade:
        logger.warning(f"RISK LIMIT: {reason} — modo monitor")
        await notifications.telegram.notify_risk_limit(
            reason=reason,
            daily_pnl=daily_pnl,
            balance=balance,
        )
        return

    # 3. Fetch señales
    meta_questions = await get_questions(
        metaculus_session, os.getenv('METACULUS_API_KEY', '')
    )
    mani_markets = await get_markets(manifold_session)
    logger.info(
        f"Señales: {len(meta_questions)} Metaculus, "
        f"{len(mani_markets)} Manifold"
    )

    # 4. Fetch mercados Simmer
    simmer_markets = executor.client.get_markets(limit=50)
    logger.info(f"Mercados Simmer activos: {len(simmer_markets)}")

    opportunities = 0

    # 5. Analizar cada mercado
    for market in simmer_markets:
        if market.status != 'active':
            continue

        title = market.question
        poly_price = market.external_price_yes or market.current_probability

        # Buscar match en ambas fuentes
        meta_prob = await meta_match(meta_questions, title)
        mani_prob = await mani_match(mani_markets, title)

        # Ambas fuentes requeridas
        if meta_prob is None or mani_prob is None:
            save_signal({
                'timestamp': datetime.utcnow().isoformat(),
                'market_id': market.id,
                'question': title,
                'metaculus_prob': meta_prob,
                'manifold_prob': mani_prob,
                'polymarket_price': poly_price,
                'edge': None,
                'action': 'SKIP',
                'skip_reason': 'no_match_both_sources',
            })
            continue

        # Calcular edge
        edge = calculate_edge(meta_prob, mani_prob, poly_price)

        if edge < MIN_EDGE:
            save_signal({
                'timestamp': datetime.utcnow().isoformat(),
                'market_id': market.id,
                'question': title[:80],
                'metaculus_prob': meta_prob,
                'manifold_prob': mani_prob,
                'polymarket_price': poly_price,
                'edge': edge,
                'action': 'SKIP',
                'skip_reason': f'edge_insuficiente_{edge:.3f}',
            })
            continue

        # ¡Edge detectado!
        opportunities += 1
        side = determine_side(meta_prob, mani_prob, poly_price)
        amount = kelly_size(edge, poly_price, balance)

        logger.info(f"OPORTUNIDAD: {title[:60]}")
        logger.info(
            f"  Edge: {edge:.1%} | Side: {side} | Amount: ${amount:.2f} SIM"
        )

        result = executor.execute_trade(
            market_id=market.id,
            question=title,
            side=side,
            amount=amount,
            entry_price=poly_price,
            metaculus_prob=meta_prob,
            manifold_prob=mani_prob,
            edge=edge,
            kelly_fraction=min(edge / (1 - poly_price), 0.15),
        )

        if result['success']:
            save_trade(result)
            save_signal({
                **result,
                'polymarket_price': poly_price,
                'action': 'TRADE',
                'skip_reason': None,
            })
            logger.info(f"TRADE OK: {side} ${amount:.2f} SIM")
            await notifications.telegram.notify_trade(result)
        else:
            logger.error(f"TRADE FAILED: {result.get('error')}")

    if opportunities == 0:
        logger.info(
            f"Sin oportunidades este ciclo — "
            f"{len(simmer_markets)} mercados analizados"
        )


async def daily_report_task(executor: TradeExecutor):
    """Corre en loop paralelo, envía reporte a las 08:00 UTC."""
    while True:
        now = datetime.utcnow()
        target = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now >= target:
            target = target + timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        today = datetime.utcnow().strftime('%Y-%m-%d')
        daily_stats = get_daily_stats(today)
        stats = {
            **daily_stats,
            'balance': executor.get_balance(),
            'total_pnl': executor.get_total_pnl(),
            'trading_active': True,
        }
        await notifications.telegram.notify_daily_report(stats)


async def main():
    logger.info("=" * 50)
    logger.info("EMMA TRADING BOT — INICIANDO")
    logger.info(f"Interval: {INTERVAL}s | Min edge: {MIN_EDGE:.0%}")
    logger.info("=" * 50)

    init_db()

    executor = TradeExecutor(api_key=os.getenv('SIMMER_API_KEY', ''))
    initial_balance = executor.get_balance()
    logger.info(f"Balance inicial: ${initial_balance:.2f} SIM")

    await notifications.telegram.notify_startup(
        balance=initial_balance,
        interval=INTERVAL,
        min_edge=MIN_EDGE,
    )

    risk_manager = RiskManager(initial_balance=initial_balance)

    running = True

    def handle_signal(sig, frame):
        nonlocal running
        logger.info("Señal de shutdown recibida — cerrando...")
        running = False

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    asyncio.create_task(daily_report_task(executor))

    async with aiohttp.ClientSession() as meta_session, \
               aiohttp.ClientSession() as mani_session:
        while running:
            try:
                await run_cycle(
                    executor, risk_manager, meta_session, mani_session
                )
            except Exception as e:
                logger.error(f"Error en ciclo: {e}", exc_info=True)

            logger.info(f"Próximo ciclo en {INTERVAL}s")
            await asyncio.sleep(INTERVAL)


if __name__ == '__main__':
    asyncio.run(main())
