Getting Started
===============

I want to generate a custom battery
-----------------------------------

The Experiment Factory provides several options for deploying a battery, or running a experiment locally.  After `installation <http://expfactory.readthedocs.org/en/latest/installation.html>`_ you can generate a battery locally or on a server. A battery of experiments is a selection of experimental paradigms that are presented in sequence. We have made it easy to select one or more experiments from http://www.github.com/expfactory/expfactory-experiments, merge them into a `expfactory battery <http://www.github.com/expfactory/expfactory-battery>`_, and deploy via a `vagrant virtual machine <http://www.github.com/expfactory/expfactory-vm>`_, a set of `docker images <http://www.github.com/expfactory/expfactory-docker>`_, or just run locally.


Local Deployment - Single Experiment
''''''''''''''''''''''''''''''''''''
A local deployment means running one or more experiments on a local machine, such as your computer or a lab machine. The simplest thing you can do is to clone the `expfactory-experiments repo <http://www.github.com/expfactory/expfactory-experiments>`_, cd into a folder, and use the expfactory command line tool to start the experiment:

::

      git clone http://www.github.com/expfactory/expfactory-experiments
      cd test_task
      expfactory --run


This will open up your browser to run the task, and data is stored to your computer via a csv file with the naming convention {{exp_id}}_experiment_results.csv, where "exp_id" corresponds with the experiment id, such as "test_task." You could run a simple battery by running this command for a participant, and then moving the downloaded folder to a location of choice, and renaming.



Local Deployment - Many Experiments
'''''''''''''''''''''''''''''''''''
It is more typical to want to deploy many experiments at once, what we call a "battery" of experiments, and to do this the Experiment Factory gives you two options: using psiturk, or using the Experiment Factory application, which uses Docker containers. Each option can be run locally, or on the cloud.


Psiturk
.......
You can generate a custom psiturk battery on your local machine (called a "folder" deployment, on your virtual machine on your local machine (we call this "vagrant"), or the equivalent psiturk battery on a virtual machine on Amazon web services (we call this "aws"). Plugging the experiments into a psiturk battery means that you can run the battery locally, or after signing up with psiturk, on Amazon Mechanical Turk. For any of these three options, you can again use the command line tool:

:: 

      expfactory


Which will open up a view in your browser. You can then click "battery." The web interface will take you through the following steps:

* A. collection of experiment details
* B. database connection parameters
* C. selection of local (folder) experiment, or deployment to AWS.
* D. selection of experiments

More `details are provided <http://expfactory.readthedocs.org/en/latest/deployment.rst>_` about choosing a deployment, and configuring your battery.


Expfactory-docker
.................
The Experiment Factory docker is a set of containers that can be run locally, or again on the cloud. The entire application comes packaged in a Docker image, meaning that installation and deployment of experiments happens in a web interface deployed by the image. We are still testing and finalizing these images, and will update this docuementation with instructions shortly.




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

The short story is that all of the experiments that can be selected are just folders on github, http://www.github.com/expfactory/expfactory-experiments, and you can contribute by modifying an existing experiment or creating a new one by submitting a PR to this repository. For complete details about experiment contributions, please see our `development <http://expfactory.readthedocs.org/en/latest/development.html?highlight=contributing#contributing-to-experiments>`_ pages. 


I want to learn about the expfactory-python functions
-----------------------------------------------------

The generation of the batteries, along with experiment validation, and virtual machine deployment, are controlled by the expfactory-python functions. You can see complete function documentation under :ref:`modindex`, and we welcome any contributions to the code base via Github pull requests (PRs) or `isses <http://www.github.com/expfactory/expfactory-python/issues>`_. We provide a few examples below of running tests and generating visualizations.

Run the experiment testing robot
''''''''''''''''''''''''''''''''

::

      cd test_task
      expfactory --test


Validate an experiment folder
'''''''''''''''''''''''''''''

::

      cd test_task
      expfactory --validate

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


