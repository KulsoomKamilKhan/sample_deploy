from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='Price',
    version='1.0',
    install_requires=requirements,
)
