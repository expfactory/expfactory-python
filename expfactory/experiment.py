'''
experiment.py: part of expfactory package
Functions to work with javascript experiments

'''

from expfactory.utils import find_directories, remove_unicode_dict
from glob import glob
import filecmp
import json
import re
import os


def get_validation_fields():
    '''get_validation_fields
    Returns a list of tuples (each a field)

    ..note:: 

          specifies fields required for a valid json
          (field,value,type)
          field: the field name
          value: indicates minimum required entires
                 0: not required, no warning
                 1: required, not valid
                 2: not required, warning      
          type: indicates the variable type

    '''
    return [("run",1,list),
            ("name",2,str), 
            ("contributors",0,str),
            ("time",1,int), 
            ("notes",0,str),
            ("reference",2,str), 
            ("exp_id",1,str),
            ("cognitive_atlas_task_id",2,str),
            ("experiment_variables",0,list),
            ("publish",1,str),
            ("deployment_variables",0,str),
            ("template",1,str)]

def notvalid(reason):
    print(reason)
    return False

def dowarning(reason):
    print(reason)

def get_valid_templates():
    return ['jspsych','survey','phaser','custom']

def get_acceptable_values(package_name):
    acceptable_values = dict()
    acceptable_values["jspsych"] =["display_element",
                                   "on_finish",
                                   "on_trial_start",
                                   "on_trial_finish",
                                   "on_data_update",
                                   "show_progress_bar",
                                   "max_load_time",
                                   "skip_load_check",
                                   "fullscreen",
                                   "default_iti"]
    acceptable_values["survey"] = ["fullscreen"]

    return acceptable_values[package_name]


def validate(experiment_folder=None,warning=True):
    '''validate
    :param experiment_folder: full path to experiment folder with config.json
    :param warning: issue a warning for empty fields with level 2 (warning)

    ..note::

        takes an experiment folder, and looks for validation based on:
    
        - config.json
        - files existing specified in config.json

        All fields should be defined, but for now we just care about run scripts
    
    '''
    if experiment_folder==None:
        experiment_folder=os.path.abspath(os.getcwd())

    try:
        meta = load_experiment(experiment_folder)
        if meta == False:
            return notvalid("%s is not an experiment." %(experiment_folder))
        experiment_name = os.path.basename(experiment_folder)
    except:
        return notvalid("%s: config.json is not loadable." %(experiment_folder))

    if len(meta)>1:
        return notvalid("%s: config.json has length > 1, not valid." %(experiment_folder))
    fields = get_validation_fields()
    valid_templates = get_valid_templates()

    for field,value,ftype in fields:

        # Field must be in the keys if required
        if field not in meta[0].keys() and value == 1:
            return notvalid("%s: config.json is missing required field %s" %(experiment_name,field))
        else:
            if value == 2:
                if warning == True:
                    dowarning("WARNING: config.json is missing field %s: %s" %(field,experiment_name))

        if field == "exp_id":
            # Tag must correspond with folder name
            if meta[0][field] != experiment_name:
                return notvalid("%s: exp_id parameter %s does not match folder name." %(experiment_name,meta[0][field]))

            # name cannot have special characters, only _ and letters/numbers
            if not re.match("^[a-z0-9_]*$", meta[0][field]): 
                return notvalid("%s: exp_id parameter %s has invalid characters, only lowercase [a-z],[0-9], and _ allowed." %(experiment_name,meta[0][field]))

        # Check if experiment is production ready
        if field == "publish":
            if meta[0][field] == "False":
                return notvalid("%s: config.json specifies not production ready." %experiment_name)

        # Run must be a list of strings
        if field == "run":
            # Is it a list?
            if not isinstance(meta[0][field],ftype):
                return notvalid("%s: field %s must be %s" %(experiment_name,field,ftype))
            # Is an experiment.js defined
            # Is each script in the list a string?
            for script in meta[0][field]:
                # If we have a single file, is it in the experiment folder?
                if len(script.split("/")) == 1:
                    if not os.path.exists("%s/%s" %(experiment_folder,script)):
                        return notvalid("%s: %s is specified in config.json but missing." %(experiment_name,script))
                # Do we have an external script? It must be https
                if re.search("http",script) and not re.search("https",script):
                    return notvalid("%s: external script %s must be https." %(experiment_name,script))
                

        # Below is for required parameters
        if value == 1:
            if meta[0][field] == "":
                return notvalid("%s: config.json must be defined for field %s" %(experiment_name,field))
            # Field value must have minimum of value entries
            if not isinstance(meta[0][field],list):
                tocheck = [meta[0][field]]
            else:
                tocheck = meta[0][field]
            if len(tocheck) < value:
                return notvalid("%s: config.json must have >= %s for field %s" %(experiment_name,value,field))
        
        # Below is for warning parameters
        elif value == 2:
            if meta[0][field] == "":
                if warning == True:
                    dowarning("WARNING: config.json is missing value for field %s: %s" %(field,experiment_name))

        # Check the experiment template, currently valid are jspsych and survey
        if field == "template":
            if meta[0][field] not in valid_templates:
                return notvalid("%s: we currently only support %s experiments." %(experiment_name,",".join(valid_templates)))

            # Jspsych javascript experiment
            if meta[0][field] == "jspsych":
                if "run" in meta[0]:
                    if "experiment.js" not in meta[0]["run"]:
                        return notvalid("%s: experiment.js is not defined in run" %(experiment_name))
                else:
                    return notvalid("%s: config.json is missing required field run" %(experiment_name))

            # Material Design light survey
            elif meta[0][field] == "survey":
                if not os.path.exists("%s/survey.tsv" %(experiment_folder)):
                    return notvalid("%s: required survey.tsv for template survey not found." %(experiment_name))

            # Phaser game
            elif meta[0][field] == "phaser":
                if not os.path.exists("%s/Run.js" %(experiment_folder)):
                    return notvalid("%s: required Run.js main game file not found." %(experiment_name))
                if "run" not in meta[0]["deployment_variables"]:
                    return notvalid("%s: 'run' (code) is required in deployment_variables" %(experiment_name))

        # Validation for deployment_variables
        if field == "deployment_variables":
            if "deployment_variables" in meta[0]:
                if "jspsych_init" in meta[0][field]:
                    check_acceptable_variables(experiment_name,meta[0][field],"jspsych","jspsych_init")
                    
                elif "survey" in meta[0][field]:
                    check_acceptable_variables(experiment_name,meta[0][field],"survey","material_design")

    return True


