'''
experiment.py: part of expfactory package
Functions to work with javascript experiments

'''

from expfactory.utils import find_directories, remove_unicode_dict
from glob import glob
import json
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
            ("tag",1,str),
            ("cognitive_atlas_task_id",1,str),
            ("performance_variable",0,dict),
            ("rejection_variable",0,dict),
            ("publish",1,str)]


def notvalid(reason):
    print reason
    return False

def dowarning(reason):
    print reason

def validate(experiment_folder,warning=True):
    '''validate
    :param experiment_folder: full path to experiment folder with config.json
    :param warning: issue a warning for empty fields with level 2 (warning)

    ..note::

        takes an experiment folder, and looks for validation based on:
    
        - config.json
        - files existing specified in config.json

        All fields should be defined, but for now we just care about run scripts
    
    '''

    try:
        meta = load_experiment(experiment_folder)
        experiment_name = os.path.basename(experiment_folder)
    except:
        return notvalid("%s: config.json is not loadable." %(experiment_folder))

    if len(meta)>1:
        return notvalid("%s: config.json has length > 1, not valid." %(experiment_folder))
    fields = get_validation_fields()

    for field,value,ftype in fields:

        # Field must be in the keys
        if field not in meta[0].keys():
            return notvalid("%s: config.json is missing field %s" %(experiment_name,field))

        # Tag must correspond with folder name
        if field == "tag":
            if meta[0][field] != experiment_name:
                return notvalid("%s: tag parameter %s does not match folder name." %(experiment_name,meta[0][field]))


        # Check if experiment is production ready
        if field == "publish":
            if meta[0][field] == "False":
                return notvalid("%s: config.json specifiesnot production ready." %experiment_name)

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

        # Run must be a list of strings
        if field == "run":
            # Is it a list?
            if not isinstance(meta[0][field],ftype):
                return notvalid("%s: field %s must be %s" %(experiment_name,field,ftype))
            # Is each script in the list a string?
            for script in meta[0][field]:
                # If we have a single file, is it in the experiment folder?
                if len(script.split("/")) == 1:
                    if not os.path.exists("%s/%s" %(experiment_folder,script)):
                        return notvalid("%s: %s is specified in config.json but missing." %(experiment_name,script))
    return True   


def get_experiments(experiment_repo,load=False,warning=True):
    '''get_experiments
    return loaded json for all valid experiments from an experiment folder
    :param experiment_repo: full path to the experiments repo
    :param load: if True, returns a list of loaded config.json objects. If False (default) returns the paths to the experiments

    '''

    experiments = find_directories(experiment_repo)
    valid_experiments = [e for e in experiments if validate(e,warning)]
    print "Found %s valid experiments" %(len(valid_experiments))
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
        meta = json.load(open(configjson,"r"))
        meta = remove_unicode_dict(meta[0])
        return [meta]
    except ValueError as e:
        print "Problem reading config.json, %s" %(e)
        raise


def make_lookup(experiment_list,key_field):
    '''make_lookup
    returns dict object to quickly look up query experiment on tag
    :param experiment_list: a list of query (dict objects)
    :param key_field: the key in the dictionary to base the lookup key (str)
    :returns lookup: dict (json) with key as "key_field" from query_list 
    '''
    lookup = dict()
    for single_experiment in experiment_list:
        lookup_key = single_experiment[0][key_field]
        lookup[lookup_key] = single_experiment[0]
    return lookup
