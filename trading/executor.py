import simmer_sdk
from datetime import datetime
from utils.logger import get_logger

logger = get_logger()


class TradeExecutor:
    def __init__(self, api_key: str):
        self.client = simmer_sdk.SimmerClient(api_key=api_key)

    def get_balance(self) -> float:
        """Balance actual en $SIM desde get_portfolio()."""
        try:
            portfolio = self.client.get_portfolio()
            if portfolio is None:
                return 0.0
            for key in ('cash', 'balance', 'buying_power', 'portfolio_value'):
                if key in portfolio and portfolio[key] is not None:
                    return float(portfolio[key])
            logger.warning(f"get_balance: claves disponibles: {list(portfolio.keys())}")
            return 0.0
        except Exception as e:
            logger.error(f"get_balance error: {e}")
            return 0.0

    def get_open_positions(self) -> list:
        """Posiciones abiertas actuales."""
        try:
            return self.client.get_positions() or []
        except Exception as e:
            logger.error(f"get_open_positions error: {e}")
            return []

    def get_held_markets(self) -> dict:
        """Markets donde tenemos posición abierta."""
        try:
            return self.client.get_held_markets() or {}
        except Exception as e:
            logger.error(f"get_held_markets error: {e}")
            return {}

    def get_total_pnl(self) -> float:
        """P&L total acumulado."""
        try:
            return float(self.client.get_total_pnl() or 0.0)
        except Exception as e:
            logger.error(f"get_total_pnl error: {e}")
            return 0.0

    def execute_trade(
        self,
        market_id: str,
        question: str,
        side: str,
        amount: float,
        entry_price: float,
        metaculus_prob: float,
        manifold_prob: float,
        edge: float,
        kelly_fraction: float,
    ) -> dict:
        """
        Ejecuta trade real via simmer_sdk.trade().
        Nunca lanza excepciones — captura todo y retorna resultado.
        """
        base = {
            'timestamp': datetime.utcnow().isoformat(),
            'market_id': market_id,
            'question': question,
            'side': side,
            'amount_sim': amount,
            'entry_price': entry_price,
            'metaculus_prob': metaculus_prob,
            'manifold_prob': manifold_prob,
            'edge': edge,
            'kelly_fraction': kelly_fraction,
        }
        try:
            result = self.client.trade(
                market_id=market_id,
                side=side,
                amount=amount,
                action='buy',
                reasoning=(
                    f"edge={edge:.3f} meta={metaculus_prob:.3f} "
                    f"mani={manifold_prob:.3f}"
                ),
            )
            trade_id = None
            if hasattr(result, 'id'):
                trade_id = str(result.id)
            elif hasattr(result, 'trade_id'):
                trade_id = str(result.trade_id)
            elif isinstance(result, dict):
                trade_id = str(result.get('id') or result.get('trade_id', ''))

            logger.info(
                f"Trade ejecutado: {side} ${amount:.2f} SIM "
                f"en {question[:50]}"
            )
            return {**base, 'success': True, 'trade_id': trade_id, 'error': None}

        except Exception as e:
            logger.error(
                f"execute_trade FAILED: {e} | "
                f"market={market_id} side={side} amount={amount}"
            )
            return {**base, 'success': False, 'trade_id': None, 'error': str(e)}
