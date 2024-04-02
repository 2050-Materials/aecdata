from setuptools import setup, find_packages

setup(
    name="aecdata",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",  # Add your dependencies here
        "numpy",
        "pandas",
        "matplotlib",
    ],
)
