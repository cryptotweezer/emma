import aiohttp
import difflib
from typing import Optional

BASE_URL = "https://api.manifold.markets/v0/markets"


async def get_markets(
    session: aiohttp.ClientSession,
    limit: int = 100
) -> list[dict]:
    """Fetch markets de Manifold sin auth."""
    params = {"limit": limit}
    try:
        async with session.get(BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    except Exception:
        return []

    results = []
    for m in data:
        if m.get("isResolved", True):
            continue
        prob = m.get("probability")
        if prob is None:
            continue
        results.append({
            "id": m.get("id"),
            "question": m.get("question", ""),
            "probability": float(prob),
        })
    return results


async def find_match(
    markets: list[dict],
    market_title: str,
    threshold: float = 0.6
) -> Optional[float]:
    """Fuzzy match por título. Retorna probability o None."""
    best_ratio = 0.0
    best_prob = None

    title_lower = market_title.lower()
    for m in markets:
        ratio = difflib.SequenceMatcher(
            None, title_lower, m["question"].lower()
        ).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_prob = m["probability"]

    if best_ratio >= threshold:
        return best_prob
    return None
