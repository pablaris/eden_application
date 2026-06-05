# ============================================================
# Empirical Distribution vs. Normal Distribution
# Fat tails, skewness, and kurtosis
# ============================================================
#
# This script compares the empirical distribution of returns
# for the S&P 500 against a theoretical normal distribution.
#
# The objective is to assess whether returns exhibit:
#   - skewness
#   - fat tails
#   - excess kurtosis
#
# These diagnostics are useful for risk analysis because
# financial returns are often not normally distributed.
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import yfinance as yf

# ============================================================
# Data download
# ============================================================
#
# Download 11 years of daily S&P 500 data from Yahoo Finance.
# The closing price series is used as the basis for return
# calculations.
# ============================================================

sp500 = yf.download("^GSPC", period="11y", interval="1d")
prices = sp500["Close"].squeeze()

# ============================================================
# Return calculation
# ============================================================
#
# Compute daily log returns:
#
#   r_t = ln(P_t) - ln(P_{t-1})
#
# Log returns are preferred here because they are time-additive
# and commonly used in distribution and tail-risk analysis.
# ============================================================

log_returns = np.log(prices).diff()
log_returns = log_returns.dropna()

# ============================================================
# Descriptive statistics
# ============================================================
#
# Mean:
#   Average daily log return
#
# Standard deviation:
#   Dispersion of returns around the mean
#
# Skewness:
#   Measures asymmetry of the return distribution
#
# Kurtosis:
#   Measures tail thickness relative to the normal distribution
# ============================================================

mu = np.mean(log_returns)
sigma = np.std(log_returns)
skew = stats.skew(log_returns)
kurt = stats.kurtosis(log_returns)

# ============================================================
# Print summary statistics
# ============================================================
#
# These values provide a quick numerical summary of the
# empirical return distribution before visual inspection.
# ============================================================

print("=" * 40)
print("ESTADÍSTICOS DESCRIPTIVOS — S&P 500")
print("=" * 40)
print(f"Mu: {mu}")
print(f"Standard Deviation: {sigma}")
print(f"Skewness: {skew}")
print(f"Kurt: {kurt}")

# ============================================================
# Visual comparison: empirical distribution vs. normal
# ============================================================
#
# The left panel shows the histogram of observed log returns
# overlaid with a theoretical normal density using the same
# mean and standard deviation.
#
# The right panel shows a QQ plot to compare empirical quantiles
# with theoretical normal quantiles.
#
# If the return distribution were normal, the histogram would
# align closely with the red curve and the QQ plot would lie
# near the straight reference line.
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram of empirical returns
axes[0].hist(
    log_returns,
    bins=50,
    density=True,
    alpha=0.6,
    color="blue",
    label="Datos Reales"
)

# Theoretical normal density with identical mean and standard deviation
x = np.linspace(min(log_returns), max(log_returns), 100)
y = stats.norm.pdf(x, mu, sigma)

axes[0].plot(
    x,
    y,
    color="red",
    linewidth=2,
    label="Curva Normal Teórica"
)

axes[0].set_title("Distribución de rendimientos logarítmicos")
axes[0].set_xlabel("Rendimiento Logarítmico")
axes[0].set_ylabel("Densidad")
axes[0].legend()

# QQ plot against the normal distribution
stats.probplot(log_returns, dist="norm", plot=axes[1])
axes[1].set_title("QQ Plot de Rendimientos logarítmicos")
axes[1].set_xlabel("Cuantiles Teóricos (Distribución Normal)")
axes[1].set_ylabel("Cuantiles de los Datos Reales")

# Adjust layout to avoid overlap between subplots
plt.tight_layout()
plt.show()