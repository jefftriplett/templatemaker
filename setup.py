#!/usr/bin/env python3

from setuptools import setup

setup(
    name="templatemaker",
    version="0.1.0",
    description="Given text examples in a similar format, templatemaker creates templates to extract data",
    long_description=open("README.TXT").read(),
    author="Adrian Holovaty",
    author_email="adrian@holovaty.com",
    py_modules=["templatemaker"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Text Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
