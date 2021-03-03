from setuptools import setup, find_packages

setup(
    name='whatsapp',
    version='0.1.0',
    packages=find_packages(include=['whatsapp', 'whatsapp.*'])
)
