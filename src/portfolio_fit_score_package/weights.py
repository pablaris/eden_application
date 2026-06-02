import numpy as np  # pyright: ignore[reportMissingImports]
import pandas as pd  # pyright: ignore[reportMissingModuleSource]
from portfolio_fit_score_package.modules import path  # pyright: ignore[reportMissingImports]
from itertools import combinations

# ============================================================
# Project paths
# ============================================================
#
# Resolve the working directory at runtime rather than using
# hard-coded paths. This keeps the script portable across
# machines and execution environments.
# ============================================================

DATA_DIR = path()

INPUT_FILE = DATA_DIR / "category_scores.csv"
OUTPUT_WEIGHTS_FILE = DATA_DIR / "portfolio_fit_weights.csv"
OUTPUT_CORR_FILE = DATA_DIR / "category_correlation_matrix.csv"
OUTPUT_LOADINGS_FILE = DATA_DIR / "pca_loadings.csv"
OUTPUT_REDUNDANCY_FILE = DATA_DIR / "redundancy_pairs.csv"

# ============================================================
# Model parameters
# ============================================================
#
# EXPLAINED_VARIANCE_THRESHOLD:
# Minimum proportion of total variance we want to capture with
# the selected principal components.
#
# REDUNDANCY_THRESHOLD:
# Correlation threshold above which two categories are flagged
# as potentially redundant.
# ============================================================

EXPLAINED_VARIANCE_THRESHOLD = 0.80
REDUNDANCY_THRESHOLD = 0.85

# ============================================================
# Load category scores
# ============================================================
#
# The input file is expected to contain the category scores
# produced by portfolio_fit_score.py.
#
# Structure:
#   Rows    -> companies
#   Columns -> Portfolio Fit categories
#
# The purpose of this script is to infer a data-driven set of
# weights from the structure of those category scores.
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Could not find input file: {INPUT_FILE}")

# Read the category score table.
# The first column is the company name, so we use it as the index.
df = pd.read_csv(INPUT_FILE, index_col=0)

# Keep only numeric columns.
# If a final score column is present, remove it because weights
# should be calculated only from the category-level scores.
numeric_df = df.select_dtypes(include=[np.number]).copy()

if "Portfolio Fit Score" in numeric_df.columns:
    numeric_df = numeric_df.drop(columns=["Portfolio Fit Score"])

# PCA requires at least two variables.
if numeric_df.shape[1] < 2:
    raise ValueError("Need at least two numeric categories to compute PCA weights.")

# ============================================================
# Basic validation
# ============================================================
#
# Categories with zero variance provide no useful information
# for correlation analysis or PCA, so we exclude them.
# ============================================================

zero_var_cols = [
    c for c in numeric_df.columns
    if np.isclose(numeric_df[c].std(ddof=0), 0.0)
]

if zero_var_cols:
    raise ValueError(
        "The following category columns have zero variance and cannot be used for PCA: "
        + ", ".join(zero_var_cols)
    )

criteria = numeric_df.columns.tolist()

# ============================================================
# Correlation matrix
# ============================================================
#
# The correlation matrix is used to detect overlapping or
# redundant Portfolio Fit categories.
#
# A high absolute correlation suggests that two categories may
# be measuring the same underlying portfolio characteristic.
# ============================================================

corr_matrix = numeric_df.corr()
corr_matrix.to_csv(OUTPUT_CORR_FILE)

# Identify highly correlated category pairs.
# These are not automatically removed, but they are useful for
# interpretation and model diagnostics.
redundancy_rows = []
for c1, c2 in combinations(criteria, 2):
    corr_value = corr_matrix.loc[c1, c2]
    if abs(corr_value) >= REDUNDANCY_THRESHOLD:
        redundancy_rows.append(
            {
                "Category 1": c1,
                "Category 2": c2,
                "Correlation": corr_value,
                "Potentially Redundant": True,
            }
        )

redundancy_df = pd.DataFrame(redundancy_rows)
redundancy_df.to_csv(OUTPUT_REDUNDANCY_FILE, index=False)

