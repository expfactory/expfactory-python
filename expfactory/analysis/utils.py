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


def clean_df(df, drop_columns = None,drop_na=True):
    '''clean_df returns a pandas dataset after removing a set of default generic 
    columns. Optional variable drop_cols allows a different set of columns to be dropped
    :df: a pandas dataframe, loaded via load_result
    :param drop_columns: a list of columns to drop. If not specified, a default list will be used from utils.get_dropped_columns()
    '''
    # Drop unnecessary columns
    if drop_columns == None:
        drop_columns = get_drop_columns()   
    df.drop(drop_columns, axis=1, inplace=True, errors='ignore')
    drop_trial_ids = ['welcome', 'instruction', 'attention_check','end']
    # Drop unnecessary columns, all null rows
    df = df.query('trial_id not in  @drop_trial_ids')
    if drop_na == True:
        df = df.dropna()
    return df


def get_drop_columns():
    return ['view_history', 'stimulus', 'trial_index', 'internal_node_id', 
            'time_elapsed', 'exp_id', 'stim_duration', 'block_duration', 
            'feedback_duration','timing_post_trial']
