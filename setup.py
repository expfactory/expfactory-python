from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Application name:
    name="expfactory",

    # Version number (initial):
    version="1.0.1",

    # Application author details:
    author="poldracklab",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data files
    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/expfactory",

    license="LICENSE.txt",
    description="Python module for managing experiment factory javascript experiment files, a psiturk battery, and virtual machines to host the compilation of these things.",
    long_description=long_description,
    keywords='psiturk behavior neuroscience experiment factory',

    install_requires = ['numpy','Flask','gitpython'],

    entry_points = {
        'console_scripts': [
            'expfactory=expfactory.scripts:main',
        ],
    },

)
