#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for Blu-ray Menu Player
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bluray-player",
    version="1.0.0",
    author="PageSecOnd",
    description="A Python application to play Blu-ray disc menus directly on Windows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PageSecOnd/bluray",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Video :: Display",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bluray-player=bluray_player:main",
        ],
    },
)