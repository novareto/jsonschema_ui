from setuptools import setup, find_packages

setup(
    name="jsonschema_ui",
    version="0.1.0",
    description="JSONSchema UI extraction",
    author="Christian Klinger",
    author_email="ck@novareto.de",
    python_requires=">=3.11",
    install_requires=["pydantic >= 2", "colander", "deform"],
    extras_require={
        "test": [
            "pytest",
            "PyHamcrest",
        ],
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)
