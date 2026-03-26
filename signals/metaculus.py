import aiohttp
import difflib
from typing import Optional

BASE_URL = "https://www.metaculus.com/api2/questions/"


async def get_questions(
    session: aiohttp.ClientSession,
    api_key: str,
    limit: int = 100
) -> list[dict]:
    """Fetch questions de Metaculus con auth."""
    headers = {"Authorization": f"Token {api_key}"}
    params = {
        "limit": limit,
        "has_group": "false",
        "status": "open",
        "order_by": "-activity",
    }
    try:
        async with session.get(BASE_URL, headers=headers, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    except Exception:
        return []

    results = []
    for q in data.get("results", []):
        cp = q.get("community_prediction")
        if cp is None:
            continue
        prob = cp.get("q2")
        if prob is None:
            continue
        results.append({
            "id": q.get("id"),
            "title": q.get("title", ""),
            "probability": float(prob),
        })
    return results


async def find_match(
    questions: list[dict],
    market_title: str,
    threshold: float = 0.6
) -> Optional[float]:
    """Fuzzy match por título. Retorna probability o None."""
    best_ratio = 0.0
    best_prob = None

    title_lower = market_title.lower()
    for q in questions:
        ratio = difflib.SequenceMatcher(
            None, title_lower, q["title"].lower()
        ).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_prob = q["probability"]

    if best_ratio >= threshold:
        return best_prob
    return None
