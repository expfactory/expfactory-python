'''
views.py

part of the experiment factory package
functions for developing experiments and batteries, viewing and testing things
'''

from expfactory.utils import copy_directory, get_installdir, sub_template
from expfactory.vm import custom_battery_download, get_stylejs
from expfactory.experiment import load_experiment
from numpy.random import choice
import SimpleHTTPServer
import SocketServer
import webbrowser
import shutil
import os

def preview_experiment(folder=None,port=None):

    if folder==None:
        folder=os.path.abspath(os.getcwd())

    tmpdir = custom_battery_download(repos=["battery"])
    experiment = load_experiment("%s" %folder)
    tag = experiment[0]["tag"]

    # We will copy the entire experiment into the battery folder
    battery_folder = "%s/battery" %(tmpdir)
    experiment_folder = "%s/static/experiments/%s" %(battery_folder,tag)
    if os.path.exists(experiment_folder):
        shutil.rmtree(experiment_folder)
    copy_directory(folder,experiment_folder)
    index_file = "%s/index.html" %(battery_folder)
        
    # Generate code for js and css
    css,js = get_stylejs(experiment)
    exp_template = "%s/templates/experiment.html" %get_installdir()
    exp_template = "".join(open(exp_template,"r").readlines())
    exp_template = sub_template(exp_template,"{{js}}",js)
    exp_template = sub_template(exp_template,"{{css}}",css)
    exp_template = sub_template(exp_template,"{{tag}}",experiment[0]["tag"])
    filey = open(index_file,"w")
    filey.writelines(exp_template)
    filey.close()

    os.chdir(battery_folder)
    
    try:
        if port == None:
            port = choice(range(8000,9999),1)[0]
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", port), Handler)
        print "Preview experiment at localhost:%s" %port
        webbrowser.open("http://localhost:%s" %(port))
        httpd.serve_forever()
    except:
        print "Stopping web server..."
        httpd.server_close()
        shutil.rmtree(tmpdir)

