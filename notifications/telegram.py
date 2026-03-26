import os
import aiohttp
from datetime import datetime
from utils.logger import get_logger

logger = get_logger()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
CHAT_ID = os.getenv('TELEGRAM_USER_ID', '')
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def send_message(text: str) -> bool:
    """Envía mensaje a Telegram. Retorna True si OK, False si falla."""
    if not BOT_TOKEN or not CHAT_ID:
        logger.warning(
            "Telegram no configurado — "
            "TELEGRAM_BOT_TOKEN o CHAT_ID faltante"
        )
        return False
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/sendMessage",
                json={
                    'chat_id': CHAT_ID,
                    'text': text,
                    'parse_mode': 'HTML',
                },
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    return True
                logger.error(
                    f"Telegram error {resp.status}: {await resp.text()}"
                )
                return False
    except Exception as e:
        logger.error(f"Telegram send_message error: {e}")
        return False


async def notify_trade(trade: dict) -> None:
    """Notifica trade ejecutado."""
    side_emoji = "🟢" if trade['side'] == 'YES' else "🔴"
    msg = (
        f"{side_emoji} <b>TRADE EJECUTADO</b>\n"
        f"📋 {trade['question'][:70]}\n"
        f"Side: <b>{trade['side']}</b> @ {trade['entry_price']:.1%}\n"
        f"Edge: <b>{trade['edge']:.1%}</b>\n"
        f"Amount: <b>${trade['amount_sim']:.2f} SIM</b>\n"
        f"Kelly: {trade['kelly_fraction']:.1%}\n"
        f"Meta: {trade['metaculus_prob']:.1%} | "
        f"Mani: {trade['manifold_prob']:.1%}"
    )
    await send_message(msg)


async def notify_risk_limit(
    reason: str, daily_pnl: float, balance: float
) -> None:
    """Notifica cuando se activa un risk limit."""
    msg = (
        f"🚨 <b>RISK LIMIT ACTIVADO</b>\n"
        f"Motivo: {reason}\n"
        f"Bot en modo <b>monitor-only</b>\n"
        f"P&L hoy: ${daily_pnl:+.2f} SIM\n"
        f"Balance: ${balance:.2f} SIM"
    )
    await send_message(msg)


async def notify_daily_report(stats: dict) -> None:
    """Reporte diario del portfolio."""
    status = "🟢 ACTIVO" if stats.get('trading_active', True) else "🔴 PAUSADO"
    win_rate = stats.get('win_rate', 0)
    msg = (
        f"📊 <b>REPORTE DIARIO — "
        f"{datetime.utcnow().strftime('%Y-%m-%d')}</b>\n"
        f"Balance: <b>${stats.get('balance', 0):.2f} SIM</b>\n"
        f"P&L hoy: <b>${stats.get('daily_pnl', 0):+.2f}</b>\n"
        f"P&L total: <b>${stats.get('total_pnl', 0):+.2f}</b>\n"
        f"Trades hoy: {stats.get('total_trades', 0)} "
        f"({stats.get('win_trades', 0)}W/"
        f"{stats.get('loss_trades', 0)}L)\n"
        f"Win rate: {win_rate:.1%}\n"
        f"Posiciones abiertas: {stats.get('open_positions', 0)}\n"
        f"Status: {status}"
    )
    await send_message(msg)


async def notify_startup(
    balance: float, interval: int, min_edge: float
) -> None:
    """Notifica que el bot arrancó."""
    msg = (
        f"🚀 <b>EMMA BOT INICIADO</b>\n"
        f"Balance: <b>${balance:.2f} SIM</b>\n"
        f"Intervalo: {interval}s | Edge mínimo: {min_edge:.0%}\n"
        f"Modo: Paper Trading ($SIM)"
    )
    await send_message(msg)
