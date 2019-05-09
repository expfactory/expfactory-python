# The Experiment Factory Python

[![Circle CI](https://circleci.com/gh/expfactory/expfactory-python.svg?style=svg)](https://circleci.com/gh/expfactory/expfactory-python)

**LEGACY** This repository is no longer actively maintained, and exists to support current implementations. We encourage users to create reproducible experiment containers with the redone [expfactory](https://expfactory.github.io) software.

Python module for managing expriment-factory [experiments](https://github.com/expfactory/expfactory-experiments), [surveys](https://github.com/expfactory/expfactory-surveys), [games](https://github.com/expfactory/expfactory-games), a [psiturk battery](https://github.com/expfactory/expfactory-battery), a [docker deployment](https://github.com/expfactory/expfactory-docker), and a [virtual machine](https://github.com/expfactory/expfactory-vm) to host the compilation of these things. You can use the functions to control these components, or just install the module and run to create an entire experiment using a web interface.

- Please see our [documentation](http://expfactory.readthedocs.org/en/latest/getting-started.html) for more complete details.
- Jump in and [try out our experiments](http://expfactory.github.io/table.html)
- Express interest in Experiments as a Service (EaS) as [expfactory.org](http://www.expfactory.org)

The Experiment Factory code is licensed under the MIT open source license, which is a highly permissive license that places few limits upon reuse. This ensures that the code will be usable by the greatest number of researchers, in both academia and industry. 

### Installation (current)

```bash
# python 3
pip install expfactory==2.5.47

# python 2
pip install expfactory==2.5.46

# version 2 (non legacy)
pip install expfactory
```

### Quick start

Installation will place an executable, `expfactory` in your bin folder. 


#### Run your local experiment
You can run an [expfactory-experiments](expfactory-experiments) folder as follows:

      cd test_task
      expfactory --preview


#### Run paradigms locally

      expfactory --run --experiments stroop,n_back
      expfactory --run --survey bis11_survey
      expfactory --run --game bridge_game


#### Validate a local experiment

      cd test_task
      expfactory --validate


#### Test with experiment robot

      cd test_task
      expfactory --test


#### Interactive generation of psiturk battery

To run the executable to open up a web interface to design your experiment:

      expfactory

The web interface includes the following:

- custom generation of battery (local folder, AWS virtual machine, or virtual machine)
- serves API (JSON) with experiment details
- complete documentation


#### Static deployment with your own mysql database
We have recently added support for generating a local battery that will work with your own mysql database. See [server/mysql](server/mysql) for details.


### Functions Provided
You can also use the library as a module, and import expfactory functions into your application.  Please see our [documentation](http://expfactory.readthedocs.org/en/latest/getting-started.html) for details
