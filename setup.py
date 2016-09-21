from setuptools import setup, find_packages

setup(
    name="cron_parser",
    version="0.0.1",
    author="Gus Chadney",
    author_email="angus.chadney@gmail.com",
    description=("Cron parser"),
    packages=find_packages(exclude=['tests', 'tests.*']),
    scripts=['bin/cron-parser'],
)
