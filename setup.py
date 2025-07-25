#!/usr/bin/env python3
"""
Setup script for docShadow CLI
"""

from setuptools import setup, find_packages
import os

# Read the README file
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
try:
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "docShadow CLI - Silent companion for Git documentation generation"

setup(
    name="docshadow",
    version="0.1.0",
    author="docShadow Team",
    author_email="",
    description="Silent companion for Git documentation generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/docGen-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "GitPython>=3.1.0",
        "pyyaml>=6.0",
        "pathspec>=0.10.0",  # For .docignore parsing
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "doc=docshadow.__main__:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 