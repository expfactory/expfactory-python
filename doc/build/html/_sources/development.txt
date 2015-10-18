Development
===========

Contributing to this documentation
----------------------------------

First you should clone the psiturk-python repo

::

     git clone https://github.com/psiturk/psiturk-python

The documentation lives in the "doc" folder. Specifically, this is sphinx documentation that gets built automatically. The "build" folder contains the output that we serve on github pages, and this works by linking the index.html in the repo base to doc/build/html. The "source" folder contains files that you will want to edit.

You will need to install sphinx to work with these files

::

    sudo pip install sphinx


And familiarize yourself with the `restructured text (rst) documentation syntax <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.htm>`_. 

The basic infrastructure is set up, so you should be able to edit the places that you need, and if you need help with something more advanced (and you can't figure it out) contact someone else in the `Poldracklab <http://poldracklab.stanford.edu>`_ or just submit `an issue <https://github.com/psiturk/psiturk-python/issues>_`. 


Basic workflow
,,,,,,,,,,,,,,

 1. Edit a file
 2. Enter the documentation base folder

::

    cd doc
    make html


Note that you should READ the error messages in the console when you build - it will tell you if you forgot to include files, or have any other syntax errors. Then:

::

    cd build/html
    python -m SimpleHTTPServer -9999


This will start a local web server using python at localhost:9999.

 3. Open your browser to localhost:9999 to preview


Typically, static github pages content is served separate from the code on the gh-pages branch, but it's easy enough to keep the content of master and gh-pages the same. Thus, you should do all changes to master, submit a PR for approval, and then push the merged version to gh-pages.
 4. Commit changes to the repo, and submit a PR.
