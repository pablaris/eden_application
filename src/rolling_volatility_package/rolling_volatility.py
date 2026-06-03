import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy import stats

#Load Data 
orion     = pd.read_csv("../data/orion_eod.csv",     parse_dates=["Date"], index_col="Date")
cleanergy = pd.read_csv("../data/cleanergy_eod.csv", parse_dates=["Date"], index_col="Date")
novaterra = pd.read_csv("../data/novaterra_eod.csv", parse_dates=["Date"], index_col="Date")

#Log returns
orion["log_return"]     = np.log(orion["Close"]     / orion["Close"].shift(1))
cleanergy["log_return"] = np.log(cleanergy["Close"] / cleanergy["Close"].shift(1))
novaterra["log_return"] = np.log(novaterra["Close"] / novaterra["Close"].shift(1))

#Rolling Volatilit
windows = [30, 90, 252]

for w in windows:
    orion[f"vol_{w}d"]     = orion["log_return"].rolling(w).std()     * np.sqrt(252)
    cleanergy[f"vol_{w}d"] = cleanergy["log_return"].rolling(w).std() * np.sqrt(252)
    novaterra[f"vol_{w}d"] = novaterra["log_return"].rolling(w).std() * np.sqrt(252)

datos = [("Orion", orion), ("Cleanergy", cleanergy), ("NovaTerra", novaterra)]

#Important Macro Events
events = {
    "COVID Crash":        "2020-03-01",
    "Fed Hikes Begin":    "2022-03-01",
    "AI Boom (ChatGPT)":  "2022-11-30",
    "AI Capex Surge":     "2024-01-01",
}

#Summary table
regimes = {
    "Pre-COVID":   (None,         "2020-02-28"),
    "COVID+Hikes": ("2020-03-01", "2022-11-29"),
    "AI Boom":     ("2022-11-30", None        ),
}

print("\n" + "=" * 75)
print(f"{'Regime':<20} {'Company':<12} {'Mean Vol':>10} {'Max Vol':>10} {'Min Vol':>10}")
print("=" * 75)

for regime_name, (start, end) in regimes.items():
    for name, df in datos:
        # filter to regime dates
        vol = df["vol_90d"].copy()
        if start:
            vol = vol[vol.index >= start]
        if end:
            vol = vol[vol.index <= end]
        vol = vol.dropna()

        if len(vol) == 0:
            continue

        print(f"{regime_name:<20} {name:<12} {vol.mean():>10.1%} {vol.max():>10.1%} {vol.min():>10.1%}")

print("=" * 75)


#Plot A: All three candidates - 90 days window
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
fig.suptitle("Rolling 90-Day Annualised Volatility — All Candidates", fontsize=14)

for ax, (name, df) in zip(axes, datos):
    ax.plot(df.index, df["vol_90d"], label="90d Annualised Volatility")

    # macro event markers
    for label, date in events.items():
        d = pd.Timestamp(date)
        if d >= df.index[0]:
            ax.axvline(d, color="grey", linewidth=0.8, linestyle="--", alpha=0.7)
            ax.text(d, ax.get_ylim()[1], label, fontsize=7,
                    rotation=90, va="top", ha="right", color="grey")

    ax.set_title(name, fontsize=11)
    ax.set_ylabel("Ann. Volatility")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    ax.legend(loc="upper left")
    ax.grid(axis="y", linewidth=0.4, alpha=0.5)

axes[-1].set_xlabel("Date")
plt.tight_layout()
plt.show()

#Plot B: Each candidate, every window
for name, df in datos:
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle(f"{name} — Rolling Volatility: 30d / 90d / 252d", fontsize=14)

    for ax, w in zip(axes, windows):
        ax.plot(df.index, df[f"vol_{w}d"],
                label=f"{w}-day Rolling Annualised Volatility")

        # macro event markers
        for label, date in events.items():
            d = pd.Timestamp(date)
            if d >= df.index[0]:
                ax.axvline(d, color="grey", linewidth=0.8, linestyle="--", alpha=0.7)
                ax.text(d, ax.get_ylim()[1], label, fontsize=7,
                        rotation=90, va="top", ha="right", color="grey")

        ax.set_title(f"{w}-Day Window", fontsize=10)
        ax.set_ylabel("Ann. Volatility")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
        ax.legend(loc="upper left")
        ax.grid(axis="y", linewidth=0.4, alpha=0.5)

    axes[-1].set_xlabel("Date")
    plt.tight_layout()
    plt.show()


