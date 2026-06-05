import numpy as np
import pandas as pd
from pathlib import Path

# ============================================================
# Project path resolution
# ============================================================
#
# Resolve the project's data directory at runtime rather than
# relying on hard-coded absolute paths.
#
# This improves portability and ensures the module can be run
# consistently across notebooks, scripts, and different machines.
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

    # Identify the directory containing this script.
    project_root = Path(__file__).resolve().parent

    # Define the output folder used by the Portfolio Fit pipeline.
    data_dir = project_root / "data"

    # Create the directory if needed. exist_ok=True avoids errors
    # when the folder is already present.
    data_dir.mkdir(exist_ok=True)

    return data_dir


DATA_DIR = path()
OUTPUT_WEIGHTS_FILE = DATA_DIR / "portfolio_fit_weights.xlsx"
OUTPUT_MATRIX_FILE = DATA_DIR / "ahp_pairwise_matrix.xlsx"

# ============================================================
# Portfolio Fit criteria
# ============================================================
#
# These are the five strategic dimensions used to weight the
# Portfolio Fit Score.
#
# The objective of this module is not to estimate a market
# factor model. Instead, it translates portfolio-construction
# judgment into a structured weighting scheme using AHP.
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
# Economic interpretation for this case:
# - Sector Diversification receives the highest priority because
#   the existing portfolio is already concentrated in semis,
#   healthcare, and consumer, while lacking energy / industrial
#   exposure.
# - Structural Theme Exposure is also highly important because
#   the portfolio-gap analysis identifies a missing energy-transition
#   theme.
# - Growth Profile matters because the stock sleeve is meant to
#   take high-conviction growth bets.
# - Revenue Quality matters because recurring revenue improves
#   cash-flow durability.
# - Geographic Diversification matters, but it is a weaker
#   constraint than the others in this specific portfolio.
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
#   1. the priority vector (weights)
#   2. the consistency ratio (CR)
#
# The consistency ratio is a sanity check on the pairwise
# comparisons. In practice, CR < 0.10 is usually treated as
# acceptable.
#
# Using the principal eigenvector method is standard in AHP
# and gives a compact representation of the relative
# importance of each criterion.
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
        - normalized AHP weights
        - consistency ratio
    """
    n = matrix.shape[0]

    # AHP requires a square matrix of pairwise comparisons.
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("AHP matrix must be square.")

    # Eigen-decomposition of the pairwise comparison matrix.
    # The dominant eigenvector gives the priority weights.
    eigenvalues, eigenvectors = np.linalg.eig(matrix)

    # Identify the eigenvector corresponding to the largest
    # eigenvalue (dominant principal component of judgment).
    max_index = np.argmax(eigenvalues.real)
    lambda_max = eigenvalues.real[max_index]
    weights = eigenvectors[:, max_index].real

    # Normalize the priority vector so that weights sum to 1.
    weights = weights / weights.sum()

    # Consistency Index (CI):
    # Measures how coherent the pairwise judgments are relative
    # to a perfectly consistent matrix.
    ci = (lambda_max - n) / (n - 1)

    # Saaty's Random Index (RI) table for CR computation.
    # The RI approximates the average CI of randomly generated
    # reciprocal matrices of the same size.
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

    # Consistency Ratio (CR) = CI / RI.
    # Lower values indicate more internally consistent judgments.
    cr = ci / ri if ri != 0 else 0.0

    return weights, cr

# ============================================================
# Compute weights
# ============================================================
#
# Convert the pairwise comparison matrix into final AHP
# priority weights.
# ============================================================

weights_array, consistency_ratio = ahp_weights(A)

weights = pd.Series(weights_array, index=CRITERIA, name="Weight")

# Defensive normalization to ensure the final weights sum to 1.
weights = weights / weights.sum()

# ============================================================
# Save outputs
# ============================================================
#
# Save both the resulting weights and the raw pairwise matrix.
# Keeping the matrix on disk is useful for auditability and
# for defending the methodology during Q&A.
# ============================================================

weights_df = weights.reset_index()
weights_df.columns = ["Category", "Weight"]
weights_df.to_excel(OUTPUT_WEIGHTS_FILE, index=False)

pd.DataFrame(A, index=CRITERIA, columns=CRITERIA).to_excel(OUTPUT_MATRIX_FILE)

# ============================================================
# Diagnostics
# ============================================================
#
# Print the pairwise matrix, the resulting weights, and the
# consistency ratio so the output is easy to inspect and
# validate during development.
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