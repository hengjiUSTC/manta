from setuptools import find_packages, setup

setup(
    name="code-manta",
    version="0.1.0",
    author="Heng Ji",
    author_email="jihengcu@gmail.com",
    description="A Python library for Code Agent Manta",
    packages=find_packages(include=["code_manta", "code_manta.*", "tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "requests>=2.26.0",
        "dataclasses>=0.8;python_version<'3.7'",
        "prompt_toolkit>=3.0.0",
        "typing-extensions>=4.0.0",
        "openai>=1.60.0",
        "pytest>=8.0.0",
        "unidiff>=0.7.0",
        "tiktoken>=0.8.0",
        "rich>=13.0.0",
    ],
    entry_points={"console_scripts": ["code-manta=code_manta.__main__:main"]},
    extras_require={
        "dev": [
            "black",
            "isort",
            "flake8",
            "mypy",
            "pytest",
            "pre_commit",
        ]
    },
    test_suite="unittest.discover",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
