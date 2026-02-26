#!/usr/bin/env python3
"""
Sykus Setup Script
"""

from setuptools import setup, find_packages

setup(
    name='sykus',
    version='5.0.0',
    description='The World\'s Most Frustration-Free Programming Language',
    author='Sykus Team',
    packages=find_packages(),
    py_modules=['lexer', 'parser', 'evaluator', 'environment', 'stdlib', 'syk_ast', 'main'],
    entry_points={
        'console_scripts': [
            'syk=main:main',
        ],
    },
    install_requires=[
        'colorama>=0.4.4',
    ],
    python_requires='>=3.8',
)
