from setuptools import setup, find_packages

setup(
    name="jsonschema_ui",
    install_requires=["pydantic >= 2", "colander", "deform"],
    extras_require={
        "test": [
            "pytest",
            "PyHamcrest",
        ],
    },
)
