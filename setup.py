from setuptools import setup, find_packages

setup(
    name="bdd-generator",
    version="0.1.0",
    description="BDD scenario generator with auto-refinement using Claude API",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "anthropic>=0.40.0",
        "typer>=0.12.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0.0"],
    },
    entry_points={},
)
