from setuptools import setup, find_packages

setup(
    name="phoenix_shared_auth",
    version="1.0.0",
    description="Phoenix Shared Authentication System",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.30.0",
        "supabase>=2.0.0",
        "pydantic>=2.5.0",
        "cryptography>=41.0.0",
        "requests>=2.31.0",
        "python-dateutil>=2.8.2",
    ],
    python_requires=">=3.8",
)