from setuptools import setup, find_packages

setup(
    # Application name:
    name="psiturkpy",

    # Version number (initial):
    version="0.0.1",

    # Application author details:
    author="poldracklab",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Details
    url="http://www.github.com/psiturk",

    license="LICENSE.txt",
    description="Python module for managing psiturk javascript experiment files, a psiturk battery, and a psiturk virtual machine to host the compilation of those two things.",

    install_requires = ['numpy']
)
