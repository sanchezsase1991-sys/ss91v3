from setuptools import setup, find_packages

setup(
    name="ss91v3",
    version="0.1.0",
    description="SS91-V3: Sentiment & Signal system with Sherloock adapter",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv",
        "supabase",
        "yfinance",
        "pandas",
        "numpy",
        "pandas-ta",
        "requests",
        "pytrends",
        "textblob",
        "snscrape",
        "joblib",
        "prophet",
        "scikit-learn",
        "ntfy",
        "tqdm",
        "fredapi"
    ],
    python_requires=">=3.9",
)
