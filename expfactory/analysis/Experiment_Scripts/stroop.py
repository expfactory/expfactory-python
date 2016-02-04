# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 00:06:21 2016

@author: ian
"""
import sys
sys.path.insert(0, '../') # there must be a better way to do this

import pandas as pd
import numpy as np
import seaborn as sns
import scipy.stats as stats
from utils import load_result

# load data frame
df = load_result('stroop_results.csv')

# *************************************
# **** Clean up Data Frame ************
# *************************************

def clean_df(df, drop_cols = [], kept_cols = []):
    """
    clean_df returns a pandas dataset after removing a set of default generic 
    columns. Optional variable drop_cols allows more columns to be dropped
    while the columns in kept_cols will be kept in the final data frame
    """
    # Drop unnecessary columns
    drop_columns= ['view_history', 'stimulus', 'trial_index', 'internal_node_id', 
                    'time_elapsed', 'exp_id', 'stim_duration', 'block_duration', 
                    'feedback_duration','timing_post_trial'] + drop_cols
    drop_columns = [i for i in drop_columns if i not in kept_cols]
    df.drop(drop_columns, axis = 1, inplace = True, errors = 'ignore')
    
    drop_trial_ids = ['welcome', 'instruction', 'attention_check','end']
    # Drop unnecessary columns
    df = df.query('trial_id not in  @drop_trial_ids')
    return df
    
df = clean_df(df)


# *************************************
# **** Compute Contrast ***************
# *************************************
def compute_contrast(df, dv, iv):
    """
    
    """
    def check_numeric(v):
        if (v.dtype == np.float64 or v.dtype == np.int64):
            return True
        else:
            return False
    rs = 'undefined'
    df = df.dropna()
    iv_vec = df[iv]
    dv_vec = df[dv]
    if (check_numeric(iv_vec) and check_numeric(dv_vec)):
        rs = stats.stats.pearson(iv_vec,dv_vec) # most results can be computed with regression. These are stand ins
        sns.jointplot(iv,dv, data = df)
    else:
        iv_labels = pd.unique(iv_vec)
        print(len(iv_labels))
        if (len(iv_labels) == 2):
            vals1 = df[iv_vec == iv_labels[0]][dv]
            vals2 = df[iv_vec == iv_labels[1]][dv]
            rs = stats.ttest_ind(vals1,vals2) 
        sns.boxplot(data = df, x = iv, y = dv)
    return rs
