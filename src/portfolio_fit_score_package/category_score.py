import pandas as pd
from pathlib import Path

# ============================================================
# Project path resolution
# ============================================================
#
# Resolve the project's data directory at runtime rather than
# using hard-coded paths.
#
# This keeps the script portable across machines, notebooks,
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

    # Identify the directory where this script lives.
    project_root = Path(__file__).resolve().parent

    # Define the output folder used by the Portfolio Fit pipeline.
    data_dir = project_root / "data"

    # Create the folder if it is missing.
    data_dir.mkdir(exist_ok=True)

    return data_dir


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
# questions.
#
# Responses are converted into numerical values:
#
#     negative = 0.0
#     neutral  = 0.5
#     positive = 1.0
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
    "negative": 0.0,
    "neutral": 0.5,
    "positive": 1.0,
}

def score_category(answers):
    """
    Convert three rubric responses into a normalized category score.

    Parameters
    ----------
    answers : list[str]
        Exactly three responses, each of which must be one of:
            - "positive"
            - "neutral"
            - "negative"

    Returns
    -------
    float
        Category score on a 0-100 scale.

    Notes
    -----
    The score is computed as:

        (sum(points) / 3) × 100

    where:
        positive = 1.0
        neutral  = 0.5
        negative = 0.0

    This rule-based scoring approach keeps the methodology
    transparent, reproducible, and easy to defend in Q&A.
    """

    # Each category must contain exactly three rubric responses
    # so that all categories remain comparable.
    if len(answers) != 3:
        raise ValueError(
            "Each category must contain exactly three rubric answers."
        )

    points = []

    # Convert each qualitative answer into a numerical score.
    for answer in answers:
        key = answer.lower().strip()

        # Enforce a strict vocabulary to keep the scoring model
        # auditable and to avoid ambiguous inputs.
        if key not in ANSWER_TO_POINTS:
            raise ValueError(
                f"Invalid answer '{answer}'. "
                "Allowed values: positive, neutral, negative."
            )

        points.append(ANSWER_TO_POINTS[key])

    # Average the three answers and scale to a 0-100 score.
    return (sum(points) / 3.0) * 100.0


# ============================================================
# Rubric definition
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
        "Orion":     ["negative", "negative", "negative"],
        "Cleanergy": ["positive", "positive", "positive"],
        "NovaTerra": ["positive", "neutral",   "positive"],
    },
    "Growth Profile": {
        "Orion":     ["positive", "positive", "positive"],
        "Cleanergy": ["positive", "positive", "positive"],
        "NovaTerra": ["positive", "neutral",   "neutral"],
    },
    "Geographic Diversification": {
        "Orion":     ["neutral",  "neutral",  "neutral"],
        "Cleanergy": ["neutral",  "negative", "neutral"],
        "NovaTerra": ["positive", "positive", "positive"],
    },
    "Structural Theme Exposure": {
        "Orion":     ["neutral",  "neutral",  "neutral"],
        "Cleanergy": ["positive", "positive", "positive"],
        "NovaTerra": ["positive", "positive", "neutral"],
    },
    "Revenue Quality": {
        "Orion":     ["neutral",  "neutral",  "neutral"],
        "Cleanergy": ["positive", "positive", "neutral"],
        "NovaTerra": ["positive", "positive", "positive"],
    },
}

# Company universe included in the analysis.
companies = ["Orion", "Cleanergy", "NovaTerra"]

# ============================================================
# Category score calculation
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
# Export results
# ============================================================
#
# Save the category-level score table for downstream use in:
#   - weight calculation
#   - final Portfolio Fit computation
#   - sensitivity analysis
#   - final investment ranking
#
# Excel is used here so the output is easy to review manually
# and can be opened directly in spreadsheet software.
# ============================================================

category_scores.to_excel(DATA_DIR / "category_scores.xlsx")