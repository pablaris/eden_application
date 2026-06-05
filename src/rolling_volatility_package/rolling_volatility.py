import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy import stats

# ============================================================
# Rolling Volatility Analysis
# ============================================================
#
# Objective:
# Measure how realized volatility evolves through time for each
# candidate company under different rolling windows.
#
# This is useful for identifying:
#   - regime shifts
#   - volatility clustering
#   - periods of elevated tail risk
#   - how each name behaves around major macro events
#
# The analysis uses annualized rolling volatility computed from
# daily log returns.
# ============================================================

# ============================================================
# Load data
# ============================================================
#
# Read the simulated end-of-day price series for each fictional
# company.
#
# The Date column is parsed as a datetime index so that time-
# series operations such as rolling windows and regime filtering
# can be applied directly.
# ============================================================

orion = pd.read_csv(
    "../data/orion_eod.csv",
    parse_dates=["Date"],
    index_col="Date"
)

cleanergy = pd.read_csv(
    "../data/cleanergy_eod.csv",
    parse_dates=["Date"],
    index_col="Date"
)

novaterra = pd.read_csv(
    "../data/novaterra_eod.csv",
    parse_dates=["Date"],
    index_col="Date"
)

# ============================================================
# Compute daily log returns
# ============================================================
#
# Log returns are used because they are additive over time and
# are standard in volatility and distribution analysis.
#
# r_t = ln(P_t / P_{t-1})
# ============================================================

orion["log_return"] = np.log(orion["Close"] / orion["Close"].shift(1))
cleanergy["log_return"] = np.log(cleanergy["Close"] / cleanergy["Close"].shift(1))
novaterra["log_return"] = np.log(novaterra["Close"] / novaterra["Close"].shift(1))

# ============================================================
# Rolling volatility estimation
# ============================================================
#
# Compute rolling annualized volatility over multiple horizons:
#   - 30 trading days
#   - 90 trading days
#   - 252 trading days
#
# The rolling standard deviation of daily log returns is scaled
# by sqrt(252) to annualize the result.
# ============================================================

windows = [30, 90, 252]

for w in windows:
    orion[f"vol_{w}d"] = orion["log_return"].rolling(w).std() * np.sqrt(252)
    cleanergy[f"vol_{w}d"] = cleanergy["log_return"].rolling(w).std() * np.sqrt(252)
    novaterra[f"vol_{w}d"] = novaterra["log_return"].rolling(w).std() * np.sqrt(252)

# Convenience list used in the plotting and summary loops.
datos = [("Orion", orion), ("Cleanergy", cleanergy), ("NovaTerra", novaterra)]

# ============================================================
# Important macro events
# ============================================================
#
# These vertical markers are used in the plots to visually
# compare volatility behavior against major macro regimes.
#
# The dates are approximate and are used only as reference
# points for visual interpretation.
# ============================================================

events = {
    "COVID Crash":       "2020-03-01",
    "Fed Hikes Begin":   "2022-03-01",
    "AI Boom (ChatGPT)": "2022-11-30",
    "AI Capex Surge":    "2024-01-01",
}

# ============================================================
# Regime summary table
# ============================================================
#
# Split the sample into broad market regimes so that volatility
# can be summarized across structurally different periods.
#
# Pre-COVID:
#   Stable pre-pandemic market regime
#
# COVID+Hikes:
#   Pandemic shock plus tightening cycle
#
# AI Boom:
#   Period when AI-related market enthusiasm accelerates
# ============================================================

regimes = {
    "Pre-COVID":   (None,         "2020-02-28"),
    "COVID+Hikes": ("2020-03-01", "2022-11-29"),
    "AI Boom":     ("2022-11-30", None),
}

# ============================================================
# Regime summary output
# ============================================================
#
# For each regime and company, report:
#   - mean volatility
#   - maximum volatility
#   - minimum volatility
#
# This gives a compact view of how unstable each stock was
# under different macro environments.
# ============================================================

print("\n" + "=" * 75)
print(f"{'Regime':<20} {'Company':<12} {'Mean Vol':>10} {'Max Vol':>10} {'Min Vol':>10}")
print("=" * 75)

for regime_name, (start, end) in regimes.items():
    for name, df in datos:
        # Use the 90-day rolling volatility series as the main
        # medium-term risk proxy for regime comparison.
        vol = df["vol_90d"].copy()

        # Restrict the sample to the regime window.
        if start:
            vol = vol[vol.index >= start]
        if end:
            vol = vol[vol.index <= end]

        # Remove missing values introduced by the rolling window.
        vol = vol.dropna()

        # Skip regimes with no valid observations.
        if len(vol) == 0:
            continue

        print(
            f"{regime_name:<20} {name:<12} "
            f"{vol.mean():>10.1%} {vol.max():>10.1%} {vol.min():>10.1%}"
        )

print("=" * 75)

# ============================================================
# Plot A: 90-day rolling volatility across all companies
# ============================================================
#
# This plot compares the medium-term volatility profile of all
# three candidates on the same horizon.
#
# The 90-day window is a good compromise between:
#   - responsiveness to regime changes
#   - smoothing of short-term noise
# ============================================================

fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
fig.suptitle("Rolling 90-Day Annualised Volatility — All Candidates", fontsize=14)

for ax, (name, df) in zip(axes, datos):
    ax.plot(df.index, df["vol_90d"], label="90d Annualised Volatility")

    # Overlay macro-event markers to visually relate volatility
    # spikes to market-wide shocks or narrative shifts.
    for label, date in events.items():
        d = pd.Timestamp(date)
        if d >= df.index[0]:
            ax.axvline(d, color="grey", linewidth=0.8, linestyle="--", alpha=0.7)
            ax.text(
                d,
                ax.get_ylim()[1],
                label,
                fontsize=7,
                rotation=90,
                va="top",
                ha="right",
                color="grey"
            )

    ax.set_title(name, fontsize=11)
    ax.set_ylabel("Ann. Volatility")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    ax.legend(loc="upper left")
    ax.grid(axis="y", linewidth=0.4, alpha=0.5)

axes[-1].set_xlabel("Date")
plt.tight_layout()
plt.show()

# ============================================================
# Plot B: Each company across multiple volatility windows
# ============================================================
#
# This set of plots compares short-, medium-, and long-horizon
# realized volatility for each candidate.
#
# Interpretation:
#   - 30d window reacts quickly to shocks
#   - 90d window shows medium-term regime changes
#   - 252d window gives a long-run volatility anchor
# ============================================================

for name, df in datos:
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle(f"{name} — Rolling Volatility: 30d / 90d / 252d", fontsize=14)

    for ax, w in zip(axes, windows):
        ax.plot(
            df.index,
            df[f"vol_{w}d"],
            label=f"{w}-day Rolling Annualised Volatility"
        )

        # Add the same macro-event markers to each window so the
        # volatility response can be compared across horizons.
        for label, date in events.items():
            d = pd.Timestamp(date)
            if d >= df.index[0]:
                ax.axvline(d, color="grey", linewidth=0.8, linestyle="--", alpha=0.7)
                ax.text(
                    d,
                    ax.get_ylim()[1],
                    label,
                    fontsize=7,
                    rotation=90,
                    va="top",
                    ha="right",
                    color="grey"
                )

        ax.set_title(f"{w}-Day Window", fontsize=10)
        ax.set_ylabel("Ann. Volatility")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
        ax.legend(loc="upper left")
        ax.grid(axis="y", linewidth=0.4, alpha=0.5)

    axes[-1].set_xlabel("Date")
    plt.tight_layout()
    plt.show()