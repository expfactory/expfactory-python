About
=====

The Experiment Factory is developed by the `Poldracklab <http://poldracklab.stanford.edu>`_ at Stanford University, and all code is publicly available on `Github <http://www.github.com/expfactory>`_. The current landscape of behavioral paradigms is messy at best, and so the Experiment Factory is an effort to standardize, organize, and collaboratively develop experiments that can be run on multiple infrastructures. Currently supported is generating experiments in a battery intended to run with `psiturk <https://github.com/NYUCCL/>`_ on a local computer, a vagrant virtual machine, or Amazon Web Services. We intend to add support for docker and other web applications soon, and welcome your contributions to `experiments <http://www.github.com/expfactory/expfactory-experiments>`_, `surveys <http://www.github.com/expfactory/expfactory-surveys>`_,  and `games <http://www.github.com/expfactory/expfactory-experiments>`_, along with the infrastructure for `psiturk battery generation <http://www.github.com/expfactory/expfactory-battery>`_, `virtual machines <http://www.github.com/expfactory/expfactory-vm>`_, and the `software itself <http://www.github.com/expfactory/expfactory-python>`_.

We are called the Experiment Factory because we want the software to support flexibility in designing the experiments, infrastructure, and deployment for your experiments.  Psychology and neuroscience researchers should have the same modern tools available to them as a commercial effort, and long gone should be the days of passing around paradigms from computer to computer on USB sticks. If we work together we can refine experiments to make them better, and making behavioral measurments with the same thing is one step toward a vision of reproducible science.

License
-------
The Experiment Factory code is licensed under the MIT open source license, which is a highly permissive license that places few limits upon reuse. This ensures that the code will be usable by the greatest number of researchers, in both academia and industry. 


Citation
--------
Please cite `the Experiment Factory paper <http://journal.frontiersin.org/article/10.3389/fpsyg.2016.00610/abstract>`_ if you use it in your work:

::

Sochat VV, Eisenberg IW, Enkavi AZ, Li J, Bissett PG and Poldrack RA (2016). The Experiment Factory: standardizing behavioral experiments. Front. Psychol. 7:610. doi: 10.3389/fpsyg.2016.00610



Integrations and Tools
----------------------

Psiturk
'''''''
These experiments are intended to run via the `psiturk infrastructure <https://github.com/NYUCCL/psiTurk>`_, and the `experiment factory battery <http://www.github.com/expfactory/expfactory-battery>`_ is the main experiment code that, when fit with `experiments <http://www.github.com/expfactory/expfactory-experiments>`_, can run on Amazon Mechanical Turk.

Phaser
''''''
We are collaborating with the `Stanford Cognitive and Systems Neuroscience Lab <http://scsnl.stanford.edu/>`_ to make simple, fun HTML event driven games that are integrated into the Experiment Factory frameowrk. This work is in its infancy, and it's going to be fun to see where we take it!


Material Design Lite
''''''''''''''''''''
We use `Google Material Design Lite <http://getmdl.io>`_ as our template for forms, as it offers a beautiful user experience, and have implemented a basic validation for it and pagination using JQuery Wizard.


JsPsych
'''''''
We use the JsPsych javascript framework to design our javascript experiments. While the current infrastructure is extendable to other frameworks, we have chosen JsPsych for our initial core of experiments.


Cognitive Atlas
---------------
Each experiment (task) is defined in the Cognitive Atlas, as are the cognitive concepts that the experiment measures. This means that, as more experiments are generated, a user can generate a battery intended to measure one or more cognitive concepts of interest. You can browse different tasks and cognitive concepts on the `Cognitive Atlas <http://www.cognitiveatlas.org>`_, and specify their unique IDs in the experiment config.json files.
