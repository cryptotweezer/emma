# Fees, rebates y EV real — Marzo 2026

**Fecha:** Marzo 2026
**Capital de referencia:** $1,000 USD

---

## Estructura de fees actualizada (Marzo 2026)

### La mayoría de mercados Polymarket — SIN FEES
Política, elecciones, eventos macro, mercados long-term:
- Makers: sin fee, sin rebate
- Takers: sin fee
- Spread = única fuente de ganancia para makers

### Mercados crypto (15min, 1H, 4H, Daily, Weekly) — CON FEES
- Takers: fee variable según probabilidad del mercado
  - Máximo ~1.56% cuando precio está en 0.50
  - Baja hacia 0% cuando precio se acerca a 0.00 o 1.00
- Makers: sin fee + reciben REBATE diario en USDC
- Fee se redistribuye 100% a makers — Polymarket no retiene nada
- Rebates se pagan diariamente proporcional a liquidez provista que fue tomada
- Consultar fee de un token: GET https://clob.polymarket.com/fee-rate?token_id={id}
  Respuesta: `{ "fee_rate_bps": 1000 }` (1000 bps = 10% = fee máximo)

### Mercados deportivos (NCAAB, Serie A — desde Feb 18, 2026)
- Solo mercados nuevos creados después del Feb 18, 2026
- Takers: fee máximo ~0.44% cuando precio está en 0.50
- Makers: rebate diario en USDC
- Mercados existentes anteriores: sin fee

### Polymarket US — CFTC regulado (mercado separado, requiere KYC)
- Taker fee: 30 basis points (0.30%)
- Maker rebate: 20 basis points (0.20%)
- Aplica a residentes USA con verificación de identidad

---

## Evolución del mercado (datos históricos verificados)

| Métrica | Valor |
|---------|-------|
| Spread promedio crypto 15min (2023) | 4.5% |
| Spread promedio crypto 15min (2025) | 1.2% |
| Profundidad order book Q3 2025 | $2.1M promedio |
| Volumen mensual Oct 2025 | $3.02B |
| Deportes como % del open interest | >60% |
| Wash trading estimado pre-fees (2025) | ~25% del volumen (estudio Columbia University) |
| Wash trading post-fees (2025) | ~5% del volumen |

**Estado del programa de rewards hoy vs 2024:**
- Elección 2024: $25,000+ diarios en rewards — excepcional, ya terminó
- Hoy: rewards provienen de taker fees redistribuidos — más sostenible pero menor magnitud
- El edge de poly-maker original YA NO APLICA sin ese programa masivo

---

## Análisis de EV por estrategia con $1,000 USD

### Estrategia A — Market Making crypto 15min (con rebates)

**Fee structure:** Takers pagan hasta 1.56% → makers reciben ese fee como rebate

**Cálculo estimado con $1K:**
- Capital activo en órdenes: ~$800 (reserva $200 para gestión)
- Si $400 de órdenes son ejecutadas por día → rebate ≈ $400 × 0.78% promedio = ~$3.12/día
- Anualizado sin pérdidas: ~$1,139/año (~114% anual)

**Problema: inventory risk**
- Mercados 15min tienen volatilidad extrema
- Quedarse atrapado 1 vez con $100 en el lado perdedor → pérdida de $15-30
- Con $1K, 3-4 eventos adversos eliminan semanas de rebates

**Veredicto: EV incierto.** El inventory risk supera el rebate con capital pequeño. Escala con $10K+.

---

### Estrategia B — Market Making mercados sin fee (política/eventos)

**Fee structure:** Cero fees para todos

**Cálculo con $1K:**
- Spread típico en mercados líquidos: 1-3 centavos (0.01-0.03)
- Posición por mercado con diversificación: ~$50-100
- Ganancia por trade ejecutado: $50 × 0.02 spread = $1.00
- Necesitas decenas de ejecuciones diarias para ser relevante
- Competencia: bots institucionales con $100K+ dominan los mercados líquidos

