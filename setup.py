from setuptools import setup, find_packages

setup(
    name="danotes",
    version="0.1.0",
    description="CLI for managing .dan format notes",
    author="Your Name",
    author_email="your@email.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyfiglet>=1.0.3",
        "pyyaml>=6.0"
        ],
    entry_points={
        "console_scripts": [
            "danotes=danotes.cli:main",
        ]
    },
    python_requires=">=3.8",
)
