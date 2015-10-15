'''
experiment.py: part of psiturkpy package
Functions to work with javascript experiments

'''

from psiturkpy.utils import find_directories, remove_unicode_dict
from glob import glob
import json
import os


"""
Fields required for a valid json
  (field,value,type)
  value indicates minimum required entires
  type indicates the variable type

"""
def get_validation_fields():
    return [("doi",0,str),
            ("run",1,list),
            ("name",0,str), 
            ("contributors",0,str),
            ("time",1,int), 
            ("notes",0,str),
            ("reference",0,str), 
            ("lab",0,str), 
            ("cognitive_atlas_concept_id",1,str), 
            ("cognitive_atlas_concept",0,str),
            ("tag",1,str),
            ("cognitive_atlas_task_id",0,str)]

def notvalid(reason):
    print reason
    return False

"""
validate:
takes an experiment folder, and looks for validation based on:

- psiturk.json
- files existing specified in psiturk.json

All fields should be defined, but for now we just care about run scripts
"""

def validate(experiment_folder):
    meta = load_experiment(experiment_folder)
    if len(meta)>1:
        return notvalid("psiturk.json has length > 1, not valid.")
    fields = get_validation_fields()
    for field,value,ftype in fields:
        if value != 0:
            # Field must exist in the keys
            if field not in meta[0].keys():
                return notvalid("psiturk.json is missing field %s" %(field))
            if meta[0][field] == "":
                return notvalid("psiturk.json must be defined for field %s" %(field))
            # Field value must have minimum of value entries
            if not isinstance(meta[0][field],list):
                tocheck = [meta[0][field]]
            else:
                tocheck = meta[0][field]
            if len(tocheck) < value:
                return notvalid("psiturk.json must have >= %s for field %s" %(value,field))
        # Run must be a list of strings
        if field == "run":
            # Is it a list?
            if not isinstance(meta[0][field],ftype):
                return notvalid("field %s must be %s" %(field,ftype))
            # Is each script in the list a string?
            for script in meta[0][field]:
                # If we have a single file, is it in the experiment folder?
                if len(script.split("/")) == 1:
                    if not os.path.exists("%s/%s" %(experiment_folder,script)):
                        return notvalid("%s is missing in %s." %(script,experiment_folder))
    return True   


"""
get_experiments
return loaded json for all valid experiments from an 
experiment folder

"""
def get_experiments(experiment_repo,load=False):
    experiments = find_directories(experiment_repo)
    valid_experiments = [e for e in experiments if validate(e)]
    print "Found %s valid experiments" %(len(valid_experiments))
    if load == True:
        valid_experiments = load_experiments(valid_experiments)
    return valid_experiments

"""
load_experiments
a wrapper for load_experiment to read multiple experiments
"""
def load_experiments(experiment_folders):
    experiments = []
    if isinstance(experiment_folders,str):
        experiment_folders = [experiment_folders]
    for experiment_folder in experiment_folders:
        exp = load_experiment(experiment_folder)
        experiments.append(exp)
    return experiments

"""

load_experiment:
read in the psiturk.json for an experiment folder

"""
def load_experiment(experiment_folder):
    fullpath = os.path.abspath(experiment_folder)
    psiturkjson = "%s/psiturk.json" %(fullpath)
    if not os.path.exists(psiturkjson):
        return notvalid("psiturk.json could not be found in %s" %(experiment_folder))
    try: 
        meta = json.load(open(psiturkjson,"r"))
        meta = remove_unicode_dict(meta[0])
        return [meta]
    except ValueError as e:
        print "Problem reading psiturk.json, %s" %(e)
        