def check_acceptable_variables(experiment_name,field_dict,template,field_dict_key):
    '''check_acceptable_variables takes a field (eg, meta[0][field]) that has a dictionary, and some template key (eg, jspsych) and makes sure the keys of the dictionary are within the allowable for the template type (the key).
    :param experiment_name: the name of the experiment
    :param field_dict: the field value from the config.json, a dictionary
    :param field_dict_key: a key to look up in the field_dict, which should contain a dictionary of {"key":"value"} variables
    :param template: the key name, for looking up acceptable values using get_acceptable_values
    '''
    acceptable_values = get_acceptable_values(template)
    for acceptable_var,acceptable_val in field_dict[field_dict_key].items():
        if acceptable_var not in acceptable_values:
            return notvalid("%s: %s is not an acceptable value for %s." %(experiment_name,acceptable_var,field_dict_key))

        # Jspsych specific validation
        if template == "jspsych":
            # Variables that must be boolean
            if acceptable_var in ["show_progress_bar","fullscreen","skip_load_check"]:
                check_boolean(experiment_name,acceptable_val,acceptable_var)      

            # Variables that must be numeric
            if acceptable_var in ["default_iti","max_load_time"]:
                if isinstance(acceptable_val,str) or isinstance(acceptable_val,bool):
                    return notvalid("%s: %s is not an acceptable value for %s in %s. Must be numeric." %(experiment_name,acceptable_val,acceptable_var,field_dict_key))

        elif template == "survey":
            # Variables that must be boolean
            if acceptable_var in ["show_progress_bar","fullscreen","skip_load_check"]:
                check_boolean(experiment_name,acceptable_val,acceptable_var)         

