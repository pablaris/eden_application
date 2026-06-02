import pandas as pd  # pyright: ignore[reportMissingModuleSource]
from portfolio_fit_score_package.modules import path  # pyright: ignore[reportMissingImports]

# ============================================================
# Data directory resolution
# ============================================================
# Resolve the output directory at runtime instead of hard-coding
# file paths. This improves portability and makes the code easier
# to run across different environments and machines.
# ============================================================

DATA_DIR = path()

# ============================================================
# Portfolio Fit Scoring Model
# ============================================================
#
# Objective:
# Quantify how well each fictional company addresses the
# weaknesses and missing exposures identified in the current
# EDEN portfolio.
#
# Methodology:
# Each Portfolio Fit category is evaluated using three guiding
# questions. Responses are converted into numerical values:
#
#     No      -> 0.0
#     Partial -> 0.5
#     Yes     -> 1.0
#
# Category Score:
#
#     Category Score = (Sum of Points / 3) × 100
#
# This produces a normalized score between 0 and 100 for each
# category, allowing direct comparison across companies.
#
# The final Portfolio Fit Score is computed later by combining
# category-level scores with externally determined weights.
# ============================================================

ANSWER_TO_POINTS = {
    "no": 0.0,
    "partial": 0.5,
    "yes": 1.0,
}


def score_category(answers):
    """
    Convert three rubric responses into a normalized category score.

    Parameters
    ----------
    answers : list[str]
        Exactly three responses, each of which must be one of:
            - "yes"
            - "partial"
            - "no"

    Returns
    -------
    float
        Category score on a 0–100 scale.

    Notes
    -----
    The score is computed as:

        (sum(points) / 3) × 100

    where:
        yes     = 1.0
        partial = 0.5
        no      = 0.0

    This rule-based scoring approach keeps the methodology
    transparent, reproducible, and easy to defend in Q&A.
    """

    # Each category must be evaluated on exactly three guiding
    # questions to preserve consistency across all dimensions.
    if len(answers) != 3:
        raise ValueError(
            "Each category must contain exactly three rubric answers."
        )

    points = []

    # Convert each qualitative answer into its numerical equivalent.
    for answer in answers:
        key = answer.lower().strip()

        # Enforce a strict response vocabulary so that the scoring
        # model remains auditable and free from ambiguous inputs.
        if key not in ANSWER_TO_POINTS:
            raise ValueError(
                f"Invalid answer '{answer}'. "
                "Allowed values: yes, partial, no."
            )

        points.append(ANSWER_TO_POINTS[key])

    # Average the three question scores and scale to 0–100.
    return (sum(points) / 3.0) * 100.0


# ============================================================
# Rubric Definition
# ============================================================
#
# The rubric is derived from:
#   1. Portfolio Gap Analysis
#   2. Candidate KPI Analysis
#
# Scores are assigned using the evidence provided in the case
# materials rather than historical price data.
#
# Category definitions:
#
# Sector Diversification
#     Measures whether the company improves industry
#     diversification and fills missing sector exposures.
#
# Growth Profile
#     Measures the company's contribution to the portfolio's
#     long-term growth characteristics.
#
# Geographic Diversification
#     Measures whether the company broadens exposure to
#     different geographic markets.
#
# Structural Theme Exposure
#     Measures exposure to underrepresented long-term themes
#     such as energy transition, industrial automation, or
#     precision agriculture.
#
# Revenue Quality
#     Measures revenue predictability, recurring revenue
#     characteristics, and overall business-model resilience.
#
# Important:
# These scores are evidence-based judgments derived from the
# assessment documents and should be interpreted as
# portfolio-construction inputs rather than standalone measures
# of company quality.
# ============================================================

rubric = {
    "Sector Diversification": {
        "Orion":     ["no",      "no",      "no"],
        "Cleanergy": ["yes",     "yes",     "yes"],
        "NovaTerra": ["yes",     "partial", "yes"],
    },
    "Growth Profile": {
        "Orion":     ["yes",     "yes",     "yes"],
        "Cleanergy": ["yes",     "yes",     "yes"],
        "NovaTerra": ["yes",     "partial", "partial"],
    },
    "Geographic Diversification": {
        "Orion":     ["partial", "partial", "partial"],
        "Cleanergy": ["partial", "no",      "partial"],
        "NovaTerra": ["yes",     "yes",     "yes"],
    },
    "Structural Theme Exposure": {
        "Orion":     ["partial", "partial", "partial"],
        "Cleanergy": ["yes",     "yes",     "yes"],
        "NovaTerra": ["yes",     "yes",     "partial"],
    },
    "Revenue Quality": {
        "Orion":     ["partial", "partial", "partial"],
        "Cleanergy": ["yes",     "yes",     "partial"],
        "NovaTerra": ["yes",     "yes",     "yes"],
    },
}

# Company universe included in the analysis.
companies = ["Orion", "Cleanergy", "NovaTerra"]

# ============================================================
# Category Score Calculation
# ============================================================
#
# Convert each company's rubric responses into category-level
# numerical scores.
#
# Output structure:
#   Rows    -> Companies
#   Columns -> Portfolio Fit categories
#
# Each cell contains a score between 0 and 100.
# ============================================================

category_scores = pd.DataFrame(index=companies)

for category, company_answers in rubric.items():
    category_scores[category] = {
        company: score_category(company_answers[company])
        for company in companies
    }

# ============================================================
# Export Results
# ============================================================
#
# Save the category-level score table for downstream use in:
#   - weight calculation
#   - final Portfolio Fit computation
#   - sensitivity analysis
#   - final investment ranking
# ============================================================

category_scores.to_csv(DATA_DIR / "category_scores.csv")