from setuptools import setup, find_packages

setup(
    name="aecdata",
    version="0.1",
    author="2050 Materials",
    author_email="nicodemos@2050-materials.com",
    description="aecdata is a Python library designed to simplify access to the 2050-materials API",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/2050-Materials/aecdata",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests>=2.31.0",
        "numpy>=1.26.4",
        "pandas>=2.2.1",
        "matplotlib>=3.8.3",
        "pyarrow>=3.0.0",
    ]
)
