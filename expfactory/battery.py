'''
battery.py: part of expfactory package
Functions to generate batteries

'''
from expfactory.experiment import get_experiments, load_experiment
from expfactory.utils import copy_directory, get_template, \
     sub_template, get_installdir, save_template
from expfactory.vm import custom_battery_download
import os
import re


def generate(battery_dest,battery_repo=None,experiment_repo=None,experiments=None,config=None,make_config=True,warning=True):
    '''generate
    will create a battery from a template and list of experiments
    :param battery_dest: [required] is the output folder for your battery. This folder MUST NOT EXIST.
    :param battery_repo: location of psiturk-battery repo to use as a template. If not specified, will be downloaded to a temporary directory
    :param experiment_repo: location of a expfactory-experiments repo to check for valid experiments. If not specified, will be downloaded to a temporary directory
    :param experiments: a list of experiments, meaning the "tag" variable in the config.json, to include. This variable also conincides with the experiment folder name.
    :param config: A dictionary with keys that coincide with parameters in the config.txt file for a expfactory experiment. If not provided, a dummy config will be generated.
    :param make_config: A boolean (default True) to control generation of the config. If there is a config generated before calling this function, this should be set to False.
    :param warning: Show config.json warnings when validating experiments. Default is True
    '''
    # We can only generate a battery to a folder that does not exist, to be safe
    if not os.path.exists(battery_dest):
        if experiment_repo == None or battery_repo == None:
            tmpdir = custom_battery_download()
            if experiment_repo == None:
                experiment_repo = "%s/experiments" %(tmpdir)     
            if battery_repo == None:
                battery_repo = "%s/battery" %(tmpdir)     

        # Copy battery skeleton to destination
        copy_directory(battery_repo,battery_dest)
        valid_experiments = get_experiments(experiment_repo,warning=warning)

        # If the user wants to select a subset
        if experiments != None:
            subset_experiments = [x for x in valid_experiments if os.path.basename(x) in [os.path.basename(e) for e in experiments]]
            valid_experiments = subset_experiments      

        # Fill in templates with the experiments, generate config
        template_experiments(battery_dest,battery_repo,valid_experiments)
        if make_config:
            if config == None:
                config = dict()
            generate_config(battery_dest,config)
    else:
        print "Folder exists at %s, cannot generate." %(battery_dest)

        
def template_experiments(battery_dest,battery_repo,valid_experiments,template_file=None):
    '''template_experiments:
    For each valid experiment, copies the entire folder into the battery destination directory, and generates templates with appropriate paths to run them
    :param battery_dest: full path to destination folder of battery
    :param battery_repo: full path to psiturk-battery repo template
    :param valid_experiments: a list of full paths to experiment folders to include
    :param template_file: the load_experiments.js template file. If not specified, the file from the battery repo is used.
    '''
    # Generate run template, make substitutions
    if template_file == None:
        template_file = "%s/static/js/load_experiments.js" %(battery_repo)
    load_template = get_template(template_file)
    valid_experiments = move_experiments(valid_experiments,battery_dest)
    loadjs = get_load_js(valid_experiments) 
    concatjs = get_concat_js(valid_experiments) 
    timingjs = get_timing_js(valid_experiments)
    load_template = sub_template(load_template,"[SUB_EXPERIMENTCONCAT_SUB]",concatjs)
    load_template = sub_template(load_template,"[SUB_EXPERIMENTLOAD_SUB]",loadjs)
    load_template = sub_template(load_template,"[SUB_EXPERIMENTTIMES_SUB]",str(timingjs)) 
    template_output = "%s/static/js/load_experiments.js" %(battery_dest)
    filey = open(template_output,'w')
    filey.writelines(load_template)
    filey.close()    


def move_experiments(valid_experiments,battery_dest):
    '''move_experiments
    Moves valid experiments into the experiments folder in battery repo
    :param valid_experiments: a list of full paths to valid experiments
    :param battery_dest: full path to battery destination folder
    '''

    moved_experiments = []
    for valid_experiment in valid_experiments:
        try:
            experiment_folder = os.path.basename(valid_experiment)
            copy_directory(valid_experiment,"%s/static/experiments/%s" %(battery_dest,experiment_folder))
            moved_experiments.append(valid_experiment)
        except:
           print "Cannot move %s, will not be added." %(valid_experiment)
    return moved_experiments


