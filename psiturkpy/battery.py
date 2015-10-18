'''
battery.py: part of psiturkpy package
Functions to generate psiturk batteries

'''
from psiturkpy.experiment import get_experiments, load_experiment
from psiturkpy.utils import copy_directory, get_template, \
     sub_template, get_installdir, save_template
from psiturkpy.vm import custom_battery_download
import os
import re


"""
generate will create a battery from a template
and list of experiments

"""

def generate(battery_dest,battery_repo=None,experiment_repo=None,experiments=None,config=None):

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
        valid_experiments = get_experiments(experiment_repo)

        # If the user wants to select a subset
        if experiments != None:
            subset_experiments = [x for x in valid_experiments if os.path.basename(x) in experiments]
            valid_experiments = subset_experiments      

        # Fill in templates with the experiments, generate config
        template_experiments(battery_dest,battery_repo,valid_experiments)
        if config == None:
            config = dict()
        generate_config(battery_dest,config)
    else:
        print "Folder exists at %s, cannot generate." %(battery_dest)

        
"""
template_experiments:
For each valid experiment, copies the entire folder into the battery destination
directory, and generates templates with appropriate paths to run them

"""
def template_experiments(battery_dest,battery_repo,valid_experiments):
    # Generate run template, make substitutions
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


"""
For each valid experiment, move into experiments folder in battery repo
"""
def move_experiments(valid_experiments,battery_dest):
    moved_experiments = []
    for valid_experiment in valid_experiments:
        try:
            experiment_folder = os.path.basename(valid_experiment)
            copy_directory(valid_experiment,"%s/static/experiments/%s" %(battery_dest,experiment_folder))
            moved_experiments.append(valid_experiment)
        except:
           print "Cannot move %s, will not be added." %(valid_experiment)
    return moved_experiments


"""
generate_config
takes a dictionary, and for matching fields, substitues and prints
to "config.txt" in a specified battery directory

  battery_dest: should be the copied, skeleton battery folder in generation
  fields: should be a dictionary with fields that match those in the config
          non matching fields will be ignored.

"""
def generate_config(battery_dest,fields):
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



"""
get_config: load in a dummy config file from psiturkpy
"""

def get_config():
    module_path = get_installdir()
    template = "%s/templates/config.txt" %(module_path)
    config = get_template(template)
    config = config.split("\n")
    for l in range(len(config)):
        line = config[l]
        if len(line)>0:
            if line[0]!="[":
                fields = [x.strip(" ") for x in line.split("=")]
                config[l] = {fields[0]:fields[1]} 
    return config


"""
Return javascript to load list of valid experiments, based on psiturk.json
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
"""
def get_load_js(valid_experiments):
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
                loadstring = '%s         loadjscssfile("static/experiments/%s/%s","%s")\n' %(loadstring,tag,script,ext)
            else:
                loadstring = '%s         loadjscssfile("%s","%s")\n' %(loadstring,script,ext)
        loadstring = "%s         break;\n" %(loadstring)
    return loadstring


"""
Return javascript concat section for valid experiments, based on psiturk.json

			case "simple-rt":
				experiments = experiments.concat(simple-rt_experiment)
				break;
			case "choice-rt":
				experiments = experiments.concat(choice-rt_experiment)
				break;

Format for experiment variables is [tag]_experiment

"""
def get_concat_js(valid_experiments):
    concatjs = "\n"
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)[0]
        tag = str(experiment["tag"])
        concatjs = '%scase "%s":\n' %(concatjs,tag)
        concatjs = '%s      experiments = experiments.concat(%s_experiment)\n' %(concatjs,tag)
        concatjs = '%s      break;\n' %(concatjs)
    return concatjs

"""
String (json / dictionary) of experiment timings in the format:
 {name:"simple_rt", time: 3.5}, {name:"choice_rt", time: 4}, ...

"""
def get_timing_js(valid_experiments):
    timingjs = []
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)[0]
        timingjs.append({"name":str(experiment["tag"]),"time":experiment["time"]})
    return timingjs
