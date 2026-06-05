# EDEN Quant Assessment

A quantitative investment analysis framework developed for the EDEN Fund stock-selection assessment.

The objective of the project is to evaluate a set of fictional investment opportunities and determine which company should be added to the existing EDEN portfolio.

The analysis combines:

* Portfolio Construction Analysis
* Portfolio Fit Scoring
* Risk Analysis
* Tail-Risk Analysis
* Benchmark Comparison
* Fundamental KPI Validation

to generate a transparent, reproducible, and defensible investment recommendation.

---

# Project Structure

```text
eden_application/
│
├── README.md
├── setup.py
├── requirements.txt
├── Assumptions.md
│
├── notebooks/
│   └── candidate_quant_analysis.ipynb
│
├── src/
│   ├── portfolio_fit_score_package/
│   │   ├── __init__.py
│   │   ├── modules.py
│   │   ├── category_score.py
│   │   ├── weights.py
│   │   ├── final_calculation.py
│   │   └── data/
│   │
│   ├── VaR_package/
│   │   ├── __init__.py
│   │   └── VaR.py
│   │
│   └── fat_tails_package/
│       ├── __init__.py
│       └── fat_tails.py
│
└── tests/
    └── test_portfolio_fit_score.py
```

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd eden_application
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Alternatively, install the project as a package:

```bash
pip install -e .
```

---

# Methodology Overview

The investment recommendation is built from three independent analytical layers:

## 1. Portfolio Fit Score

The Portfolio Fit Score measures how well a company addresses the weaknesses and missing exposures identified in the current EDEN portfolio.

The framework evaluates five dimensions:

* Sector Diversification
* Growth Profile
* Geographic Diversification
* Structural Theme Exposure
* Revenue Quality

Each category is scored using a rule-based framework built from predefined guiding questions.

Responses are classified as:

| Response | Score |
| -------- | ----: |
| Positive |   1.0 |
| Neutral  |   0.5 |
| Negative |   0.0 |

Category scores are calculated as:

```text
Category Score = (Sum of Points / 3) × 100
```

The resulting category scores are combined using weights generated through the Analytic Hierarchy Process (AHP).

---

## 2. Risk Analysis

The Risk Analysis module evaluates the downside risk associated with each investment opportunity.

Key metrics include:

* Annualized Volatility
* Rolling Volatility
* Beta
* Correlation
* Historical VaR
* Parametric VaR
* CVaR (Expected Shortfall)

The purpose of this module is to quantify how much risk investors must assume when adding a new position to the portfolio.

---

## 3. Compensation per Risk Analysis

This component evaluates whether investors are being adequately compensated for the level of risk assumed.

Key metrics include:

* Sharpe Ratio
* Sortino Ratio
* Annualized Return
* Maximum Drawdown

The objective is to identify companies that generate attractive returns relative to their risk profile.

---

## 4. Fundamental Validation

A KPI-based regression framework is used to assess whether stock-price evolution appears to be supported by underlying business fundamentals.

Examples of explanatory variables include:

* Revenue Growth
* Gross Margin
* Software / Subscription Revenue Mix
* AI Prediction Accuracy
* Assets Under Management
* Industry-Specific KPI Growth

The purpose of this analysis is not to establish causality, but rather to evaluate whether price performance appears directionally consistent with business performance.

---

# Package Overview

## portfolio_fit_score_package

Responsible for portfolio construction analysis.

Modules:

### category_score.py

Calculates category-level Portfolio Fit scores using the rubric-based methodology.

Output:

```text
category_scores.xlsx
```

---

### weights.py

Computes category weights using the Analytic Hierarchy Process (AHP).

Outputs:

```text
portfolio_fit_weights.xlsx
ahp_pairwise_matrix.xlsx
```

---

### final_calculation.py

Combines category scores and category weights to produce the final Portfolio Fit ranking.

Output:

```text
final_portfolio_fit_scores.xlsx
```

---

## VaR_package

Computes:

* Historical VaR
* Parametric VaR
* CVaR

Purpose:

Quantify downside tail risk.

---

## fat_tails_package

Analyzes return distributions using:

* Histograms
* QQ Plots
* Skewness
* Kurtosis

Purpose:

Assess whether return distributions deviate from normality.

---

# Assumptions

The project assumptions are documented in:

```text
Assumptions.md
```

These assumptions define:

* Return conventions
* Annualization methodology
* Risk-free rate assumptions
* Position sizing assumptions
* VaR and CVaR methodology
* Interpretation guidelines

All analytical modules should remain consistent with these assumptions.

---

# Testing

Run the test suite:

```bash
pytest
```

Current tests validate:

* Path resolution
* Portfolio Fit infrastructure
* Data export functionality

---

# Output

The final objective of the project is to generate a ranked investment recommendation that integrates:

1. Portfolio Fit Score
2. Risk Analysis
3. Compensation per Risk Analysis
4. Fundamental Validation

The resulting recommendation is designed to mimic the decision-making process of an investment committee and provide a transparent justification for portfolio inclusion.
