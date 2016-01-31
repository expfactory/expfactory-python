About
=====

The Experiment Factory is developed by the `Poldracklab <http://poldracklab.stanford.edu>`_ at Stanford University, and all code is publicly available on `Github <http://www.github.com/expfactory>`_. The current landscape of behavioral paradigms is messy at best, and so the Experiment Factory is an effort to standardize, organize, and collaboratively develop experiments that can be run on multiple infrastructures. Currently supported is generating experiments in a battery intended to run with `psiturk <https://github.com/NYUCCL/>`_ on a local computer, a vagrant virtual machine, or Amazon Web Services. We intend to add support for docker and other web applications soon, and welcome your contributions to `experiments <http://www.github.com/expfactory/expfactory-experiments>`_, `psiturk battery generation <http://www.github.com/expfactory/expfactory-battery>`_, `virtual machines <http://www.github.com/expfactory/expfactory-vm>`_, and the `software itself <http://www.github.com/expfactory/expfactory-python>`_.

We are called the Experiment Factory because we want the software to support flexibility in designing the experiments, infrastructure, and deployment for your experiments.  Psychology and neuroscience researchers should have the same modern tools available to them as a commercial effort, and long gone should be the days of passing around paradigms from computer to computer on USB sticks. If we work together we can refine experiments to make them better, and making behavioral measurments with the same thing is one step toward a vision of reproducible science.


Integrations and Tools
----------------------

Psiturk
'''''''
These experiments are intended to run via the `psiturk infrastructure<https://github.com/NYUCCL/psiTurk>_`, and the `experiment factory battery<http://www.github.com/expfactory/expfactory-battery>_` is the main experiment code that, when fit with `experiments<http://www.github.com/expfactory/expfactory-experiments>_`, can run on Amazon Mechanical Turk.


JsPsych
'''''''
We use the JsPsych javascript framework to design our javascript experiments. While the current infrastructure is extendable to other frameworks, we have chosen JsPsych for our initial core of experiments.


Cognitive Atlas
---------------
Each experiment (task) is defined in the Cognitive Atlas, as are the cognitive concepts that the experiment measures. This means that, as more experiments are generated, a user can generate a battery intended to measure one or more cognitive concepts of interest. You can browse different tasks and cognitive concepts on the `Cognitive Atlas <http://www.cognitiveatlas.org>`_, and specify their unique IDs in the experiment config.json files.
