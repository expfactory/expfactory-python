'''
battery.py: part of psiturkpy package
Functions to generate psiturk batteries

'''
import os
import re
from psiturkpy.utils import copy_directory, find_directories, \
     get_template, sub_template
from psiturkpy.experiment import validate, load_experiment

#TODO: in future, location of battery repo should be envionment variable

"""
generate will create a battery from a template
and list of experiments

"""
def generate(battery_repo,battery_dest,experiment_repo):
    #TODO: Config file should be generated here as well
    #TODO: battery and experiment repo should not be required (auto download to tmp folders)
    if not os.path.exists(battery_dest):
        copy_directory(battery_repo,battery_dest)
        # Get valid experiments
        #TODO: give user choice in experiments
        experiments = find_directories(experiment_repo)
        valid_experiments = [e for e in experiments if validate(e)]
        print "Found %s valid experiments" %(len(valid_experiments))
        load_experiments(battery_dest,valid_experiments)
    else:
        print "Folder exists at %s, cannot generate." %(battery_repo)

        
"""
load_experiments:
For each valid experiment, copies the entire folder into the battery destination
directory, and generates templates with appropriate paths to run them

"""
def load_experiments(battery_dest,valid_experiments):

    # Generate run template, make substitutions
    template_file = "%s/static/js/load_experiments.js" %(battery_dest)
    load_template = get_template(template_file)
    valid_experiments = move_experiments(valid_experiments,battery_dest)
    loadjs = get_load_js(valid_experiments) 
    concatjs = get_concat_js(valid_experiments) 
    timingjs = get_timing_js(valid_experiments)
    load_template = sub_template(load_template,"[SUB_EXPERIMENTCONCAT_SUB]",concatjs)
    load_template = sub_template(load_template,"[SUB_EXPERIMENTLOAD_SUB]",loadjs)
    load_template = sub_template(load_template,"[SUB_EXPERIMENTTIMES_SUB]",str(timingjs)) 
    filey = open(template_file,'w')
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
        loadstring = '%scase: "%s":\n' %(loadstring,tag)
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
        concatjs = '%scase: "%s":\n' %(concatjs,tag)
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
