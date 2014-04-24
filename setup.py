from setuptools import find_packages, setup

setup(
    name="pmcf",
    version="2014.1",
    description="Piksel Managed Cloud Framework",
    author="Stephen Gran",
    author_email="stephen.gran@piksel.com",
    url="http://www.piksel.com",
    packages=find_packages('.', exclude=['tests*']),
    test_suite="nose.collector",
)