# ============================================================
# PCA via eigen-decomposition of the correlation matrix
# ============================================================
#
# PCA is performed on the correlation matrix rather than the raw
# values because the categories are already on the same scale
# and we want to analyze structure, not magnitude.
#
# For standardized variables, eigendecomposition of the
# correlation matrix is equivalent to PCA.
# ============================================================

corr_values = corr_matrix.values
eigvals, eigvecs = np.linalg.eigh(corr_values)

# Sort eigenvalues and eigenvectors from largest to smallest.
order = np.argsort(eigvals)[::-1]
eigvals = eigvals[order]
eigvecs = eigvecs[:, order]

# Small negative values may appear due to floating-point noise.
# Clip them to zero to keep the decomposition numerically stable.
eigvals = np.clip(eigvals, 0, None)

# Explained variance ratio for each principal component.
explained_variance_ratio = eigvals / eigvals.sum()
cumulative_explained_variance = np.cumsum(explained_variance_ratio)

# Select the smallest number of components that explains enough
# total variance according to the chosen threshold.
n_components = int(
    np.searchsorted(cumulative_explained_variance, EXPLAINED_VARIANCE_THRESHOLD) + 1
)
n_components = max(1, min(n_components, len(criteria)))

# PCA loadings:
# loading = eigenvector * sqrt(eigenvalue)
# Loadings indicate how strongly each category contributes to
# each principal component.
loadings = eigvecs[:, :n_components] * np.sqrt(eigvals[:n_components])

loadings_df = pd.DataFrame(
    loadings,
    index=criteria,
    columns=[f"PC{i+1}" for i in range(n_components)]
)
loadings_df.to_csv(OUTPUT_LOADINGS_FILE)

# ============================================================
# Convert PCA structure into weights
# ============================================================
#
# The weighting scheme gives more importance to categories that:
#   1. load strongly on the main principal components, and
#   2. contribute to components explaining a larger share of
#      total variance.
#
# This creates a data-driven set of weights that emphasizes the
# dominant structure in the category score table while reducing
# the risk of double-counting highly correlated dimensions.
# ============================================================

importance = np.zeros(len(criteria))

for i in range(n_components):
    importance += np.abs(loadings[:, i]) * explained_variance_ratio[i]

weights = importance / importance.sum()
weights_series = pd.Series(weights, index=criteria, name="Weight")

# Save weights in tabular form for downstream use.
weights_df = weights_series.reset_index()
weights_df.columns = ["Category", "Weight"]
weights_df.to_csv(OUTPUT_WEIGHTS_FILE, index=False)

# ============================================================
# Output
# ============================================================
#
# Print the main diagnostics so the model is transparent during
# development and easy to discuss in the final presentation.
# ============================================================

print("\n=== CATEGORY CORRELATION MATRIX ===")
print(corr_matrix.round(3))

print("\n=== HIGHLY CORRELATED PAIRS (if any) ===")
if redundancy_df.empty:
    print("No category pairs exceeded the redundancy threshold.")
else:
    print(redundancy_df.round(3).to_string(index=False))

print("\n=== PCA EXPLAINED VARIANCE ===")
for i, evr in enumerate(explained_variance_ratio[:n_components], start=1):
    print(f"PC{i}: {evr:.4f}")

print(
    f"\nCumulative explained variance using {n_components} PCs: "
    f"{cumulative_explained_variance[n_components - 1]:.4f}"
)

print("\n=== PCA LOADINGS ===")
print(loadings_df.round(4))

print("\n=== FINAL WEIGHTS ===")
print((weights_series * 100).round(2).sort_values(ascending=False))

print(f"\nSaved weights to: {OUTPUT_WEIGHTS_FILE}")
print(f"Saved correlation matrix to: {OUTPUT_CORR_FILE}")
print(f"Saved PCA loadings to: {OUTPUT_LOADINGS_FILE}")
print(f"Saved redundancy report to: {OUTPUT_REDUNDANCY_FILE}")