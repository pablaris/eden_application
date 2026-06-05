import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ============================================================
# KPI Regression Analysis
# ============================================================
#
# Objective:
# Examine whether changes in each company's annual share price
# can be broadly explained by its operating fundamentals.
#
# This script is not intended to produce a rigorous statistical
# inference model. With only 4 annual observations per company,
# the regression is effectively saturated (intercept + 3 KPIs),
# so the output should be interpreted as a descriptive
# validation tool rather than a robust econometric result.
#
# The purpose is to help assess whether price behavior appears
# supported by fundamentals or whether it may be driven more by
# narrative, sentiment, or speculation.
# ============================================================

# ============================================================
# Load daily price data
# ============================================================
#
# Each company is loaded from its simulated end-of-day file.
# The Date column is parsed as a datetime index so that the
# series can be resampled to annual frequency.
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
# Convert daily prices into annual average prices
# ============================================================
#
# We use annual average closing prices rather than year-end
# closes to reduce noise from short-term market fluctuations.
#
# This produces one annual price observation per year, which
# can then be aligned with the annual KPI values from the case
# materials.
# ============================================================

orion_annual = orion["Close"].resample("YE").mean()
cleanergy_annual = cleanergy["Close"].resample("YE").mean()
novaterra_annual = novaterra["Close"].resample("YE").mean()

# Restrict the sample to 2022-2025 so that the price series
# aligns with the KPI observations in the assessment brief.
orion_P = orion_annual["2022":"2025"].values
cleanergy_P = cleanergy_annual["2022":"2025"].values
novaterra_P = novaterra_annual["2022":"2025"].values

years = [2022, 2023, 2024, 2025]

# ============================================================
# KPI design matrices
# ============================================================
#
# Each regression uses:
#
#   Y = annual average price
#   X = [intercept, operating KPI 1, operating KPI 2, operating KPI 3]
#
# The first column is a constant term (intercept).
#
# Orion:
#   - Average Selling Price
#   - Gross Margin
#   - Software Revenue %
#
# Cleanergy:
#   - ARR
#   - Gross Margin
#   - Software Subscription Revenue %
#
# NovaTerra:
#   - Revenue per Acre
#   - AI Prediction Accuracy
#   - Subscription Revenue %
#
# These KPIs are chosen because they are the most direct
# operating signals available in the case materials.
# ============================================================

X_orion = np.array([
    [1, 38.4, 0.61, 0.11],
    [1, 35.1, 0.58, 0.16],
    [1, 31.6, 0.54, 0.21],
    [1, 28.9, 0.51, 0.27],
])

X_cleanergy = np.array([
    [1,  52, 0.38, 0.18],
    [1,  89, 0.41, 0.24],
    [1, 148, 0.44, 0.31],
    [1, 241, 0.47, 0.39],
])

X_novaterra = np.array([
    [1, 5.2, 0.81, 0.48],
    [1, 4.8, 0.84, 0.57],
    [1, 4.5, 0.88, 0.63],
    [1, 4.6, 0.91, 0.69],
])

# ============================================================
# Ordinary Least Squares regression
# ============================================================
#
# We estimate:
#
#   beta = (X'X)^(-1) X'Y
#
# using numpy's least-squares solver.
#
# The function returns:
#   - beta: regression coefficients
#   - Y_hat: fitted values
#   - r2: coefficient of determination
#
# Note:
# With 4 observations and 4 parameters, the regression is
# saturated. That means the fitted line may pass very closely
# through the observed points, so the R² should not be treated
# as evidence of causal explanation.
# ============================================================

def ols_regression(X, Y):
    """
    Fit an OLS regression model and compute fitted values and R².

    Parameters
    ----------
    X : np.ndarray
        Design matrix including intercept.
    Y : np.ndarray
        Dependent variable, here annual average share price.

    Returns
    -------
    beta : np.ndarray
        Estimated regression coefficients.
    Y_hat : np.ndarray
        Fitted values from the regression.
    r2 : float
        Coefficient of determination.
    """
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    Y_hat = X @ beta

    # Residual sum of squares
    ss_res = np.sum((Y - Y_hat) ** 2)

    # Total sum of squares
    ss_tot = np.sum((Y - np.mean(Y)) ** 2)

    # R², guarding against division by zero
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    return beta, Y_hat, r2


beta_orion, yhat_orion, r2_orion = ols_regression(X_orion, orion_P)
beta_cleanergy, yhat_cleanergy, r2_cleanergy = ols_regression(X_cleanergy, cleanergy_P)
beta_novaterra, yhat_novaterra, r2_novaterra = ols_regression(X_novaterra, novaterra_P)

# ============================================================
# Results printing helper
# ============================================================
#
# Print regression coefficients in a structured and readable
# format so the output can be used directly in analysis notes
# or presentation preparation.
# ============================================================

def print_results(name, beta, r2, kpi_names):
    print(f"\n{'=' * 50}")
    print(f"{name} — OLS Regression Results")
    print(f"{'=' * 50}")
    print(f"  Intercept:  {beta[0]:>10.3f}")
    for i, kpi in enumerate(kpi_names):
        print(f"  {kpi:<25} {beta[i + 1]:>10.3f}")
    print(f"  R²:         {r2:>10.3f}")


print_results(
    "Orion",
    beta_orion,
    r2_orion,
    ["Avg Selling Price", "Gross Margin", "Software Revenue %"]
)

print_results(
    "Cleanergy",
    beta_cleanergy,
    r2_cleanergy,
    ["ARR ($M)", "Gross Margin", "Software Subs Revenue %"]
)

print_results(
    "NovaTerra",
    beta_novaterra,
    r2_novaterra,
    ["Revenue per Acre", "AI Prediction Accuracy", "Subscription Revenue %"]
)

# ============================================================
# Plot actual vs fitted prices
# ============================================================
#
# This visualization helps assess whether the fitted values
# track the observed price trend over time.
#
# If the fitted line closely matches the actual prices, the
# KPI set is at least directionally consistent with price
# evolution.
#
# Because the sample is extremely small, this should be read as
# a visual plausibility check rather than formal validation.
# ============================================================

fig, axes = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle("KPI Regression — Actual vs Fitted Annual Price", fontsize=14)

companies = [
    ("Orion", orion_P, yhat_orion, r2_orion),
    ("Cleanergy", cleanergy_P, yhat_cleanergy, r2_cleanergy),
    ("NovaTerra", novaterra_P, yhat_novaterra, r2_novaterra),
]

for ax, (name, actual, fitted, r2) in zip(axes, companies):
    ax.plot(years, actual, marker="o", label="Actual Price")
    ax.plot(years, fitted, marker="x", linestyle="--", label="Fitted Price")
    ax.set_title(f"{name} — R² = {r2:.3f}", fontsize=11)
    ax.set_ylabel("Average Annual Price")
    ax.set_xlabel("Year")
    ax.legend(loc="upper left")
    ax.grid(axis="y", linewidth=0.4, alpha=0.5)

plt.tight_layout()
plt.show()