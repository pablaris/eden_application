# Portfolio Fit Score

## Overview

The **Portfolio Fit Score** evaluates how well each fictional investment opportunity addresses the weaknesses and missing exposures identified in the current EDEN portfolio.

Unlike traditional security analysis, which focuses on company quality in isolation, this module focuses on **portfolio construction**.

### Core Question

> Which company improves the current portfolio the most?

The resulting Portfolio Fit Score is later combined with:

* Risk Score
* Compensation per Risk Score

to generate the final investment recommendation.

---

## Methodology

The Portfolio Fit Score is constructed using a rule-based scoring framework derived from:

1. Portfolio Gap Analysis
2. Candidate KPI Analysis

Historical price data is intentionally excluded from this stage of the analysis. Price-based metrics are evaluated separately through the Risk and Compensation per Risk modules.

---

# Portfolio Fit Categories

## 1. Sector Diversification

Measures whether the company improves industry diversification and fills missing sector exposures.

### Guiding Questions

* Which sectors are already heavily represented in the portfolio?
* Which important sectors are currently underrepresented or absent?
* Would adding this company improve diversification or increase concentration?

---

## 2. Growth Profile

Measures the company's contribution to the portfolio's long-term growth characteristics.

### Guiding Questions

* Is the portfolio currently tilted toward growth or capital preservation?
* Does the portfolio have sufficient exposure to long-term growth opportunities?
* Would this company improve the portfolio's overall growth profile?

---

## 3. Geographic Diversification

Measures whether the company broadens exposure to different geographic markets.

### Guiding Questions

* Which regions currently drive the portfolio's returns?
* Is the portfolio overly dependent on a specific region or economy?
* Would this company provide meaningful geographic diversification?

---

## 4. Structural Theme Exposure

Measures exposure to underrepresented long-term investment themes.

### Examples

* Energy Transition
* Industrial Automation
* Precision Agriculture
* AI Infrastructure

### Guiding Questions

* Which long-term investment themes are currently underrepresented in the portfolio?
* Does this company provide meaningful exposure to those themes?
* Would this company strengthen the portfolio's positioning for future structural trends?

---

## 5. Revenue Quality

Measures revenue predictability, recurring revenue characteristics, and business-model resilience.

### Guiding Questions

* How much of the portfolio is currently exposed to predictable recurring revenue models?
* Does this company generate stable revenues or depend primarily on one-time sales?
* Would adding this company improve the overall quality and predictability of portfolio cash flows?

---

# Scoring Framework

Each guiding question is evaluated using the following rubric:

| Response | Score |
| -------- | ----: |
| No       |   0.0 |
| Partial  |   0.5 |
| Yes      |   1.0 |

Each category contains exactly **three guiding questions**.

### Category Score Formula

```text
Category Score = (Sum of Points / 3) × 100
```

This produces a normalized score between **0 and 100**.

### Examples

| Responses         | Category Score |
| ----------------- | -------------: |
| No, No, No        |           0.00 |
| Yes, No, No       |          33.33 |
| Yes, Partial, No  |          50.00 |
| Yes, Yes, No      |          66.67 |
| Yes, Yes, Partial |          83.33 |
| Yes, Yes, Yes     |         100.00 |

---

# Package Structure

```text
portfolio_fit_score/
│
├── portfolio_fit_score.py
├── weights.py
├── final_calculation.py
│
└── data/
    ├── category_scores.csv
    ├── portfolio_fit_weights.csv
    ├── category_correlation_matrix.csv
    ├── pca_loadings.csv
    ├── redundancy_pairs.csv
    └── final_portfolio_fit_scores.csv
```

---

# Module Overview

## portfolio_fit_score.py

Converts rubric responses into category-level scores and exports:

```text
category_scores.csv
```

### Responsibilities

* Define rubric
* Score categories
* Export category-level results

---

## weights.py

Computes category weights using:

* Correlation Matrix Analysis
* Principal Component Analysis (PCA)

Exports:

```text
portfolio_fit_weights.csv
category_correlation_matrix.csv
pca_loadings.csv
redundancy_pairs.csv
```

### Responsibilities

* Detect redundant categories
* Identify latent portfolio dimensions
* Generate data-informed category weights

---

## final_calculation.py

Combines:

* Category Scores
* Category Weights

to generate the final Portfolio Fit ranking.

Exports:

```text
final_portfolio_fit_scores.csv
```

### Responsibilities

* Load category scores
* Load category weights
* Compute Portfolio Fit Score
* Generate ranking

---

# Design Principles

## Transparency

Every score can be traced back to specific evidence contained in the assessment materials.

---

## Reproducibility

Different analysts applying the same rubric should obtain the same category scores.

---

## Explainability

The methodology is intentionally simple enough to defend during Q&A while still incorporating quantitative techniques such as PCA and correlation analysis.

---

## Portfolio-Oriented Thinking

The framework evaluates how well a company improves the portfolio rather than how attractive the company appears in isolation.

---

# Outputs

The final output of this module is a ranked list of investment opportunities based exclusively on portfolio construction considerations.

This ranking serves as one of the three primary inputs used in the final investment recommendation:

1. Portfolio Fit Score
2. Risk Score
3. Compensation per Risk Score
