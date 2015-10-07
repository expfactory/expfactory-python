from psiturkpy.experiment import validate
from psiturkpy.utils import find_directories

myexperiments = find_directories("../psiturk-experiments")

for experiment in myexperiments:
    if not validate(experiment):
        print experiment

#Problem reading psiturk.json, Expecting , delimiter: line 6 column 17 (char 105)
#/home/vanessa/Documents/Dropbox/Code/psiturk/psiturk-experiments/go-nogo
#Problem reading psiturk.json, No JSON object could be decoded
#/home/vanessa/Documents/Dropbox/Code/psiturk/psiturk-experiments/tone-monitoring
#Problem reading psiturk.json, No JSON object could be decoded
#/home/vanessa/Documents/Dropbox/Code/psiturk/psiturk-experiments/stroop
