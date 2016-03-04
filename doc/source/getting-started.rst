Getting Started
===============

I want to generate a custom battery
-----------------------------------

First you should follow instructions for `installation <http://expfactory.readthedocs.org/en/latest/installation.html>`_. The Experiment Factory provides several options for deploying a battery, running one or more experiments locally, or generating a static battery to run on your own web server. A battery of experiments is a selection of experimental paradigms that are presented in sequence. We have made it easy to select one or more experiments from http://www.github.com/expfactory/expfactory-experiments, plug them into a `expfactory battery <http://www.github.com/expfactory/expfactory-battery>`_, and deploy.  What are your deployment options? You can run a battery on demand using the command line tool, generate a custom folder to run later, or deploy a more substantial infrastructure, including `vagrant virtual machines <http://www.github.com/expfactory/expfactory-vm>`_, a `docker-based infrastructure <http://www.github.com/expfactory/expfactory-docker>`_.


Local Deployment of Experiments
'''''''''''''''''''''''''''''''
A local deployment means running one or more experiments on a local machine, such as your computer or a lab machine. The simplest thing you can do is install the expfactory tool, and then run a battery of experiments:

::

      expfactory --run --experiments stroop,nback

This command will use the latest experiments in the repo. If you want to ensure that your experiments do not change, or if you will be running the experiments without an internet connection, or if you want to modify experiments for your need, we recommend cloning the experiments repo, and specifying it as an argument to the command:

::

      git clone http://www.github.com/expfactory/expfactory-experiments
      expfactory --run --experiments stroop,nback --folder expfactory-experiments



You can do the same for a battery folder:

::

      git clone http://www.github.com/expfactory/expfactory-experiments
      expfactory --run --experiments stroop,nback --battery expfactory-battery

For each of the above, this will open up your browser to run the experiments, and data is stored to your computer via a csv file downloaded in the browser. You might want to specify a participant id to customize the naming of the output data, and to embed the id in the data itself:


::

      git clone http://www.github.com/expfactory/expfactory-experiments
      expfactory --run --experiments stroop,nback --subid DNS001



Generation of Local Battery
'''''''''''''''''''''''''''
If you want to generate a custom folder and run it later, you can use the expfactory command line "--generate" command. This situation is ideal for generating your own static HTML/CSS files to put on your own web server. We recommend our Windows users to do this in some Linux environment (if your university has a shared cluster or on a Virtual Machine) and then to move the battery folder back onto the Windows Machine. To generate a battery folder:

::

      expfactory --generate --experiments stroop,nback


Or to generate a Psiturk battery folder:

::

      expfactory --generate --experiments stroop,nback --psiturk

If you don't specify an output folder, a temporary directory will be created. For each of the above, you can specify the --output command, a full path to a folder (that does not exist) that you want the battery generated in.



Expfactory Portal
.................
If you are a Linux or Unix-based user and want to dynamically generate a custom battery for Psiturk (called a "folder" deployment), or a Virtual Machine with Vagrant, you can do so with the command line tool: 

:: 

      expfactory


Which will open up a view in your browser. You can then click "battery." The web interface will take you through the following steps:

* A. collection of experiment details
* B. database connection parameters
* C. selection of local (folder) experiment, or deployment to AWS.
* D. selection of experiments

More `details are provided <http://expfactory.readthedocs.org/en/latest/deployment.html>`_ about choosing a deployment, and configuring your battery.


Expfactory-docker
.................
The Experiment Factory docker is a set of containers that can be run locally, or again on the cloud. The entire application comes packaged in a set of Docker images, meaning that installation and deployment of experiments happens in a web interface deployed by Docker Compose. We plan to offer experiment deployment as a service at `expfactory.org <http://www.expfactory.org>`_ and encourage you to `sign up <http://www.expfactory.org/signup>`_ to express interest. You can also `deploy our Docker infrastructure <http://www.expfactory.org/signup>`_ on your own server, however experience with docker and cloud computing is required.


I want to preview available experiments
---------------------------------------

We provide static versions of all experiments, along with meta-data, in our `expfactory-experiments <http://expfactory.github.io/>`_ github pages. You can preview the currently available experiments in our `online portal <http://expfactory.github.io/experiments.html>`_. You can generate this portal on the fly on your local machine as well:

::

      from expfactory.views import generate_experiment_web
      output_folder = os.path.abspath("/home/vanessa/Desktop/web")
      generate_experiment_web(output_folder)


The output folder does not need to exist. This will generate the equivalent interface hosted on expfactory.github.io.


I want to contribute an experiment
----------------------------------

The short story is that all of the experiments that can be selected are just folders on Github, http://www.github.com/expfactory/expfactory-experiments, and you can contribute by modifying an existing experiment or creating a new one by submitting a PR to this repository. For complete details about experiment contributions, please see our `development <http://expfactory.readthedocs.org/en/latest/development.html?highlight=contributing#contributing-to-experiments>`_ pages. 


I want to learn about the expfactory-python functions
-----------------------------------------------------

The generation of the batteries, along with experiment validation, and virtual machine deployment, are controlled by the expfactory-python functions. You can see complete function documentation under :ref:`modindex`, and we welcome any contributions to the code base via Github pull requests (PRs) or `isses <http://www.github.com/expfactory/expfactory-python/issues>`_. We provide a few examples below of running tests and generating visualizations.

Run the experiment testing robot
''''''''''''''''''''''''''''''''

::

      expfactory --test


Validate an experiment folder
'''''''''''''''''''''''''''''

::

      expfactory --validate


Preview a single experiment
'''''''''''''''''''''''''''

::

      expfactory --preview


Generate the entire expfactory.github.io interface
''''''''''''''''''''''''''''''''''''''''''''''''''

::
      
      from expfactory.views import generate_experiment_web
      web_folder = '/home/vanessa/Desktop/site'
      generate_experiment_web(web_folder) 


You can then run an experiment robot over experiments in this folder, either for all experiments:

::

      experiment_robot_web(web_folder)

or a subset of experiments

::

      experiment_robot_web(web_folder,experiment_tags=changed_experiments)


Checking static javascript with jshint
''''''''''''''''''''''''''''''''''''''
We recommend using the docker image to do this, across many experiment directories at once:

::

      docker pull hyzual/jshint
      cd expfactory-experiments
      sudo docker run -it -v $(pwd):/lint hyzual/jshint --config /lint/.jshint_config .


Validate an entire set of experiment directories
''''''''''''''''''''''''''''''''''''''''''''''''

::

    from expfactory.tests import validate_experiment_directories, validate_experiment_tag
    validate_experiment_directories('expfactory-experiments')
    validate_experiment_tag('expfactory-experiments')


