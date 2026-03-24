# Opciones de estrategia — Análisis inicial

**Estado:** En evaluación
**Capital:** $1,000 USD
**Fecha:** Marzo 2026

## Restricciones del capital ($1K)
- Fees y spread se comen el margen rápido con capital pequeño
- El edge debe ser muy preciso y consistente
- Posiciones pequeñas por mercado para diversificar riesgo
- Kelly criterion será clave para sizing

## Opciones identificadas

### Opción A — Market Making pasivo
- **Mecanismo:** Poner órdenes en ambos lados del libro, ganar spread + maker rebates
- **Edge:** Rebates para makers + capturar spread entre bid/ask
- **Riesgo:** Inventory risk — quedarse con tokens del lado perdedor
- **Capital mínimo:** Bajo — funciona con $1K pero escala mejor con más
- **Referencia:** warproxxx/poly-maker
- **Complejidad:** Media

### Opción B — Arbitrage de información
- **Mecanismo:** Detectar mispricing usando fuentes externas antes que el mercado se ajuste
- **Edge:** Información más actualizada que el precio del mercado
- **Fuentes:** Noticias en tiempo real, Metaculus, odds de casas de apuestas, datos on-chain
- **Riesgo:** Velocidad de ejecución, adversarial selection
- **Capital mínimo:** Bajo — pero requiere señales confiables
- **Complejidad:** Alta

### Opción C — Copy trading de top wallets
- **Mecanismo:** Seguir wallets rentables usando Data API (público, sin auth)
- **Edge:** Seguir traders con track record demostrable on-chain
- **Riesgo:** Slippage al copiar, wallets pueden cambiar estrategia
- **Capital mínimo:** Muy bajo
- **Referencia:** dev-protocol/copytrading-bot-sport
- **Complejidad:** Baja-Media

## Próximos pasos
- [ ] Evaluar viabilidad real de cada opción con $1K
- [ ] Analizar fees reales por estrategia
- [ ] Definir criterios de selección de mercados
- [ ] Diseñar sistema de gestión de riesgo
