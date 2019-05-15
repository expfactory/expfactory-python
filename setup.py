from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

setup(
    # Application name:
    name="expfactory",

    # Version number (initial):
    version="2.5.47",

    # Application author details:
    author="Vanessa Sochat",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data files
    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/expfactory",

    license="LICENSE",
    description="Python module for managing experiment factory experiments, for deployment to a psiturk battery or docker container.",
    keywords='psiturk behavior neuroscience experiment factory docker',

    install_requires = ['requests','Flask>=1.0.2','gitpython','Flask-RESTful==0.3.6','selenium>=2.53.6','cognitiveatlas>=0.1.9'],

    entry_points = {
        'console_scripts': [
            'expfactory=expfactory.scripts:main',
        ],
    },

)
