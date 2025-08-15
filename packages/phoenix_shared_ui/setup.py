"""
Setup script pour Phoenix Shared UI
"""

from setuptools import setup, find_packages

setup(
    name="phoenix-shared-ui",
    version="1.0.0",
    description="Composants UI partagés pour l'écosystème Phoenix",
    author="Claude Phoenix DevSecOps Guardian",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.30.0",
    ],
    python_requires=">=3.11",
    package_data={
        "phoenix_shared_ui": ["*.css"],
    },
    include_package_data=True,
)