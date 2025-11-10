from setuptools import setup, find_packages

setup(
    name="ss91v3",
    version="0.1.0",
    description="SS91-V3: Sentiment & Signal system with Sherloock adapter",
    packages=find_packages(),
    include_package_data=True,
    
    install_requires=[
        "python-dotenv",
        "yfinance",
        "pandas",
        "numpy",
        "pandas-ta",
        "requests",
        "pytrends",
        "vaderSentiment",
        "scikit-learn",
        "z3-solver",
        "pulp",
        "sympy",
        "psutil",
    ],
    
    # Esta línea es correcta y exige Python 3.12 o superior
    python_requires=">=3.12",
)
