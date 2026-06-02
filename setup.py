from pathlib import Path
from setuptools import find_packages, setup

HERE = Path(__file__).parent.resolve()
README = (HERE / "README.md").read_text(encoding="utf-8") if (HERE / "README.md").exists() else ""

setup(
    name="eden-quant-analysis",
    version="0.1.0",
    description="Quant analysis project for EDEN assessment",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Darius-Luca Petruti",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "numpy>=2.4,<3",
        "pandas>=2.2,<3",
        "matplotlib>=3.8,<4",
        "scipy>=1.11,<2",
        "yfinance>=0.2,<1",
        "openpyxl>=3.1,<4",
    ],
    include_package_data=True,
    zip_safe=False,
)
