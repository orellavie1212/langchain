import io
import os
import re
import subprocess
from typing import List, Set

import setuptools

ROOT_DIR = os.path.dirname(__file__)

def get_path(*filepath) -> str:
    return os.path.join(ROOT_DIR, *filepath)


def find_version(filepath: str):
    """Extract version information from the given filepath.

    Adapted from https://github.com/ray-project/ray/blob/0b190ee1160eeca9796bc091e07eaebf4c85b511/python/setup.py
    """
    with open(filepath) as fp:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  fp.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


def read_readme() -> str:
    """Read the README file."""
    return io.open(get_path("README.md"), "r", encoding="utf-8").read()


def get_requirements() -> List[str]:
    """Get Python package dependencies from requirements.txt."""
    with open(get_path("requirements.txt")) as f:
        requirements = f.read().strip().split("\n")
    return requirements


setuptools.setup(
    name="langchain",
    version="0.0.305", #find_version("langchain", get_path("__init__.py")),
    author="Orel Team",
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
    ],
    packages=setuptools.find_packages(exclude=("benchmarks", "csrc", "docs",
                                               "examples", "tests")),
    python_requires=">=3.8",
    install_requires=get_requirements(),
    package_data={'langchain': ['chains/llm_summarization_checker/prompts/*.txt',
                               'llms/grammars/*.gbnf']},

)
