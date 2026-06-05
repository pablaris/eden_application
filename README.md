# EDEN Quant Assessment — Methodology Assumptions

## Data source

Candidate price data comes from the provided EOD CSV files:

- `orion_eod.csv`
- `cleanergy_eod.csv`
- `novaterra_eod.csv`

These CSVs are treated as the primary source for candidate price performance because the companies are fictional.

## Return convention

Main performance metrics use simple daily returns calculated from closing prices:

```python
daily_return = close_price.pct_change()
```

Log returns may be used only for distribution diagnostics such as skewness, kurtosis, histogram analysis, QQ plots, or parametric VaR checks.

## Annualization

We assume 252 trading days per year.

## Annualized return

Annualized return is calculated geometrically from the start and end price:

```python
annualized_return = (ending_price / starting_price) ** (252 / number_of_trading_days) - 1
```

## Annualized volatility

Annualized volatility is calculated as:

```python
annualized_volatility = daily_returns.std() * sqrt(252)
```

## Sharpe ratio

Sharpe ratios use a 3% annual risk-free rate assumption:

```python
sharpe = (annualized_return - 0.03) / annualized_volatility
```

This is a simple proxy for a low-risk annual return and avoids overstating risk-adjusted performance.

## VaR and CVaR

VaR and CVaR are calculated over a 1-trading-day horizon.

The euro impact is calculated using the assessment allocation size:

```python
euro_loss = percentage_loss * 5000
```

VaR answers: “What loss threshold is exceeded only in the worst tail of the distribution?”

CVaR, also called Expected Shortfall, answers: “Once we are already in the worst tail, what is the average loss?”

## Position size

The proposed investment size is €5,000, matching the assessment brief.

## External data

External public data may be used later for benchmarks or current portfolio holdings, but it should be clearly separated from the candidate CSV-derived analysis.

## Interpretation principle

Metrics are used to support the investment recommendation, not to mechanically determine it.

The final decision should combine:

- CSV-derived quantitative evidence
- Fundamental business quality
- Portfolio fit with EDEN’s existing holdings
- EDEN rule compliance
- Downside-risk defensibility in Q&A

# Portfolio Fit Rubric Interpretation

To ensure consistency, transparency, and reproducibility, each Portfolio Fit category is evaluated using three guiding questions.

Each question receives one of the following responses:

| Response | Score |
| -------- | ----: |
| Positive |   1.0 |
| Neutral  |   0.5 |
| Negative |   0.0 |

The category score is then calculated as:

```text
Category Score = (Sum of Points / 3) × 100
```

This produces a normalized score between 0 and 100 for every category and company.

---

# 1. Sector Diversification

### Guiding Question 1

**Which sectors are already heavily represented in the portfolio?**

| Response | Interpretation                                                        |
| -------- | --------------------------------------------------------------------- |
| Positive | The company operates outside heavily represented sectors.             |
| Neutral  | The company has partial overlap with existing sectors.                |
| Negative | The company operates in a sector that is already heavily represented. |

---

### Guiding Question 2

**Which important sectors are currently underrepresented or absent?**

| Response | Interpretation                                             |
| -------- | ---------------------------------------------------------- |
| Positive | The company directly fills a missing sector exposure.      |
| Neutral  | The company partially addresses a missing sector exposure. |
| Negative | The company does not address a portfolio gap.              |

---

### Guiding Question 3

**Would adding this company improve diversification or increase concentration?**

| Response | Interpretation                                    |
| -------- | ------------------------------------------------- |
| Positive | The company improves portfolio diversification.   |
| Neutral  | The company has a limited diversification impact. |
| Negative | The company increases portfolio concentration.    |

---

# 2. Growth Profile

### Guiding Question 1

**Is the portfolio currently tilted toward growth or capital preservation?**

| Response | Interpretation                                                                |
| -------- | ----------------------------------------------------------------------------- |
| Positive | The company improves the portfolio's balance between growth and preservation. |
| Neutral  | The company has a limited effect on portfolio balance.                        |
| Negative | The company reinforces an existing imbalance.                                 |

