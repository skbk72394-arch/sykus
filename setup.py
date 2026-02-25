#!/usr/bin/env python3
"""
Sykus Setup Script
"""

from setuptools import setup, find_packages

setup(
    name='sykus',
    version='3.0.0',
    description='The World\'s Most Frustration-Free Programming Language',
    author='Sykus Team',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'syk=cli.syk_cli:main',
        ],
    },
    install_requires=[
        'colorama>=0.4.4',
    ],
    python_requires='>=3.8',
)
