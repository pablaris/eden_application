#Distribución empírica vs. Normal
# Fat tails, skewness y kurtosis

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import yfinance as yf


# Descarga de datos

sp500 = yf.download('^GSPC', period = '11y', interval = '1d')
prices = sp500["Close"].squeeze() 
# Cálculo de log-retornos

log_returns = np.log(prices).diff()
log_returns = log_returns.dropna()


# Estadísticos descriptivos

mu     = np.mean(log_returns) # TU CÓDIGO AQUÍ
sigma  = np.std(log_returns) # TU CÓDIGO AQUÍ
skew   = stats.skew(log_returns)  # TU CÓDIGO AQUÍ
kurt   = stats.kurtosis(log_returns)  # TU CÓDIGO AQUÍ

print("=" * 40)
print("ESTADÍSTICOS DESCRIPTIVOS — S&P 500")
print("=" * 40)
# Imprime los cuatro estadísticos con formato claro
print(f"Mu: {mu}")
print(f"Standard Deviation: {sigma}")
print(f"Skewness: {skew}")
print(f"Kurt: {kurt}")

# Histograma vs. Normal teórica

fig, axes = plt.subplots(1, 2, figsize=(14, 5))


axes[0].hist(log_returns, bins=50, density=True, alpha=0.6, color='blue', label='Datos Reales')
x = np.linspace(min(log_returns), max(log_returns), 100)
y = stats.norm.pdf(x, mu, sigma)
axes[0].plot(x, y, color='red', linewidth=2, label='Curva Normal Teórica')
axes[0].set_title("Distribución de rendimientos logarítmicos")
axes[0].set_xlabel("Rendimiento Logarítmico")
axes[0].set_ylabel("Densidad")
axes[0].legend() 


stats.probplot(log_returns, dist = "norm", plot = axes[1])
axes[1].set_title("QQ Plot de Rendimientos logarítmicos")
axes[1].set_xlabel("Cuantiles Teóricos (Distribución Normal)")
axes[1].set_ylabel("Cuantiles de los Datos Reales")


plt.tight_layout()
plt.show()

