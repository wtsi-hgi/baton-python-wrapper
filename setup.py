from setuptools import setup, find_packages

setup(
    name="baton-python-wrapper",

    version="0.1.0",

    author="Colin Nolan",
    author_email="hgi@sanger.ac.uk",

    packages=find_packages(exclude=["test"]),

    url="https://github.com/wtsi-hgi/baton-python-wrapper",

    license="LICENSE",

    description="Python wrapper for baton.",
    long_description=open("README.md").read(),

    install_requires=[x for x in open("requirements.txt").read().splitlines() if "://" not in x],
    dependency_links=[x for x in open("requirements.txt").read().splitlines() if "://" in x],

    test_suite="baton.tests"
)
