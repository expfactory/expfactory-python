#Psi-turkey-py

Python module for managing [psiturk javascript experiment files](https://github.com/psiturk/psiturk-experiments), a [psiturk battery](https://github.com/psiturk/psiturk-battery), and a psiturk [virtual machine](https://github.com/psiturk/psiturk-vm) to host the compilation of those two things.  You can use the functions to control these psiturk components, or just install the module and run to create an entire experiment using a web interface.

Please see our [documentation](http://psiturk.github.io/psiturk-python) for more complete details.

### Installation

      pip install git+git://github.com/psiturk/psiturk-python.git


### Running to Generate a Battery
Installation will place an executable, `psyturkpy` in your bin folder. To run the executable to open up a web interface to design your experiment:

      psiturkpy

The web interface will take you through the following steps:

- collection of experiment details
- database connection validation
- creation of local (folder) experiment, or deployment to AWS.

### Functions Provided
If you want to use the library as a module, functions are provided that do the following.

###### experiment.py

- validator for experiment format (json, etc) to add a new experiment
- command line generation of new experiments

###### battery.py

- functions to select a subset of experiments and generate a battery to run with psiturk

###### vm.py

- functions for generating a new vm instance
- should use functions from battery.py to select, create output, plug into vm, deploy

###### analysis.py

- functions to do analyses, probably using db.py

###### db.py

- functions for extracting stuff / working with database(s)
