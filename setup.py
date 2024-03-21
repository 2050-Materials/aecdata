from setuptools import setup, find_packages

setup(
    name="materials_2050_api_client",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",  # Add your dependencies here
        "numpy",
        "pandas",
    ],
)
