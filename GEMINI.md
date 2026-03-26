# Polymarket Trading Bot - GEMINI.md

## Project Overview
This project aims to develop and deploy an automated trading bot for **Polymarket** with a sustainable positive Expected Value (EV). It follows a two-phase strategy:
1. **Phase 1 (Information Arbitrage):** Capitalizing on mispriced markets (politics, macro events) using external signals (Metaculus, Manifold).
2. **Phase 2 (Market Making):** Providing liquidity in high-volume markets (crypto) to earn maker rebates once capital exceeds $5,000.

The project is currently in **Sprint 1: Paper Trading 24/7**, running on a **Contabo VPS** using **OpenClaw** and the **Simmer SDK**.

## Tech Stack
- **Language:** Python 3.9+ (asyncio preferred)
- **Execution Layer:** 
  - [Simmer SDK](https://simmer.market/) (Paper trading & production execution)
  - `py-clob-client` (Advanced CLOB control)
- **Signal Sources:**
  - **Metaculus API:** Primary probability source.
  - **Manifold Markets API:** Secondary probability source (also via MCP Server).
  - **NOAA API:** Weather market forecasts.
  - **HashDive:** Smart money tracking and confirmation.
- **Infrastructure:**
  - **Server:** Contabo VPS10 (4 vCPU, 8 GB RAM) located in Seattle.
  - **Agent Runner:** [OpenClaw](https://openclaw.io/) (runs 24/7 as a systemd daemon).
  - **Identity:** "Emma" (@emma_openclawbot on Telegram).
  - **Database/Memory:** Gemini text-embedding-001 for semantic memory.
- **Blockchain:** Polygon (Chain ID 137), USDC collateral.

## Architecture & Logic
- **Signal Detection:** `edge = (Metaculus * 0.6) + (Manifold * 0.4) - Polymarket_Price`.
- **Threshold:** Signal is valid if `edge >= 8%` and both sources agree on the direction.
- **Position Sizing:** Kelly Criterion (capped at 15% of capital per position).
- **Safety Rails:** Simmer SDK limits ($100/trade, $500/day during paper trading).

## Development Conventions
- **Paper Trading First:** Mandatory 3 weeks/30 trades with >= 55% win rate before using real capital.
- **Documentation:** All strategic changes must be documented in `/research`.
- **Error Handling:** Avoid known bugs in official SDKs (USDC divisor 10e5 vs 10e6, infinite recursion in error handlers).
- **Tooling:** Use `uv` for dependency management where applicable (e.g., PolyClaw).
- **Secrets:** Never commit `.env` or `openclaw.json` containing API keys.

## Key Directories
- `/research`: In-depth analysis of strategies, signals, and tools.
- `/docs`: API documentation and repository references.
- `/skills`: Custom agent skills (e.g., `grimoire-polymarket`).
- `/dev_logs`: History of development sessions.

## Key Commands (Inferred)
- **Install Dependencies:** `pip install simmer-sdk py-clob-client`
- **Run Skill (uv):** `uv run ~/.openclaw/skills/polyclaw`
- **Server Access:** `ssh openclaw` (for tunnel/dashboard) or `ssh openclaw-shell`.
- **Bot Execution:** `python bot.py` (Planned entry point).

## Critical Bugs to Avoid (from CLAUDE.md)
1. **USDC Divisor:** Official agents use `10e5`, but Polymarket uses `1e6`. Correct this to avoid 10x sizing errors.
2. **Market Orders:** Some SDK versions always buy the wrong outcome; verify token selection.
3. **Recursion:** Watch out for infinite loops in error handlers that can crash the bot.
