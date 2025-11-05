"""
Setup file for shared library package.

This allows the shared library to be installed as a package
so it can be imported by all microservices.
"""

from setuptools import setup, find_packages

setup(
    name="realtoros-shared",
    version="1.0.0",
    description="Shared library for RealtorOS microservices",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "pydantic[email]>=2.5.3",
        "sqlalchemy>=2.0.23",
        "asyncpg>=0.29.0",
        "python-jose[cryptography]>=3.3.0",
        "bcrypt>=4.0.0",
        "pyjwt>=2.8.0",
    ],
)

