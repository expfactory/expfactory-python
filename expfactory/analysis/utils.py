'''
analysis/utils.py: part of expfactory package
utils to perform analyses

'''

from expfactory.utils import find_directories, remove_unicode_dict
from glob import glob
import pandas
import json
import re
import os


def load_result(result):
    '''load_result returns a pandas data frame of a result variable, either a json data structure, a downloaded csv file from an individual experiment, or a tsv file exported from the expfactory-docker instance
    :param result: one of a csv (from jsPsych), tsv (from expfactory-docker) or json (from Jspsych)
    '''

    if isinstance(result,str):
        filey = os.path.abspath(result)
        file_name,ext = os.path.splitext(filey)

        if ext.lower() == ".csv":
            df = pandas.read_csv(result,sep=",")
        elif ext.lower() == ".tsv":
            df = pandas.read_csv(result,sep="\t")
        elif ext.lower() == ".json":
            df = pandas.read_json(result)
        else:
            print "File extension not recognized, must be .csv (JsPsych single experiment export) or tsv (expfactory-docker) export." 
 
    return df
    