**Veredicto: Muy difícil competir con $1K.** Los makers institucionales tienen ventaja de escala y latencia irreversible con capital pequeño.

---

### Estrategia C — Arbitrage de información

**Fee structure:** Cero fees en mercados de política y eventos (la mayoría)

**Cálculo con $1K:**
- Escenario: encuentras mercado mispricedo en 5 centavos
- Compras $100 de YES a 0.45 cuando el valor real estimado es 0.50
- EV esperado: $100 × 0.05 = $5.00 por trade (5% sobre capital desplegado)
- Sin fees en mercados de política = EV puro sin fricción
- 10 trades correctos al mes de $100 c/u → +$50/mes = +5% mensual con 10% del capital

**Condiciones:**
- Requiere fuente de información confiable antes que el mercado la procese
- Requiere velocidad de ejecución (el mispricing dura minutos u horas, no días)
- El capital pequeño NO es desventaja — el edge es la información, no la escala

**Veredicto: MEJOR EV potencial con $1K.** Sin fees, edge basado en información, capital pequeño no limita.

---

### Estrategia D — Copy trading de top wallets

**Fee structure:** Taker en mercados con fees (peor caso: 1.56%)

**Cálculo con $1K:**
- Wallet top con 60% win rate histórico
- Trade promedio: $50. Ganancia si gana: $30. Pérdida si pierde: $50
- EV bruto por trade: 0.60 × $30 − 0.40 × $50 = $18 − $20 = **−$2.00**
- El slippage de copiar + fees destruyen el edge del trader original
- Con mercados sin fee: EV mejora pero el slippage sigue siendo el problema principal

**Veredicto: EV negativo con $1K.** Slippage y timing erosionan el edge. Solo viable con gran capital y latencia ultra-baja.

---

## Conclusión — Estrategia recomendada para $1K

### Ganadora: Estrategia C — Arbitrage de información en mercados sin fee

**Por qué esta y no las otras:**

| Criterio | MM Crypto | MM Sin Fee | Info Arb | Copy Trading |
|----------|-----------|------------|----------|--------------|
| Fees | Favorables (rebate) | Neutro (cero) | Neutro (cero) | Adversos |
| Ventaja con $1K | No (necesita escala) | No (necesita escala) | **Sí** | No |
| Dependencia de rewards externos | Alta | Baja | Ninguna | Ninguna |
| Riesgo de inventario | Muy alto | Medio | Bajo | Bajo |
| EV esperado hoy | Incierto | Negativo | **Positivo si hay señal** | Negativo |

**5 razones concretas:**
1. Cero fees en mercados de política y eventos long-term — sin fricción de entrada/salida
2. EV positivo puro cuando la señal es correcta — no depende de volumen ni escala
3. Capital pequeño no es desventaja — el edge es la información, no el tamaño de la posición
4. No hay competencia de bots institucionales en mercados de nicho o recién abiertos
5. Edge sostenible — no depende de programas de rewards externos que pueden terminar

**Condiciones que deben cumplirse para ser rentable:**
- Señal confiable con anticipación al mercado: Metaculus, noticias en tiempo real, odds de sportsbooks, datos on-chain
- Selección correcta de mercados: liquidez suficiente para ejecutar ($5K-$50K de volumen), no demasiada (mercados muy líquidos = precio eficiente = sin edge)
- Sizing conservador: nunca más del 10-15% del capital por posición ($100-150 max por trade)
- Velocidad de ejecución: el mispricing dura poco — ejecución en segundos tras detectar señal

**Riesgo principal a mitigar:**
- Señal incorrecta = pérdida directa sin protección de spread ni rebate
- Mitigación: diversificación en múltiples mercados independientes + límite de pérdida máxima por posición (ej: salir si el mercado se mueve 3 centavos en contra)

**Siguiente paso:**
Definir exactamente qué fuentes de información usaremos como señal y cómo detectar automáticamente el mispricing con código.
