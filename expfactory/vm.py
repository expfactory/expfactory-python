'''
vm.py: part of expfactory package
Functions to generate virtual machines to run expfactory batteries

Copyright (c) 2016-2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


'''

from expfactory.utils import save_template, clean_fields, copy_directory, get_installdir, sub_template, get_template
from logman import bot
from git import Repo
import tempfile
import shutil
import sys
import os
import re

def download_repo(repo_type,destination):
    '''download_repo
    Download a expfactory infrastructure repo "repo_type" to a "destination"
    :param repo_type: can be one of "experiments" "battery" "vm"
    :param destination: the full path to the destination for the repo
    '''
    acceptable_types = ["experiments","battery","vm","surveys","games"]
    if repo_type not in acceptable_types:
        bot.error("repo_type must be in %s" %(",".join(acceptable_types)))
        sys.exit(1)
    else:
        return Repo.clone_from("https://github.com/expfactory/expfactory-%s" %(repo_type), destination)


def custom_battery_download(tmpdir=None,repos=["experiments","battery","surveys","games"]):
    '''custom_battery_download
    Download battery and experiment repos to a temporary folder to build a custom battery, return the path to the tmp folders
    :param tmpdir: The directory to download to. If none, a temporary directory will be made
    :param repos: The repositories to download, valid choices are "experiments" "battery" and "vm"
    '''
    if isinstance(repos,str):
        repos = [repos]
    if not tmpdir:
        tmpdir = tempfile.mkdtemp()
    for repo in repos:
        download_repo(repo,"%s/%s/" %(tmpdir,repo))
    return tmpdir


def add_custom_logo(battery_repo,logo):
    '''add_custom_logo
    Add a custom logo to the vm battery
    :param battery_repo: the full path to the battery repo base, assumed to have an "img" folder
    :param logo: the full path to the logo to copy. Should ideally be png.
    '''
    shutil.copy(logo,"%s/img/logo.png" %(battery_repo))
    

def generate_database_url(dbtype=None,username=None,password=None,host=None,table=None,template=None):
    '''generate_database_url
    Generate a database url from input parameters, or get a template
    :param dbtype: the type of database, must be one of "mysql" or "postgresql"
    :param username: username to connect to the database
    :param password: password to connect to the database
    :param host: database host
    :para table: table in the database
    :param template: can be one of "mysql" "sqlite3" or "postgresql" If specified, all other parameters are ignored, and a default database URL is produced to work in a Vagrant VM produced by expfactory
    
    '''
    if not template:
        if not dbtype or not username or not password or not host or not table:
            bot.error("Please provide all inputs: dbtype,username,password,host,table.")
            sys.exit(1)
        else:
            return "%s://%s:%s@%s/%s"  %(dbtype,
                                         username,
                                         password,
                                         host,
                                         table)
    elif template == "mysql":
        return "mysql://expfactory:expfactory@localhost:3306/expfactory"
    elif template == "sqlite3":
        return "sqlite:///participants.db" 
    elif template == "postgresql":
        return "postgresql://expfactory:expfactory@localhost:5432/expfactory"


def prepare_vm(battery_dest,fields=None,vm_repo=None,vm_type="vagrant"):
    '''prepare_vm
    Prepare virtual machine to run local with vagrant, or with vagrant-aws
    :param battery_dest: the battery destination folder
    :param fields: if specified, will be added to the config.txt
    :param vm_repo: the expfactory-vm repo to use for templates. If not provided, one will be downloaded to a temporary directory for use.
    :param vm_type: one of "vagrant" or "aws" Default is "vagrant" meaning a localvirtual machine with vagrant.
    
    '''

    # Download vm_repo if it hasn't been specified
    if not vm_repo:
        download_repo("vm","%s/vm" %battery_dest)

    # Grab the appropriate vagrantfile template
    if vm_type == "aws":
        template = get_template("%s/vm/VagrantfileAWS" %(battery_dest))
    else:
        template = get_template("%s/vm/VagrantfileLocal" %(battery_dest))

    # If the user has custom config fields, write to file
    if fields != None:
        fields = clean_fields(fields)
        template = sub_template(template,"[SUB_CONFIG_SUB]",str(fields))
    else:
        template = sub_template(template,"[SUB_CONFIG_SUB]","None")

    # Change file to be a custom install
    template = sub_template(template,'CUSTOM_INSTALL="False"','CUSTOM_INSTALL="True"')
        
    output_file = "%s/Vagrantfile" %(battery_dest)
    save_template(output_file,template)
    return template

