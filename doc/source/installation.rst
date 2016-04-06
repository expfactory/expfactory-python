Installation
============

Installation of the Experiment Factory Software requires some familiarity with the command line, as the software is based in python. "`Pip <https://en.wikipedia.org/wiki/Pip_(package_manager)>`_" is a package management system for python, and you can use pip to install our software, expfactory-python, which is the controller of all pieces of this infrastructure. If you want to install the development version, you can install directly from Github with this command:

::

      pip install git+git://github.com/expfactory/expfactory-python.git




Or to install the current release, use this command:


::


     pip install expfactory
 


Please note that expfactory was developed with python 2.7 and has not been tested on other versions. Installation will place an executable, `expfactory` in your bin folder. You should be able to type `which expfactory` and see the location of your application. If you cannot, you likely installed the application locally, and the executable was placed in a folder not on your path. You can either try installation with sudo, or look at the output of the installation to find the path that it was installed to:

::

      Installing expfactory script to /usr/local/bin



You can also use the module as a standard python module, meaning importing functions into scripts, for example:

::

     from expfactory.battery import generate





Quickstart
----------

Running Experiments
'''''''''''''''''''

Deploy a battery of experiments, a game, or a survey on your local machine

:: 

      expfactory --run --experiments stroop,nback
      expfactory --run --survey bis11_survey
      expfactory --run --game bridge_game



Developing Experiments
''''''''''''''''''''''

To run (or preview) a folder (experiment) you are working on, you can cd into that folder, and use the `--run` command:


::

      cd my_experiment
      expfactory --run


You can also specify the folder as an argument:

::

      expfactory --run --folder /home/vanessa/Desktop/my_experiment
      


Validate the configuration file (config.json) for your experiment

:: 

      cd my_experiment
      expfactory --validate


Test your experiment with our experiment robot

:: 

      cd my_experiment
      expfactory --test



Run the executable to open up a web interface to generate psiturk battery or virtual machine.


::

      expfactory



You can also specify a port:


::

      expfactory --port=8088


.. image:: _static/img/api/webinterface.png
