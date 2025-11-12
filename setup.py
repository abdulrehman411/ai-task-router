"""Setup script for AI Task Router."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="ai-task-router",
    version="1.0.0",
    description="Intelligent multi-agent task routing system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Task Router Team",
    author_email="",
    url="https://github.com/yourusername/ai-task-router",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "langchain>=0.1.0",
        "langgraph>=0.0.20",
        "langchain-openai>=0.0.5",
        "langchain-core>=0.1.0",
        "pydantic>=2.0.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "streamlit>=1.28.0",
        "requests>=2.31.0",
        "trafilatura>=1.6.0",
        "pymupdf>=1.23.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        "console_scripts": [
            "ai-task-router-api=app.api:main",
        ],
    },
)

