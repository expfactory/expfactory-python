# The Experiment Factory Python

[![Circle CI](https://circleci.com/gh/expfactory/expfactory-python.svg?style=svg)](https://circleci.com/gh/expfactory/expfactory-python)

The Experiment Factory Python is a module for managing reproducible experiments. The previous version focused on a template approach for [experiments](https://github.com/expfactory/expfactory-experiments), [surveys](https://github.com/expfactory/expfactory-surveys), and [games](https://github.com/expfactory/expfactory-games), and this version is agnostic to the underlying driver of the experiments, and provides reproducible, instantly deployable "container" experiments. What does that mean?

 - You obtain (or build from scratch) one container, a battery of experiments.
 - The container is a Singularity container, meaning that it's a file that can be easily moved, and shared.
 - You run the container with (optionally) some subset and ordering of your battery.
 
The means that the minimum requirement of an experiment is:

 - an `index.html` file and `config.json` in the root of the folder.
 - (optional) documentation about any special variables that can be set in the Singularity build recipe environment section for it (more on this later).
 - an associated repository to clone from, (optionally) registered in the library.

- Please see our [documentation](http://expfactory.readthedocs.org/en/latest/getting-started.html) for more complete details.
- Jump in and [try out our experiments](http://expfactory.github.io/table.html)
- Express interest in Experiments as a Service (EaS) as [expfactory.org](http://www.expfactory.org)

The Experiment Factory code is licensed under the MIT open source license, which is a highly permissive license that places few limits upon reuse. This ensures that the code will be usable by the greatest number of researchers, in both academia and industry. 



### Quick start

You don't actually need to install the Software on your local machine, it will be installed into a container where your experiments live.


```
git clone -b development git+git://github.com/expfactory/expfactory-python.git

```


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
