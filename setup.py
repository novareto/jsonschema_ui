from setuptools import setup


setup(
    name='jsonschema_ui',
    install_requires=[
        "pydantic" >= "2",
    ],
    extras_require={
        'test': [
            'pytest>=3',
            'PyHamcrest'
        ]
    }
)
