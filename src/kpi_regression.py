import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ── LOAD COMPANIES ────────────────────────────────────────────────────────────
orion     = pd.read_csv("../data/orion_eod.csv",     parse_dates=["Date"], index_col="Date")
cleanergy = pd.read_csv("../data/cleanergy_eod.csv", parse_dates=["Date"], index_col="Date")
novaterra = pd.read_csv("../data/novaterra_eod.csv", parse_dates=["Date"], index_col="Date")

# ── ANNUAL AVERAGE PRICE — aggregate daily prices to yearly ───────────────────
orion_annual     = orion["Close"].resample("YE").mean()
cleanergy_annual = cleanergy["Close"].resample("YE").mean()
novaterra_annual = novaterra["Close"].resample("YE").mean()

# Filter to 2022-2025 to match KPI data
orion_P     = orion_annual["2022":"2025"].values
cleanergy_P = cleanergy_annual["2022":"2025"].values
novaterra_P = novaterra_annual["2022":"2025"].values

years = [2022, 2023, 2024, 2025]

# ── KPI MATRICES ──────────────────────────────────────────────────────────────
# Orion: Average Selling Price, Gross Margin, Software Revenue %
X_orion = np.array([
    [1, 38.4, 0.61, 0.11],
    [1, 35.1, 0.58, 0.16],
    [1, 31.6, 0.54, 0.21],
    [1, 28.9, 0.51, 0.27],
])

# Cleanergy: ARR, Gross Margin, Software Subscription Revenue %
X_cleanergy = np.array([
    [1,  52, 0.38, 0.18],
    [1,  89, 0.41, 0.24],
    [1, 148, 0.44, 0.31],
    [1, 241, 0.47, 0.39],
])

# NovaTerra: Revenue per Acre, AI Prediction Accuracy, Subscription Revenue %
X_novaterra = np.array([
    [1, 5.2, 0.81, 0.48],
    [1, 4.8, 0.84, 0.57],
    [1, 4.5, 0.88, 0.63],
    [1, 4.6, 0.91, 0.69],
])

# ── OLS REGRESSION — beta = (X'X)^-1 X'Y ────────────────────────────────────
def ols_regression(X, Y):
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    Y_hat = X @ beta
    ss_res = np.sum((Y - Y_hat) ** 2)
    ss_tot = np.sum((Y - np.mean(Y)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    return beta, Y_hat, r2

beta_orion,     yhat_orion,     r2_orion     = ols_regression(X_orion,     orion_P)
beta_cleanergy, yhat_cleanergy, r2_cleanergy = ols_regression(X_cleanergy, cleanergy_P)
beta_novaterra, yhat_novaterra, r2_novaterra = ols_regression(X_novaterra, novaterra_P)

# ── PRINT RESULTS ─────────────────────────────────────────────────────────────
def print_results(name, beta, r2, kpi_names):
    print(f"\n{'=' * 50}")
    print(f"{name} — OLS Regression Results")
    print(f"{'=' * 50}")
    print(f"  Intercept:  {beta[0]:>10.3f}")
    for i, kpi in enumerate(kpi_names):
        print(f"  {kpi:<25} {beta[i+1]:>10.3f}")
    print(f"  R²:         {r2:>10.3f}")

print_results("Orion",
              beta_orion, r2_orion,
              ["Avg Selling Price", "Gross Margin", "Software Revenue %"])

print_results("Cleanergy",
              beta_cleanergy, r2_cleanergy,
              ["ARR ($M)", "Gross Margin", "Software Subs Revenue %"])

print_results("NovaTerra",
              beta_novaterra, r2_novaterra,
              ["Revenue per Acre", "AI Prediction Accuracy", "Subscription Revenue %"])

# ── PLOT — ACTUAL vs FITTED PRICES ───────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle("KPI Regression — Actual vs Fitted Annual Price", fontsize=14)

companies = [
    ("Orion",     orion_P,     yhat_orion,     r2_orion),
    ("Cleanergy", cleanergy_P, yhat_cleanergy, r2_cleanergy),
    ("NovaTerra", novaterra_P, yhat_novaterra, r2_novaterra),
]

for ax, (name, actual, fitted, r2) in zip(axes, companies):
    ax.plot(years, actual, marker="o", label="Actual Price")
    ax.plot(years, fitted, marker="x", linestyle="--", label="Fitted Price")
    ax.set_title(f"{name}  —  R² = {r2:.3f}", fontsize=11)
    ax.set_ylabel("Average Annual Price")
    ax.set_xlabel("Year")
    ax.legend(loc="upper left")
    ax.grid(axis="y", linewidth=0.4, alpha=0.5)

plt.tight_layout()
plt.show()