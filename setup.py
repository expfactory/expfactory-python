from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Application name:
    name="psiturkpy",

    # Version number (initial):
    version="1.0.0",

    # Application author details:
    author="poldracklab",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data files
    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/psiturk",

    license="LICENSE.txt",
    description="Python module for managing psiturk javascript experiment files, a psiturk battery, and a psiturk virtual machine to host the compilation of those two things.",
    long_description=long_description,
    keywords='psiturk behavior neuroscience',

    install_requires = ['numpy','Flask'],

    entry_points = {
        'console_scripts': [
            'psiturkpy=psiturkpy.interface:main',
        ],
    },

)
