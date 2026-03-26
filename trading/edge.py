def calculate_edge(
    metaculus_prob: float,
    manifold_prob: float,
    polymarket_price: float
) -> float:
    """
    edge = (metaculus × 0.6 + manifold × 0.4) - polymarket_price
    Positivo = YES está subvaluado en Polymarket
    Negativo = NO está subvaluado
    """
    signal = (metaculus_prob * 0.6) + (manifold_prob * 0.4)
    return signal - polymarket_price


def kelly_size(
    edge: float,
    polymarket_price: float,
    portfolio_total: float,
    max_fraction: float = 0.15
) -> float:
    """
    Kelly Criterion con cap.
    kelly = edge / (1 - polymarket_price)
    amount = portfolio_total × min(kelly, max_fraction)
    """
    if edge <= 0:
        return 0.0
    denominator = 1 - polymarket_price
    if denominator <= 0:
        return 0.0
    kelly = edge / denominator
    fraction = min(kelly, max_fraction)
    return round(portfolio_total * fraction, 2)


def determine_side(
    metaculus_prob: float,
    manifold_prob: float,
    polymarket_price: float
) -> str:
    """Retorna 'YES' o 'NO' según dónde está el edge."""
    signal = (metaculus_prob * 0.6) + (manifold_prob * 0.4)
    return 'YES' if signal > polymarket_price else 'NO'
