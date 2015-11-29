Installation
============

To install the latest version, use pip:

::

      pip install git+git://github.com/expfactory/expfactory-python.git



To install a (possibly older) version:


::


     pip install expfactory
 


Please note that expfactory was developed with python 2.7 and has not been tested on other versions. Installation will place an executable, `expfactory` in your bin folder. You should be able to type `which expfactory` and see the location of your application. If you cannot, you likely installed the application locally, and the executable was placed in a folder not on your path. You can either try installation with sudo, or look at the output of the installation to find the path that it was installed to:

::

      Installing expfactory script to /usr/local/bin




Quickstart
''''''''''

To run the executable to open up a web interface to select what you would like to do:


::

      expfactory



You can also specify a port:


::

      expfactory --port=8088


To preview a folder (experiment) you are working on, you can cd into that folder, and use the `--preview` command:


::


      cd simple_experiment
      expfactory --preview


You can also specify the folder as an argument:

::

      expfactory --preview --folder /home/vanessa/Desktop/simple_rt
      

.. image:: _static/img/api/webinterface.png