---

### Guiding Question 2

**Does the portfolio have sufficient exposure to long-term growth opportunities?**

| Response | Interpretation                                         |
| -------- | ------------------------------------------------------ |
| Positive | The company provides strong long-term growth exposure. |
| Neutral  | The company provides moderate growth exposure.         |
| Negative | The company provides weak growth exposure.             |

---

### Guiding Question 3

**Would this company improve the portfolio's overall growth profile?**

| Response | Interpretation                                      |
| -------- | --------------------------------------------------- |
| Positive | The company significantly improves growth exposure. |
| Neutral  | The company moderately improves growth exposure.    |
| Negative | The company provides little improvement.            |

---

# 3. Geographic Diversification

### Guiding Question 1

**Which regions currently drive the portfolio's returns?**

| Response | Interpretation                                                    |
| -------- | ----------------------------------------------------------------- |
| Positive | The company introduces meaningful new geographic exposure.        |
| Neutral  | The company partially overlaps with existing geographic exposure. |
| Negative | The company remains concentrated in existing regions.             |

---

### Guiding Question 2

**Is the portfolio overly dependent on a specific region or economy?**

| Response | Interpretation                                           |
| -------- | -------------------------------------------------------- |
| Positive | The company reduces regional dependence.                 |
| Neutral  | The company has a limited impact on regional dependence. |
| Negative | The company reinforces existing regional dependence.     |

---

### Guiding Question 3

**Would this company provide meaningful geographic diversification?**

| Response | Interpretation                                            |
| -------- | --------------------------------------------------------- |
| Positive | The company provides strong geographic diversification.   |
| Neutral  | The company provides moderate geographic diversification. |
| Negative | The company provides little geographic diversification.   |

---

# 4. Structural Theme Exposure

### Guiding Question 1

**Which long-term investment themes are currently underrepresented in the portfolio?**

| Response | Interpretation                                             |
| -------- | ---------------------------------------------------------- |
| Positive | The company directly addresses an underrepresented theme.  |
| Neutral  | The company partially addresses an underrepresented theme. |
| Negative | The company provides no meaningful thematic exposure.      |

---

### Guiding Question 2

**Does this company provide meaningful exposure to those themes?**

| Response | Interpretation                                        |
| -------- | ----------------------------------------------------- |
| Positive | The theme is central to the company's business model. |
| Neutral  | The theme is a secondary component of the business.   |
| Negative | The theme has minimal relevance to the business.      |

---

### Guiding Question 3

**Would this company strengthen the portfolio's positioning for future structural trends?**

| Response | Interpretation                                                     |
| -------- | ------------------------------------------------------------------ |
| Positive | The company significantly improves long-term thematic positioning. |
| Neutral  | The company moderately improves long-term thematic positioning.    |
| Negative | The company provides little thematic benefit.                      |

---

# 5. Revenue Quality

### Guiding Question 1

**How much of the portfolio is currently exposed to predictable recurring revenue models?**

| Response | Interpretation                                                 |
| -------- | -------------------------------------------------------------- |
| Positive | The company significantly improves recurring revenue exposure. |
| Neutral  | The company moderately improves recurring revenue exposure.    |
| Negative | The company provides little recurring revenue exposure.        |

---

### Guiding Question 2

**Does this company generate stable revenues or depend primarily on one-time sales?**

| Response | Interpretation                                                    |
| -------- | ----------------------------------------------------------------- |
| Positive | The company generates highly recurring and predictable revenue.   |
| Neutral  | The company has a mixed revenue model.                            |
| Negative | The company depends primarily on transactional or one-time sales. |

---

### Guiding Question 3

**Would adding this company improve the overall quality and predictability of portfolio cash flows?**

| Response | Interpretation                                                |
| -------- | ------------------------------------------------------------- |
| Positive | The company significantly improves cash-flow quality.         |
| Neutral  | The company moderately improves cash-flow quality.            |
| Negative | The company provides little improvement in cash-flow quality. |
