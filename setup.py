"""Setup script for Gmail Document Scraper."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding="utf-8").splitlines()
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="gmail-doc-scraper",
    version="1.0.0",
    description="Intelligent document extraction and classification from Gmail",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://gitlab.com/your-username/gmail-doc-scraper",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "gmail-scraper=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Email",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    keywords="gmail email documents extraction classification nlp ml",
    project_urls={
        "Bug Reports": "https://gitlab.com/your-username/gmail-doc-scraper/-/issues",
        "Source": "https://gitlab.com/your-username/gmail-doc-scraper",
        "Documentation": "https://gitlab.com/your-username/gmail-doc-scraper/-/blob/main/README.md",
    },
)
