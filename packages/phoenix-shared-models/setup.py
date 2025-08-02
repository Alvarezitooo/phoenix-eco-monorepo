# phoenix_shared_models/setup.py
from setuptools import find_packages, setup

setup(
    name="phoenix_shared_models",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["pydantic"],
)
