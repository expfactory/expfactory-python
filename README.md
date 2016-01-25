# The Experiment Factory Python

[![Circle CI](https://circleci.com/gh/expfactory/expfactory-python.svg?style=svg)](https://circleci.com/gh/expfactory/expfactory-python)

Python module for managing [experiment factory javascript experiment files](https://github.com/expfactory/expfactory-experiments), a [psiturk battery](https://github.com/expfactory/expfactory-battery), and a [virtual machine](https://github.com/expfactory/expfactory-vm) to host the compilation of these things.  We currently have support for just psiturk batteries, and other integrations will come shortly. You can use the functions to control these components, or just install the module and run to create an entire experiment using a web interface.

Please see our [documentation](http://expfactory.github.io/) for more complete details.

### Installation (current)

      pip install expfactory

### Installation (dev)

      pip install git+git://github.com/expfactory/expfactory-python.git


### Quick start
Installation will place an executable, `expfactory` in your bin folder. To run the executable to open up a web interface to design your experiment:

      expfactory

The web interface includes the following:

- custom generation of battery (local folder, AWS virtual machine, or virtual machine)
- serves API (JSON) with experiment details
- complete documentation


#### Run a local experiment
You can run an [expfactory-experiments](expfactory-experiments) folder as follows:

      cd test_task
      expfactory --run


#### Validate a local experiment

      cd test_task
      expfactory --validate


#### Test with experiment robot

      cd test_task
      expfactory --test


### Functions Provided
You can also use the library as a module, and import expfactory functions into your application.  Please see our [documentation](http://expfactory.github.io) for details
