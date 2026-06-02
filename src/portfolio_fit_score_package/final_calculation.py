import pandas as pd  # pyright: ignore[reportMissingModuleSource]
from portfolio_fit_score_package.modules import path  # pyright: ignore[reportMissingImports]

# ============================================================
# Project paths
# ============================================================
#
# Resolve the data directory at runtime.
#
# This avoids hard-coded paths and allows all modules in the
# Portfolio Fit pipeline to read and write data consistently.
# ============================================================

DATA_DIR = path()

CATEGORY_SCORES_FILE = DATA_DIR / "category_scores.csv"
WEIGHTS_FILE = DATA_DIR / "portfolio_fit_weights.csv"
OUTPUT_FILE = DATA_DIR / "final_portfolio_fit_scores.csv"

# ============================================================
# Load inputs
# ============================================================
#
# This module combines:
#
#   1. Category Scores
#      Produced by portfolio_fit_score.py
#
#   2. Category Weights
#      Produced by weights.py
#
# The objective is to compute a final Portfolio Fit Score
# for each company and generate a ranking.
# ============================================================

if not CATEGORY_SCORES_FILE.exists():
    raise FileNotFoundError(
        f"Missing category scores file: {CATEGORY_SCORES_FILE}"
    )

if not WEIGHTS_FILE.exists():
    raise FileNotFoundError(
        f"Missing weights file: {WEIGHTS_FILE}"
    )

# ============================================================
# Load category scores
# ============================================================
#
# Expected structure:
#
# Rows:
#   Orion
#   Cleanergy
#   NovaTerra
#
# Columns:
#   Portfolio Fit categories
#
# Values:
#   Scores between 0 and 100
# ============================================================

category_scores = pd.read_csv(
    CATEGORY_SCORES_FILE,
    index_col=0
)

# ============================================================
# Load category weights
# ============================================================
#
# Expected structure:
#
# Category | Weight
#
# Example:
#
# Sector Diversification | 0.35
# Growth Profile         | 0.20
# ...
#
# Weights are generated through the PCA /
# correlation-matrix analysis performed in weights.py
# ============================================================

weights_df = pd.read_csv(WEIGHTS_FILE)

required_cols = {"Category", "Weight"}

if not required_cols.issubset(weights_df.columns):
    raise ValueError(
        f"Weights file must contain columns {required_cols}. "
        f"Found columns: {list(weights_df.columns)}"
    )

weights_df = weights_df.set_index("Category")

# ============================================================
# Prepare category score matrix
# ============================================================
#
# Remove any pre-existing Portfolio Fit Score column to avoid
# accidentally using an outdated result in the calculation.
# ============================================================

if "Portfolio Fit Score" in category_scores.columns:
    category_scores = category_scores.drop(
        columns=["Portfolio Fit Score"]
    )

# ============================================================
# Category alignment validation
# ============================================================
#
# Verify that every category appearing in the weight table
# also exists in the category score table.
#
# This prevents accidental mismatches between:
#
#   portfolio_fit_score.py
#
# and
#
#   weights.py
# ============================================================

weight_categories = weights_df.index.tolist()

missing_categories = [
    c
    for c in weight_categories
    if c not in category_scores.columns
]

if missing_categories:
    raise ValueError(
        "The following weighted categories are missing "
        "from category_scores.csv: "
        + ", ".join(missing_categories)
    )

# Reorder category columns to match the weight table.
# This guarantees proper matrix multiplication.
category_scores = category_scores[weight_categories]

# ============================================================
# Weight validation
# ============================================================
#
# Convert weights to numeric values and normalize them
# defensively.
#
# Normalization is applied because PCA output may contain
# small rounding errors that prevent the weights from
# summing exactly to 1.
# ============================================================

weights = weights_df["Weight"].astype(float)

weights_sum = weights.sum()

if weights_sum <= 0:
    raise ValueError(
        "Weights must sum to a positive value."
    )

weights = weights / weights_sum

# ============================================================
# Portfolio Fit Score Calculation
# ============================================================
#
# Formula:
#
# Portfolio Fit Score =
#
# Σ(Category Score × Category Weight)
#
# Since:
#
#   Category Scores ∈ [0,100]
#
# and
#
#   Σ Weights = 1
#
# the resulting Portfolio Fit Score also lies
# approximately between 0 and 100.
# ============================================================

category_scores["Portfolio Fit Score"] = (
    category_scores.mul(weights, axis=1)
    .sum(axis=1)
)

# ============================================================
# Ranking
# ============================================================
#
# Rank companies from highest Portfolio Fit Score
# to lowest Portfolio Fit Score.
# ============================================================

final_scores = category_scores.sort_values(
    "Portfolio Fit Score",
    ascending=False
)

# Round values for presentation and reporting.
final_scores = final_scores.round(2)

# ============================================================
# Display Results
# ============================================================
#
# Output:
#
# 1. Final category weights
# 2. Complete Portfolio Fit score table
# 3. Final ranking
# ============================================================

print("\n=== PORTFOLIO FIT WEIGHTS ===")
print((weights * 100).round(2))

print("\n=== FINAL PORTFOLIO FIT SCORES ===")
print(final_scores)

print("\n=== FINAL RANKING ===")

ranking = final_scores["Portfolio Fit Score"]

print(ranking)

# ============================================================
# Export Results
# ============================================================
#
# Save final Portfolio Fit scores for use in:
#
#   - Risk analysis
#   - Compensation-per-risk analysis
#   - Final investment recommendation
#   - Presentation exhibits
# ============================================================

final_scores.to_csv(OUTPUT_FILE)

print(f"\nSaved final scores to: {OUTPUT_FILE}")