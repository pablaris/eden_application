import numpy as np  # pyright: ignore[reportMissingImports]
import pandas as pd  # pyright: ignore[reportMissingModuleSource]
from pathlib import Path

# ============================================================
# Project paths
# ============================================================
#
# Resolve the data directory at runtime so the script does not
# depend on hard-coded absolute paths.
#
# This makes the module portable across machines, notebooks,
# and execution environments.
# ============================================================

def path() -> Path:
    """
    Return the project's data directory.

    The directory is created automatically if it does not
    already exist.

    Returns
    -------
    Path
        Absolute path to the project's data directory.
    """

    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

DATA_DIR = path()
OUTPUT_WEIGHTS_FILE = DATA_DIR / "portfolio_fit_weights.xlsx"
OUTPUT_MATRIX_FILE = DATA_DIR / "ahp_pairwise_matrix.xlsx"

# ============================================================
# Portfolio Fit criteria
# ============================================================
#
# These are the five categories used to build the Portfolio
# Fit Score.
#
# The weights are determined using AHP because the objective is
# to translate portfolio-construction judgment into a structured,
# reproducible weighting scheme.
# ============================================================

CRITERIA = [
    "Sector Diversification",
    "Growth Profile",
    "Geographic Diversification",
    "Structural Theme Exposure",
    "Revenue Quality",
]

# ============================================================
# Pairwise comparison matrix
# ============================================================
#
# The matrix uses Saaty's 1-9 scale:
#
#   1 = equally important
#   3 = moderately more important
#   5 = strongly more important
#   7 = very strongly more important
#   9 = extremely more important
#
# Reciprocal structure:
#   A[i, j] = 1 / A[j, i]
#
# Interpretation for this case:
# - Sector Diversification is the most important because the
#   portfolio already has semis / healthcare / consumer and
#   lacks energy / industrial exposure.
# - Structural Theme Exposure is next because the portfolio
#   lacks energy-transition exposure.
# - Growth Profile matters, but the stock sleeve is already
#   intended for high-conviction growth.
# - Revenue Quality matters because recurring revenue improves
#   durability.
# - Geographic Diversification matters, but it is the least
#   critical gap in this specific portfolio.
# ============================================================

A = np.array([
    [1,   3,   5,   2,   4],
    [1/3, 1,   3,   1/2, 2],
    [1/5, 1/3, 1,   1/4, 1/2],
    [1/2, 2,   4,   1,   3],
    [1/4, 1/2, 2,   1/3, 1]
], dtype=float)

# ============================================================
# AHP helper function
# ============================================================
#
# This function computes:
#   1. the priority weights
#   2. the consistency ratio
#
# The consistency ratio tells us whether the pairwise judgments
# are logically coherent. In practice, CR < 0.10 is usually
# considered acceptable.
# ============================================================

def ahp_weights(matrix: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Compute AHP weights using the principal eigenvector method.

    Parameters
    ----------
    matrix : np.ndarray
        Square reciprocal pairwise comparison matrix.

    Returns
    -------
    tuple[np.ndarray, float]
        - normalized weights
        - consistency ratio
    """

    n = matrix.shape[0]
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("AHP matrix must be square.")
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    max_index = np.argmax(eigenvalues.real)
    lambda_max = eigenvalues.real[max_index]
    weights = eigenvectors[:, max_index].real
    weights = weights / weights.sum()
    ci = (lambda_max - n) / (n - 1)
    ri_table = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49,
    }
    ri = ri_table.get(n, 1.49)
    cr = ci / ri if ri != 0 else 0.0
    return weights, cr

# ============================================================
# Compute weights
# ============================================================

weights_array, consistency_ratio = ahp_weights(A)
weights = pd.Series(weights_array, index=CRITERIA, name="Weight")
weights = weights / weights.sum()

# ============================================================
# Save outputs
# ============================================================

weights_df = weights.reset_index()
weights_df.columns = ["Category", "Weight"]
weights_df.to_excel(OUTPUT_WEIGHTS_FILE, index=False)
pd.DataFrame(A, index=CRITERIA, columns=CRITERIA).to_excel(OUTPUT_MATRIX_FILE)

# ============================================================
# Diagnostics
# ============================================================
#
# These prints help validate that the weights are defensible
# and internally consistent.
# ============================================================

print("\n=== AHP PAIRWISE MATRIX ===")
print(pd.DataFrame(A, index=CRITERIA, columns=CRITERIA).round(3))
print("\n=== AHP WEIGHTS ===")
print((weights * 100).round(2).sort_values(ascending=False))
print(f"\nConsistency Ratio: {consistency_ratio:.4f}")
if consistency_ratio > 0.10:
    print("Warning: pairwise judgments may be inconsistent.")
else:
    print("AHP consistency is acceptable.")