def check_boolean(experiment_name,value,variable_name):
    '''check_boolean checks if a value is boolean
    :param experiment_name: the name of the experiment
    :param value: the value to check
    :param variable_name: the name of the variable (the key being indexed in the dictionary)
    '''
    if value not in [True,False]:
        return notvalid("%s: %s is not an acceptable value for %s. Must be true/false." %(experiment_name,value,varialbe_name))


def get_experiments(experiment_repo, load=False, warning=True, repo_type="experiments"):
    '''get_experiments
    return loaded json for all valid experiments from an experiment folder
    :param experiment_repo: full path to the experiments repo
    :param load: if True, returns a list of loaded config.json objects. If False (default) returns the paths to the experiments
    :param repo_type: tells the user what kind of task is being parsed, default is "experiments," but can also be "surveys" when called by get_surveys
    '''
    experiments = find_directories(experiment_repo)
    valid_experiments = [e for e in experiments if validate(e,warning)]
    print("Found %s valid %s" %(len(valid_experiments),repo_type))
    if load == True:
        valid_experiments = load_experiments(valid_experiments)
    return valid_experiments


def load_experiments(experiment_folders):
    '''load_experiments
    a wrapper for load_experiment to read multiple experiments
    :param experiment_folders: a list of experiment folders to load, full paths
    '''
    experiments = []
    if isinstance(experiment_folders,str):
        experiment_folders = [experiment_folders]
    for experiment_folder in experiment_folders:
        exp = load_experiment(experiment_folder)
        experiments.append(exp)
    return experiments


def load_experiment(experiment_folder):
    '''load_experiment:
    reads in the config.json for an
    :param experiment folder: full path to experiment folder
    '''
    fullpath = os.path.abspath(experiment_folder)
    configjson = "%s/config.json" %(fullpath)
    if not os.path.exists(configjson):
        return notvalid("config.json could not be found in %s" %(experiment_folder))
    try: 
        with open(configjson,"r") as filey:
            meta = json.load(filey)
        meta = remove_unicode_dict(meta[0])
        return [meta]
    except ValueError as e:
        print("Problem reading config.json, %s" %(e))
        raise

def find_changed(new_repo,comparison_repo,return_experiments=True,repo_type="experiments"):
    '''find_changed returns a list of changed files or experiments between two repos
    :param new_repo: the updated repo - any new files, or changed files, will be returned
    :param comparison_repo: the old repo to compare against. A file changed or missing in this repo in the new_repo indicates it should be tested
    :param return_experiments: return experiment folders. Default is True. If False, will return complete file list
    ''' 
    # First find all experiment folders in current repo
    experiment_folders = get_experiments(new_repo,load=False,warning=False,repo_type=repo_type)
    file_list = []
    # Find all files
    for experiment_folder in experiment_folders:
        for root, dirnames, filenames in os.walk(experiment_folder):
            for filename in filenames:
                file_list.append(os.path.join(root, filename))
    # Compare against master
    changed_files = []
    for contender_file in file_list:
        old_file = contender_file.replace("%s/expfactory-%s" %(os.environ["HOME"],repo_type),comparison_repo)
        # If the old file exists, check if it's changed
        if os.path.exists(old_file):
            if not filecmp.cmp(old_file,contender_file):
                changed_files.append(contender_file)
        # If it doesn't exist, we check
        else:
            changed_files.append(contender_file)

    # Find differences with compare
    print("Found files changed: %s" %(",".join(changed_files)))

    if return_experiments == True:
        return list(set([os.path.dirname(x.strip("\n")) for x in changed_files if os.path.dirname(x.strip("\n")) != ""]))
  
    return changed_files


def make_lookup(experiment_list,key_field):
    '''make_lookup
    returns dict object to quickly look up query experiment on exp_id
    :param experiment_list: a list of query (dict objects)
    :param key_field: the key in the dictionary to base the lookup key (str)
    :returns lookup: dict (json) with key as "key_field" from query_list 
    '''
    lookup = dict()
    for single_experiment in experiment_list:
        lookup_key = single_experiment[0][key_field]
        lookup[lookup_key] = single_experiment[0]
    return lookup
