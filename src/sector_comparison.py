import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy import stats


orion     = pd.read_csv("../data/orion_eod.csv",     parse_dates=["Date"], index_col="Date")
cleanergy = pd.read_csv("../data/cleanergy_eod.csv", parse_dates=["Date"], index_col="Date")
novaterra = pd.read_csv("../data/novaterra_eod.csv", parse_dates=["Date"], index_col="Date")

#Load ETFs
soxx = yf.download("SOXX", start="2019-01-01")["Close"]  # Orion benchmark
icln = yf.download("ICLN", start="2019-01-01")["Close"]  # Cleanergy benchmark 1
grid = yf.download("GRID", start="2019-01-01")["Close"]  # Cleanergy benchmark 2
moo  = yf.download("MOO",  start="2019-01-01")["Close"]  # NovaTerra benchmark

orion     = orion["2019":]
cleanergy = cleanergy["2019":]
novaterra = novaterra["2019":]

#Log returns
orion["log_return"]     = np.log(orion["Close"]     / orion["Close"].shift(1))
cleanergy["log_return"] = np.log(cleanergy["Close"] / cleanergy["Close"].shift(1))
novaterra["log_return"] = np.log(novaterra["Close"] / novaterra["Close"].shift(1))

soxx_ret = np.log(soxx / soxx.shift(1))
icln_ret = np.log(icln / icln.shift(1))
grid_ret = np.log(grid / grid.shift(1))
moo_ret  = np.log(moo  / moo.shift(1))

orion_aligned,          soxx_aligned = orion["log_return"].align(soxx_ret, join="inner")
cleanergy_aligned_icln, icln_aligned = cleanergy["log_return"].align(icln_ret, join="inner")
cleanergy_aligned_grid, grid_aligned = cleanergy["log_return"].align(grid_ret, join="inner")
novaterra_aligned,      moo_aligned  = novaterra["log_return"].align(moo_ret,  join="inner")

#Beta calculation
def calculate_beta(stock_returns, benchmark_returns):
    combined = pd.concat([stock_returns, benchmark_returns], axis=1).dropna()
    s = combined.iloc[:, 0].values
    b = combined.iloc[:, 1].values
    cov_matrix = np.cov(s, b)
    covariance = cov_matrix[0, 1]
    variance   = cov_matrix[1, 1]
    return covariance / variance

beta_orion          = calculate_beta(orion_aligned,          soxx_aligned)
beta_cleanergy_icln = calculate_beta(cleanergy_aligned_icln, icln_aligned)
beta_cleanergy_grid = calculate_beta(cleanergy_aligned_grid, grid_aligned)
beta_novaterra      = calculate_beta(novaterra_aligned,      moo_aligned)

#Correlation calculation 
def calculate_corr(stock_returns, benchmark_returns):
    combined = pd.concat([stock_returns, benchmark_returns], axis=1).dropna()
    return combined.iloc[:, 0].corr(combined.iloc[:, 1])

corr_orion          = calculate_corr(orion_aligned,          soxx_aligned)
corr_cleanergy_icln = calculate_corr(cleanergy_aligned_icln, icln_aligned)
corr_cleanergy_grid = calculate_corr(cleanergy_aligned_grid, grid_aligned)
corr_novaterra      = calculate_corr(novaterra_aligned,      moo_aligned)

print("=" * 55)
print(f"{'Company':<20} {'Beta':>10} {'Correlation':>15}")
print("=" * 55)
print(f"{'Orion vs SOXX':<20} {beta_orion:>10.3f} {corr_orion:>15.3f}")
print(f"{'Cleanergy vs ICLN':<20} {beta_cleanergy_icln:>10.3f} {corr_cleanergy_icln:>15.3f}")
print(f"{'Cleanergy vs GRID':<20} {beta_cleanergy_grid:>10.3f} {corr_cleanergy_grid:>15.3f}")
print(f"{'NovaTerra vs MOO':<20} {beta_novaterra:>10.3f} {corr_novaterra:>15.3f}")
print("=" * 55)

#Plot. We normalise to 100 in order to offer side-by-side comparison
pairs = [
    ("Orion",             orion["Close"],     soxx, "SOXX"),
    ("Cleanergy vs ICLN", cleanergy["Close"], icln, "ICLN"),
    ("Cleanergy vs GRID", cleanergy["Close"], grid, "GRID"),
    ("NovaTerra",         novaterra["Close"], moo,  "MOO"),
]
fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
fig.suptitle("Stock vs Sector ETF — Normalised Performance (Base 100, 2019)", fontsize=14)

# Orion vs SOXX
stock_norm = (orion["Close"] / orion["Close"].iloc[0]) * 100
etf_norm   = (soxx / soxx.iloc[0]) * 100
axes[0].plot(stock_norm.index, stock_norm, label="Orion")
axes[0].plot(etf_norm.index,   etf_norm,   label="SOXX", linestyle="--")
axes[0].set_title("Orion vs SOXX", fontsize=11)
axes[0].set_ylabel("Normalised Price (Base 100)")
axes[0].legend(loc="upper left")
axes[0].grid(axis="y", linewidth=0.4, alpha=0.5)

# Cleanergy vs ICLN and GRID
stock_norm  = (cleanergy["Close"] / cleanergy["Close"].iloc[0]) * 100
icln_norm   = (icln / icln.iloc[0]) * 100
grid_norm   = (grid / grid.iloc[0]) * 100
axes[1].plot(stock_norm.index, stock_norm, label="Cleanergy")
axes[1].plot(icln_norm.index,  icln_norm,  label="ICLN", linestyle="--")
axes[1].plot(grid_norm.index,  grid_norm,  label="GRID", linestyle=":")
axes[1].set_title("Cleanergy vs ICLN and GRID", fontsize=11)
axes[1].set_ylabel("Normalised Price (Base 100)")
axes[1].legend(loc="upper left")
axes[1].grid(axis="y", linewidth=0.4, alpha=0.5)

# NovaTerra vs MOO
stock_norm = (novaterra["Close"] / novaterra["Close"].iloc[0]) * 100
etf_norm   = (moo / moo.iloc[0]) * 100
axes[2].plot(stock_norm.index, stock_norm, label="NovaTerra")
axes[2].plot(etf_norm.index,   etf_norm,   label="MOO", linestyle="--")
axes[2].set_title("NovaTerra vs MOO", fontsize=11)
axes[2].set_ylabel("Normalised Price (Base 100)")
axes[2].legend(loc="upper left")
axes[2].grid(axis="y", linewidth=0.4, alpha=0.5)

axes[-1].set_xlabel("Date")
plt.tight_layout()
plt.show()
axes[-1].set_xlabel("Date")
plt.tight_layout()
plt.show()