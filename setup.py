#!/usr/bin/python

from setuptools import find_packages, setup

from pmcf.version import VERSION

setup(
    name="pmcf",
    version=VERSION,
    description="Piksel Managed Cloud Framework",
    author="Stephen Gran",
    author_email="stephen.gran@piksel.com",
    url="http://www.piksel.com",
    packages=find_packages('.', exclude=['tests*']),
    test_suite="nose.collector",
    install_requires=[
        "awacs",
        "argparse",
        "boto",
        "jsonschema",
        "PyYAML",
        "netaddr",
        "troposphere",
        "xmltodict",
    ],
    tests_require=[
        "cov-core",
        "coverage",
        "flake8",
        "mock",
        "nose",
        "nose-cov",
        "pep8",
        "Sphinx",
        "tox",
    ],
    entry_points={
        'console_scripts': [
            'pmcf = pmcf.cli.cli:main',
        ],
    },
)
