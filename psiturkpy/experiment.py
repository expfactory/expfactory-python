'''
experiment.py: part of psiturkpy package
Functions to work with javascript experiments

'''

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
            ("run",1,str),
            ("name",0,str), 
            ("contributors",0,str), 
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
valid:
takes an experiment folder, and looks for validation based on:

- psiturk.json
- files existing specified in psiturk.json

All fields should be defined, but for now we just care about run scripts
"""


def validate(experiment_folder):
    fullpath = os.path.abspath(experiment_folder)
    psiturkjson = "%s/psiturk.json" %(fullpath)
    if not os.path.exists(psiturkjson):
        return notvalid("psiturk.json could not be found in %s" %(experiment_folder))
    try: 
        meta = json.load(open(psiturkjson,"rb"))
        if len(meta)>1:
            return notvalid("psiturk.json has length > 1, not valid.")
        fields = get_validation_fields()
        for field,value,ftype in fields:
            if value != 0:
                if field not in meta[0].keys():
                    return notvalid("psiturk.json is missing field %s" %(field))
                if meta[0][field] < value:
                    return notvalid("psiturk.json must have >= %s for field %s" %(value,field))
        return True
    except ValueError as e:
        print "Problem reading psiturk.json, %s" %(e)
    
