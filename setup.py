#!/usr/bin/python

from setuptools import find_packages, setup

from pmcf.version import VERSION

req_lines = [line.strip() for line in open('requirements.txt').readlines()]
install_reqs = list(filter(None, req_lines))

t_lines = [line.strip() for line in open('test-requirements.txt').readlines()]
test_reqs = list(filter(None, t_lines))

setup(
    name="pmcf",
    version=VERSION,
    description="Piksel Managed Cloud Framework",
    author="Stephen Gran",
    author_email="stephen.gran@piksel.com",
    url="http://www.piksel.com",
    packages=find_packages('.', exclude=['tests*']),
    test_suite="nose.collector",
    install_requires=install_reqs,
    tests_require=test_reqs,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pmcf = pmcf.cli.cli:main',
        ],
    },
)
