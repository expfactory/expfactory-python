from expfactory.experiment import validate
from expfactory.utils import find_directories

myexperiments = find_directories("../expfactory-experiments")

for experiment in myexperiments:
    if not validate(experiment):
        print experiment
