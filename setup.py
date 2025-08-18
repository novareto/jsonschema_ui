import tomllib
from pathlib import Path
from setuptools import setup, find_packages

# Read pyproject.toml
pyproject_path = Path(__file__).parent / "pyproject.toml"
with open(pyproject_path, "rb") as f:
    pyproject_data = tomllib.load(f)

project_config = pyproject_data["project"]

# Extract project metadata
name = project_config["name"]
version = project_config["version"]
description = project_config["description"]
authors = project_config["authors"]
author_names = [author["name"] for author in authors]
author_emails = [author["email"] for author in authors]
requires_python = project_config["requires-python"]
dependencies = project_config["dependencies"]

# Handle optional dependencies
extras_require = project_config.get("optional-dependencies", {})

# Read README if it exists
readme_file = project_config.get("readme", "README.rst")
readme_path = Path(__file__).parent / readme_file
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/x-rst" if readme_file.endswith(".rst") else "text/markdown",
    author=", ".join(author_names),
    author_email=", ".join(author_emails),
    python_requires=requires_python,
    install_requires=dependencies,
    extras_require=extras_require,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)