# ============================================================
# Value at Risk (VaR) and Conditional VaR (CVaR) Analysis
# ============================================================
#
# Objective:
# Estimate downside risk for the S&P 500 using historical and
# parametric methods.
#
# The script computes:
#   - Historical VaR at the 95% and 99% levels
#   - Parametric VaR at the 95% and 99% levels
#   - CVaR (Expected Shortfall) at the 95% level
#
# These measures are useful for quantifying tail risk and
# understanding how severe losses may be under adverse market
# conditions.
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import yfinance as yf

# ============================================================
# Load benchmark market data
# ============================================================
#
# Download 11 years of daily S&P 500 closing prices.
# The S&P 500 is used here as a broad market reference series
# for tail-risk estimation.
# ============================================================

sp500 = yf.download("^GSPC", period="11y", interval="1d")
prices = sp500["Close"].squeeze()

# ============================================================
# Compute log returns
# ============================================================
#
# Log returns are used because they are standard in risk and
# distribution analysis and are additive over time.
#
# r_t = ln(P_t / P_{t-1})
# ============================================================

log_returns = np.diff(np.log(prices))

# ============================================================
# Estimate distribution parameters
# ============================================================
#
# mu:
#   Mean daily log return
#
# sd:
#   Standard deviation of daily log returns
#
# These parameters are used in the parametric VaR calculation.
# ============================================================

mu = np.mean(log_returns)
sd = np.std(log_returns)

# ============================================================
# Historical VaR
# ============================================================
#
# Historical VaR is a non-parametric estimate based directly on
# the empirical return distribution.
#
# 95% VaR:
#   5th percentile of returns
#
# 99% VaR:
#   1st percentile of returns
#
# The negative sign converts return quantiles into loss values.
# ============================================================

VaR_hist_95 = -np.percentile(log_returns, 5)
VaR_hist_99 = -np.percentile(log_returns, 1)

# ============================================================
# Parametric VaR
# ============================================================
#
# Parametric VaR assumes returns are approximately normally
# distributed.
#
# Formula:
#
#   VaR = -(mu + z_alpha * sd)
#
# where z_alpha is the relevant normal quantile.
# ============================================================

VaR_param_95 = -(mu + stats.norm.ppf(0.05) * sd)
VaR_param_99 = -(mu + stats.norm.ppf(0.01) * sd)

# ============================================================
# CVaR (Expected Shortfall)
# ============================================================
#
# CVaR measures the average loss conditional on being in the
# worst tail of the distribution.
#
# It is more conservative than VaR because it looks beyond the
# threshold and captures the magnitude of extreme losses.
# ============================================================

filtro = np.percentile(log_returns, 5)
CVaR_95 = -np.mean(log_returns[log_returns <= filtro])

# ============================================================
# Euro impact
# ============================================================
#
# Convert percentage losses into euro losses using the assumed
# investment size.
#
# Note:
# If you want to align this with the EDEN assumptions file,
# use €5,000 rather than €10,000. :contentReference[oaicite:0]{index=0}
# ============================================================

inversion = 10_000

informacion = {
    "Histórico": {
        "95%": {"VaR": VaR_hist_95, "Perdida": VaR_hist_95 * inversion},
        "99%": {"VaR": VaR_hist_99, "Perdida": VaR_hist_99 * inversion},
    },
    "Paramétrico": {
        "95%": {"VaR": VaR_param_95, "Perdida": VaR_param_95 * inversion},
        "99%": {"VaR": VaR_param_99, "Perdida": VaR_param_99 * inversion},
    },
    "CVaR": {
        "95%": {"VaR": CVaR_95, "Perdida": CVaR_95 * inversion},
    },
}

# ============================================================
# Visualisation
# ============================================================
#
# Plot the empirical distribution of log returns and overlay:
#   - Historical VaR
#   - Parametric VaR
#   - CVaR
#
# The shaded area highlights the left tail of the return
# distribution.
# ============================================================

plt.hist(log_returns, bins=50, alpha=0.6, color="black", density=True)
plt.axvline(
    x=-VaR_hist_95,
    color="blue",
    linestyle="--",
    label="VaR histórico al 95%"
)
plt.axvline(
    x=-VaR_param_95,
    color="red",
    linestyle="--",
    label="VaR paramétrico al 95%"
)
plt.axvline(
    x=-CVaR_95,
    color="orange",
    linestyle="--",
    label="CVaR al 95%"
)
plt.axvspan(
    xmin=log_returns.min(),
    xmax=-VaR_hist_95,
    alpha=0.3,
    color="grey",
    label="Zona sombreada en el 5% izquierdo"
)

plt.legend()
plt.xlabel("Rendimiento logarítmico")
plt.ylabel("Densidad")
plt.title(
    "Histograma de retornos logarítmicos sobre el S&P 500 "
    "con VaR histórico, VaR paramétrico y CVaR"
)
plt.show()

# ============================================================
# Print results
# ============================================================
#
# Display the estimated risk measures and their euro-equivalent
# losses in a readable table format.
# ============================================================

for metodo, niveles in informacion.items():
    for nivel, valores in niveles.items():
        print(
            f"{metodo} | {nivel} | "
            f"VaR: {valores['VaR']:.4f} | "
            f"Pérdida: {valores['Perdida']:.2f}€"
        )