def specify_experiments(battery_dest,experiments):
    '''specify_experiments
    Specify experiments for a Vagrantfile in an output folder
    :param battery_dest: destination folder for battery
    :param experiments: a list of experiment tags to include
    '''
    experiments = [e.encode("utf-8") for e in experiments]
    vagrantfile = "%s/Vagrantfile" %(battery_dest)
    if not os.path.exists(vagrantfile):
        prepare_vm(battery_dest)
    template = get_template(vagrantfile)
    template = sub_template(template,"[SUB_EXPERIMENTS_SUB]",str(experiments))
    save_template(vagrantfile,template)
    return template

def get_stylejs(experiment,url_prefix=""):
    '''get_stylejs
    return string for js and css scripts to insert into a page based on battery path structure
    '''
    js = ""
    css = ""
    scripts = experiment[0]["run"]
    tag = experiment[0]["exp_id"]
    repo_type = "experiments"
    if experiment[0]["template"] == "survey":
        repo_type = "surveys"
    elif experiment[0]["template"] == "phaser":
        repo_type = "games"

    for script in scripts:
        ext = script.split(".")[-1]

        # Do we have a relative experiment path?
        if len(script.split("/")) == 1:
            if ext == "js":
                js = "%s\n<script src='%sstatic/%s/%s/%s'></script>" %(js,url_prefix,repo_type,tag,script)
            elif ext == "css":
                css = "%s\n<link rel='stylesheet' type='text/css' href='%sstatic/%s/%s/%s'>" %(css,url_prefix,repo_type,tag,script)

        # Do we have an https/https path?
        elif re.search("^http",script):
            if ext == "js":
                js = "%s\n<script src='%s'></script>" %(js,script)
            elif ext == "css":
                css = "%s\n<link rel='stylesheet' type='text/css' href='%s'>" %(css,script)

        # Do we have a battery relative path?
        else:    
            if ext == "js":
                js = "%s\n<script src='%s%s'></script>" %(js,url_prefix,script)
            elif ext == "css":
                css = "%s\n<link rel='stylesheet' type='text/css' href='%s%s'>" %(css,url_prefix,script)

    return css,js


