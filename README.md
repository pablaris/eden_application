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
