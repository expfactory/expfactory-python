from efactory.experiment import validate
from efactory.utils import find_directories

myexperiments = find_directories("../efactory-experiments")

for experiment in myexperiments:
    if not validate(experiment):
        print experiment
