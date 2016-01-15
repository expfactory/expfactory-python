'''
tests.py: part of expfactory package
tests for experiments and batteries, not for expfactory-python

'''
from expfactory.utils import find_directories
from expfactory.experiment import validate
from numpy.testing import assert_equal

def validate_experiment_directories(experiment_folder):
    experiments = find_directories(experiment_folder)
    for contender in experiment:
        assert_equal(validate(contender),True)
