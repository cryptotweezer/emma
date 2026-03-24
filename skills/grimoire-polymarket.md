# Grimoire Polymarket Skill

**Fuente:** https://skills.sh/franalgaba/grimoire/grimoire-polymarket
**Instalar:** `npx skills add https://github.com/franalgaba/grimoire --skill grimoire-polymarket`
**Installs:** 10.6K — Compatible con Claude Code, Codex, Cursor, Cline

## Qué hace
Skill dedicada a Polymarket: market discovery, CLOB data, y order management a través del adaptador `polymarket` de Grimoire.

## Invocaciones preferidas
- `grimoire venue polymarket ...`
- `npx -y @grimoirelabs/cli venue polymarket ...` (sin instalación)

## Preflight recomendado
```bash
grimoire venue doctor --adapter polymarket --json
grimoire venue polymarket info --format json
```

## Comandos principales

### Discovery
```bash
# Buscar mercados por query
grimoire venue polymarket search-markets --query bitcoin --active-only true --open-only true --format json

# Buscar por categoría/liga
grimoire venue polymarket search-markets --category sports --league "la liga" --active-only true --format json

# Listar mercados
grimoire venue polymarket markets list --limit 25 --format json

# Listar eventos
grimoire venue polymarket events list --limit 25 --format json
```

### CLOB (Order Book)
```bash
# Ver order book de un token
grimoire venue polymarket clob book <token_id> --format json

# Precio midpoint
grimoire venue polymarket clob midpoint <token_id> --format json

# Precio de compra/venta
grimoire venue polymarket clob price <token_id> --side buy --format json
```

### Order Management (requiere auth)
```bash
# Ver orden específica
grimoire venue polymarket clob order <order_id> --format json

# Historial de trades
grimoire venue polymarket clob trades --market <condition_id> --format json

# Órdenes abiertas
grimoire venue polymarket clob orders --market <condition_id> --format json

# Balance
grimoire venue polymarket clob balance --asset-type conditional --token <token_id> --format json
```

## Configuración de entorno
```bash
# Requerido
POLYMARKET_PRIVATE_KEY=

# Opcionales
POLYMARKET_API_KEY=
POLYMARKET_API_SECRET=
POLYMARKET_API_PASSPHRASE=
POLYMARKET_SIGNATURE_TYPE=   # 0=EOA, 1=POLY_PROXY, 2=GNOSIS_SAFE
POLYMARKET_FUNDER=
```

## Prerequisito: CLI oficial de Polymarket
```bash
brew tap Polymarket/polymarket-cli && brew install polymarket
```

## Tipos de órdenes
| Tipo | Descripción |
|------|-------------|
| GTC  | Good Til Cancelled — limit order que queda en el libro |
| GTD  | Good Til Date — limit con fecha de expiración |
| FOK  | Fill or Kill — ejecuta completo o rechaza |
| FAK  | Fill and Kill — ejecuta lo disponible, cancela el resto |

## Grupos bloqueados (seguridad)
wallet, bridge, approve, ctf, setup, upgrade, shell
