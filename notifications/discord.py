"""
Discord notifications — Sprint 2
El servidor de Discord aún no existe.
Cuando esté listo: agregar DISCORD_WEBHOOK_URL al .env
"""
import os
from utils.logger import get_logger

logger = get_logger()

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')


async def send_message(text: str) -> bool:
    """Stub — Sprint 2."""
    if WEBHOOK_URL:
        # TODO Sprint 2: implementar webhook Discord
        pass
    return False


async def notify_trade(trade: dict) -> None:
    """Stub — Sprint 2."""
    pass


async def notify_daily_report(stats: dict) -> None:
    """Stub — Sprint 2."""
    pass
