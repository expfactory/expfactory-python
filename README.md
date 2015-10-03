#Psi-turkey-py

Python module for managing [psiturk javascript experiment files](https://github.com/psiturk/psiturk-experiments), a [psiturk battery](https://github.com/psiturk/psiturk-battery), and a psiturk [virtual machine](https://github.com/psiturk/psiturk-vm) to host the compilation of those two things.  

### Functions Needed

###### experiment.py

- 
- validator for experiment format (json, etc) to add a new experiment
- instructions for how to add a new experiment

###### battery.py

- functions to select a subset of experiments and generate a battery to run with psiturk

###### vm.py

- functions for generating a new vm instance
   - should use functions from battery.py to select, create output, plug into vm, deploy

###### analysis.py

- functions to do analyses, probably using db.py

###### db.py

- functions for extracting stuff / working with database(s)
