from setuptools import setup, find_packages

setup(
    name="aecdata",
    version="0.0.7",
    author="2050 Materials",
    license="Apache License 2.0",
    author_email="nicodemos@2050-materials.com",
    description="A Python library designed to simplify access to the 2050-materials API",
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
        "requests",
        "numpy",
        "pandas",
        "pyarrow",
    ]
)
