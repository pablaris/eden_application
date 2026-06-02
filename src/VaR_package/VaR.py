#Value at Risk (VaR) y CVaR

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import yfinance as yf

sp500 = yf.download('^GSPC', period='11y', interval='1d')
prices = sp500["Close"].squeeze()
log_returns = np.diff(np.log(prices))

mu = np.mean(log_returns)
sd = np.std(log_returns)
# VaR Histórico

VaR_hist_95 = -np.percentile(log_returns, 5)  # TU CÓDIGO AQUÍ
VaR_hist_99 = -np.percentile(log_returns, 1)   # TU CÓDIGO AQUÍ

# VaR Paramétrico
VaR_param_95 = -(mu + stats.norm.ppf(0.05)*sd)  # TU CÓDIGO AQUÍ
VaR_param_99 = -(mu + stats.norm.ppf(0.01)*sd)  # TU CÓDIGO AQUÍ

# CVaR (Expected Shortfall)


filtro = np.percentile(log_returns, 5)
CVaR_95 = -np.mean(log_returns[log_returns <= filtro]) # TU CÓDIGO AQUÍ

# Comparación e impacto en euros

inversion = 10_000

informacion = {
    "Histórico": {
        "95%": {"VaR": VaR_hist_95, "Perdida": VaR_hist_95*inversion},
        "99%": {"VaR": VaR_hist_99, "Perdida": VaR_hist_99*inversion}
    },
    "Paramétrico": {
        "95%": {"VaR": VaR_param_95, "Perdida": VaR_param_95*inversion},
        "99%": {"VaR": VaR_param_99, "Perdida": VaR_param_99*inversion}
    },
    "CVaR": {
        "95%": {"VaR": CVaR_95, "Perdida": CVaR_95*inversion}
    }
}

#  Visualización

plt.hist(log_returns, bins = 50, alpha = 0.6, color = "black", density=True)
plt.axvline(x = -VaR_hist_95, color = "blue", linestyle = "--", label = "VaR histórico al 95%")
plt.axvline(x = -VaR_param_95, color = "red", linestyle = "--", label = "VaR paramétrico al 95%")
plt.axvline(x = -CVaR_95, color = "orange", linestyle = "--", label = "CVaR al 95%")
plt.axvspan(xmin = log_returns.min(), xmax=-VaR_hist_95, alpha = 0.3, color = "grey", label = "Zona sombreada en el 5% izquierdo")

plt.legend()
plt.xlabel("Rendimiento logarítmico")
plt.ylabel("Densidad")
plt.title("Histograma de retornos logarítmicos sobre el S&P 500 desde el 2015 con VaR paramétricos e históricos, CVaR incluido")
plt.show()

for metodo, niveles in informacion.items():
    for nivel, valores in niveles.items():
        print(f"{metodo} | {nivel} | VaR: {valores['VaR']:.4f} | Pérdida: {valores['Perdida']:.2f}€")