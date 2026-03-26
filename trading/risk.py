import os

RISK_DEFAULTS = {
    'max_daily_loss_pct': 0.05,   # 5% pérdida diaria → parar
    'max_drawdown_pct': 0.15,     # 15% drawdown total → parar
    'max_open_positions': 5,      # máx posiciones abiertas
    'min_edge': 0.08,             # 8% edge mínimo
    'min_liquidity_usd': 1000,    # volumen mínimo del mercado
}


class RiskManager:
    def __init__(self, initial_balance: float, config: dict = None):
        self.initial_balance = initial_balance
        cfg = {**RISK_DEFAULTS, **(config or {})}

        self.max_daily_loss_pct = float(
            os.getenv('BOT_MAX_DAILY_LOSS', cfg['max_daily_loss_pct'])
        )
        self.max_drawdown_pct = float(
            os.getenv('BOT_MAX_DRAWDOWN', cfg['max_drawdown_pct'])
        )
        self.max_open_positions = int(
            os.getenv('BOT_MAX_POSITIONS', cfg['max_open_positions'])
        )
        self.min_edge = float(
            os.getenv('BOT_MIN_EDGE', cfg['min_edge'])
        )
        self.min_liquidity_usd = cfg['min_liquidity_usd']

    def can_trade(
        self,
        current_balance: float,
        daily_pnl: float,
        open_positions: int
    ) -> tuple[bool, str]:
        """
        Verifica todos los límites.
        Retorna (True, "") si puede tradear.
        Retorna (False, "motivo exacto") si no puede.
        """
        if self.is_daily_loss_exceeded(daily_pnl, current_balance):
            loss_pct = abs(daily_pnl / current_balance) if current_balance else 0
            return False, (
                f"daily loss {loss_pct:.1%} supera límite "
                f"{self.max_daily_loss_pct:.1%}"
            )

        if self.is_drawdown_exceeded(current_balance):
            dd = (current_balance - self.initial_balance) / self.initial_balance
            return False, (
                f"drawdown {dd:.1%} supera límite "
                f"-{self.max_drawdown_pct:.1%}"
            )

        if open_positions >= self.max_open_positions:
            return False, (
                f"posiciones abiertas {open_positions} = "
                f"máximo {self.max_open_positions}"
            )

        return True, ""

    def is_daily_loss_exceeded(
        self, daily_pnl: float, current_balance: float
    ) -> bool:
        if current_balance <= 0:
            return False
        return (daily_pnl / current_balance) < -self.max_daily_loss_pct

    def is_drawdown_exceeded(self, current_balance: float) -> bool:
        if self.initial_balance <= 0:
            return False
        dd = (current_balance - self.initial_balance) / self.initial_balance
        return dd < -self.max_drawdown_pct
