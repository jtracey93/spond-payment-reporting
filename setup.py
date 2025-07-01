#!/usr/bin/env python3
"""
Setup script for Spond Payment Reporting Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Spond Payment Reporting Tool"

setup(
    name="spond-payment-reporting",
    version="1.0.0",
    author="jtracey93",
    author_email="",
    description="A tool to generate payment reports from Spond club management system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jtracey93/spond-payment-reporting",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.21.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "spond-report=spond_reporting.cli:main",
            "spond-mcp-server=spond_reporting.mcp_server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