def get_jspsych_init(experiment,deployment="local",finished_message=None):
    '''get_jspsych_init
    return entire jspsych init structure
    :param experiment: the loaded config.json for the experiment
    :param deployment: specify to deploy local (default), or docker-mturk,docker-local (expfactory-docker). 
    :param finished_message: custom message to show at the end of the experiment with Redo and Next Experiment Buttons
    '''
    jspsych_init = "jsPsych.init({\ntimeline: %s_experiment,\n" %(experiment["exp_id"])

    if finished_message == None:
        finished_message = 'You have completed the experiment. Click "Next Experiment" to keep your result, and progress to the next task. If you believe your ability to focus was significantly compromised by some external factor (e.g. someone started talking to you while you were doing the task) press "Redo Experiment" to be presented with the task again at a later time.'

    default_inits = dict()
    default_inits["local"] = {"on_finish":["jsPsych.data.localSave('%s_results.csv', 'csv');\nexpfactory_finished = true;" %(experiment["exp_id"])]}

    # Amazon Mechanical Turk
    default_inits["docker-mturk"] = {"on_finish":["""finished_message = '<div id="finished_message" style="margin:100px"><h1>Experiment Complete</h1><p>%s</p><button id="next_experiment_button" type="button" class="btn btn-success">Next Experiment</button><button type="button" id="redo_experiment_button" class="btn btn-danger">Redo Experiment</button></div>'\nexpfactory.recordTrialData(jsPsych.data.getData());\n$("body").append(finished_message);\n$(".display_stage").hide();\n$(".display_stage_background").hide();\n$("#redo_experiment_button").click( function(){\njavascript:window.location.reload();\n})\n$("#next_experiment_button").click( function(){\nexpfactory.djstatus = "FINISHED";\n$.ajax({ type: "POST",\ncontentType: "application/json",\nurl : "/sync/{{result.id}}/",\ndata : JSON.stringify(expfactory),\ndataType: "json",\nerror: function(error){\nconsole.log(error)\n},\nsuccess: function(data){\nconsole.log("Finished!");\nif (data.finished_battery == "FINISHED"){\n$("#turkey_form").submit()\n} else {\ndocument.location = "{{next_page}}";\n}\n}\n});\n});\n""" %finished_message],
                               "on_data_update":["""expfactory.djstatus = "UPDATE";\n$.ajax({ type: "POST",\ncontentType: "application/json",\nurl : "/sync/{{result.id}}/",\ndata : JSON.stringify(expfactory),\ndataType: "json",\nsuccess: function(data){\nconsole.log("data update called")\n}\n});\n"""]}

    # Local Docker Deployment
    default_inits["docker-local"] = {"on_finish":["""finished_message = '<div id="finished_message" style="margin:100px"><h1>Experiment Complete</h1><p>%s</p><button id="next_experiment_button" type="button" class="btn btn-success">Next Experiment</button><button type="button" id="redo_experiment_button" class="btn btn-danger">Redo Experiment</button></div>'\nexpfactory.recordTrialData(jsPsych.data.getData());\n$("body").append(finished_message)\n$(".display_stage").hide()\n$(".display_stage_background").hide()\n$("#redo_experiment_button").click( function(){\njavascript:window.location.reload();\n})\n$("#next_experiment_button").click( function(){\nexpfactory.djstatus = "FINISHED";\n$.ajax({ type: "POST",\ncontentType: "application/json",\nurl : "/local/{{result.id}}/",\ndata : JSON.stringify(expfactory),\ndataType: "json",\nerror: function(error){\nconsole.log(error)\n},\nsuccess: function(data){\nconsole.log("Finished!");\ndocument.location = "{{next_page}}";\n}\n});\n});\n""" %finished_message],
                               "on_data_update":["""expfactory.djstatus = "UPDATE";\n$.ajax({ type: "POST",\ncontentType: "application/json",\nurl : "/local/{{result.id}}/",\ndata : JSON.stringify(expfactory),\ndataType: "json",\nsuccess: function(data){\nconsole.log("data update called")\n}\n});\n"""]}
    
    # Docker Preview, no saving of data
    default_inits["docker-preview"] = {"on_finish":["""finished_message = '<div id="finished_message" style="margin:100px"><h1>Experiment Complete</h1><p>%s</p><button id="next_experiment_button" type="button" class="btn btn-success">Next Experiment</button><button type="button" id="redo_experiment_button" class="btn btn-danger">Redo Experiment</button></div>'\n$("body").append(finished_message)\n$(".display_stage").hide()\n$(".display_stage_background").hide()\n$("#redo_experiment_button").click( function(){\njavascript:window.location.reload();\n})\n$("#next_experiment_button").click( function(){\nconsole.log("Finished!");\ndocument.location = "{{next_page}}";\n});\n""" %finished_message],
                               "on_data_update":["""console.log(data);\n"""]}



    if "deployment_variables" in experiment:
        if "jspsych_init" in experiment["deployment_variables"]:
            custom_variables = experiment["deployment_variables"]["jspsych_init"]

            # Fill user custom variables into data structure
            for jspsych_var,jspsych_val in custom_variables.iteritems():
                if deployment == "local":            
                    if jspsych_var in default_inits[deployment]:
                         holder = default_inits[deployment][jspsych_var]
                         holder.append(jspsych_val)
                         default_inits[deployment][jspsych_var] = holder
                    else:
                         default_inits[deployment][jspsych_var] = [jspsych_val]
                elif deployment in ["docker-mturk","docker-local","docker-preview"]:
                    if jspsych_var not in default_inits[deployment]:
                         default_inits[deployment][jspsych_var] = [jspsych_val]

    # Write rest of config
    for v in range(len(default_inits[deployment])):
        jspsych_var = default_inits[deployment].keys()[v]
        jspsych_val = "\n".join([str(x) for x in default_inits[deployment].values()[v]]) 
        if jspsych_var in ["on_finish","on_data_update","on_trial_start","on_trial_finish"]:
            jspsych_init = "%s%s: function(data){\n%s\n}" %(jspsych_init,
                                                            jspsych_var,
                                                            jspsych_val)

        # Boolean
        elif jspsych_var in ["show_progress_bar","fullscreen","skip_load_check"]:
            jspsych_init = "%s%s: %s" %(jspsych_init,
                                        jspsych_var,
                                        jspsych_val.lower())

        # Numeric (no quotes)
        elif jspsych_var in ["default_iti","max_load_time"]:
            jspsych_init = "%s%s: %s" %(jspsych_init,
                                        jspsych_var,
                                        jspsych_val)
        # Everything else
        else:
            jspsych_init = '%s%s: "%s"' %(jspsych_init,
                                        jspsych_var,
                                        jspsych_val)

        if v != len(default_inits[deployment])-1:
            jspsych_init = "%s,\n" %(jspsych_init)
        else:
            jspsych_init = "%s\n});" %(jspsych_init)

    return jspsych_init
