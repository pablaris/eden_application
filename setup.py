from setuptools import setup, find_packages

setup(
    name="eden_quant_assessment",
    version="0.1.0",
    description="EDEN Quant Team Assessment: Portfolio fit, risk, and tail-risk analysis",
    author="EDEN Quant Team",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "yfinance",
        "openpyxl",
    ],
)
