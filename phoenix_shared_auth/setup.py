"""
🚀 Phoenix Shared Auth - Setup Configuration
Module d'authentification unifiée pour l'écosystème Phoenix
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="phoenix-shared-auth",
    version="1.0.0",
    author="Phoenix Ecosystem",
    author_email="dev@phoenix-ecosystem.com",
    description="Module d'authentification unifiée pour l'écosystème Phoenix",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phoenix-ecosystem/phoenix-shared-auth",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
