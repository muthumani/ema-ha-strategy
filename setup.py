"""
Setup script for the EMA Heikin Ashi Strategy package.
"""

from setuptools import setup, find_packages
import os

# Get version from version.py
version = {}
with open(os.path.join("version.py")) as f:
    exec(f.read(), version)

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ema_ha_strategy",
    version=version['__version__'],
    description="EMA Heikin Ashi Trading Strategy",
    author=version['__author__'],
    author_email="your.email@example.com",
    url="https://github.com/yourusername/ema-ha-strategy",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ema-ha-strategy=main:main",
        ],
    },
)