def generate_config(battery_dest,fields):
    '''generate_config
    takes a dictionary, and for matching fields, substitues and prints to "config.txt" in a specified battery directory
    :param battery_dest: should be the copied, skeleton battery folder in generation
    :param fields: should be a dictionary with fields that match those in the config non matching fields will be ignored.
    '''
    config = get_config()
    # Convert dictionaries back to string
    for l in range(len(config)):
        line = config[l]
        if isinstance(line,dict):
            linekey = line.keys()[0]
            if linekey in fields.keys():
                config[l][linekey] = fields[linekey]
            config[l] = "%s = %s" %(linekey,config[l][linekey])
    config = "\n".join(config)    
    save_template("%s/config.txt" %battery_dest,config)
    return config



def get_config():
    '''get_config
    load in a dummy config file from expfactory
    '''
    module_path = get_installdir()
    template = "%s/templates/config.txt" %(module_path)
    config = get_template(template)
    config = config.split(os.linesep)
    for l in range(len(config)):
        line = config[l]
        if len(line)>0:
            if line[0]!="[":
                fields = [x.strip(" ") for x in line.split("=")]
                config[l] = {fields[0]:fields[1]} 
    return config


def get_load_static(valid_experiments,url_prefix=""):
    '''get_load_static
    return the scripts and styles as <link> and <script> to embed in a page directly
    '''
    loadstring = "\n"
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)[0]
        tag = str(experiment["tag"])
        for script in experiment["run"]:
            fname,ext = os.path.splitext(script)
            ext = ext.replace(".","").lower()
            # If the file is included in the experiment
            if len(script.split("/")) == 1:               
                if ext == "js":   
                    loadstring = '%s<script type="text/javascript" src="%sstatic/experiments/%s/%s"></script>\n' %(loadstring,url_prefix,tag,script)
                else:
                    loadstring = '%s<link rel="stylesheet" href="%sstatic/experiments/%s/%s" />\n' %(loadstring,url_prefix,tag,script)
            else:
                loadstring = '%s<script type="text/javascript" src="%s%s"></script>\n' %(loadstring,url_prefix,script)    
    return loadstring


def get_load_js(valid_experiments,url_prefix=""):
    '''get_load_js
    Return javascript to load list of valid experiments, based on psiturk.json
    :param valid_experiments: a list of full paths to valid experiments to include

    ..note::
        Format is:
         {
		case "simple_rt":
			loadjscssfile("static/css/experiments/simple_rt.css","css")
			loadjscssfile("static/js/experiments/simple_rt.js","js")
			break;
		case "choice_rt":
			loadjscssfile("static/css/experiments/choice_rt.css","css")
			loadjscssfile("static/js/experiments/choice_rt.js","js")
			break;

          ...
          }

    '''
    loadstring = "\n"
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)[0]
        tag = str(experiment["tag"])
        loadstring = '%scase "%s":\n' %(loadstring,tag)
        for script in experiment["run"]:
            fname,ext = os.path.splitext(script)
            ext = ext.replace(".","").lower()
            # If the file is included in the experiment
            if len(script.split("/")) == 1:                
                loadstring = '%s         loadjscssfile("%sstatic/experiments/%s/%s","%s")\n' %(loadstring,url_prefix,tag,script,ext)
            else:
                loadstring = '%s         loadjscssfile("%s%s","%s")\n' %(loadstring,url_prefix,script,ext)
        loadstring = "%s         break;\n" %(loadstring)
    return loadstring


def get_concat_js(valid_experiments):
    '''get_concat_js
    Return javascript concat section for valid experiments, based on psiturk.json
    :param valid_experiments: full paths to valid experiments to include

    ..note::

			case "simple-rt":
				experiments = experiments.concat(simple-rt_experiment)
				break;
			case "choice-rt":
				experiments = experiments.concat(choice-rt_experiment)
				break;

               Format for experiment variables is [tag]_experiment

    '''
    concatjs = "\n"
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)[0]
        tag = str(experiment["tag"])
        concatjs = '%scase "%s":\n' %(concatjs,tag)
        concatjs = '%s      experiments = experiments.concat(%s_experiment)\n' %(concatjs,tag)
        concatjs = '%s      break;\n' %(concatjs)
    return concatjs

def get_timing_js(valid_experiments):
    '''get_timing_js
    Produce string (json / dictionary) of experiment timings
    :param valid_experiments: a list of full paths to valid experiments to include

    ..note::

         Produces the following format for each experiment

         {name:"simple_rt", time: 3.5}, {name:"choice_rt", time: 4}, ...
    
    
    '''
    timingjs = []
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)[0]
        timingjs.append({"name":str(experiment["tag"]),"time":experiment["time"]})
    return timingjs
