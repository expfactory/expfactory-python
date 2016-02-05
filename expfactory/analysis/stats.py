'''
analysis/stats.py: part of expfactory package
stats functions

'''
from expfactory.analysis.maths import check_numeric
import scipy.stats as stats
import seaborn as sns
import pandas
import numpy
import sys

def compute_contrast(df, dep_var, ind_var, plot=True):
    '''compute_contrast calculates a contrast (either pearson correlation for numeric or ttest for not) between two variables in the data frame
    :param dep_var: dependent variable, must be column in data frame
    :param ind_var: independent variable, must be column in data frame
    :param plot: boolean to return plot object in result (default True)
    :return results: dict that includes t statistic or correlation, prob (two tailed p value), and plot
    '''
    results = dict()

    if dep_var and ind_var in df.columns:
        result = 'undefined'
        iv_vec = df[ind_var]
        dv_vec = df[dep_var]
        if (check_numeric(iv_vec) and check_numeric(dv_vec)):
            corr,pval = stats.stats.pearsonr(iv_vec,dv_vec) # most results can be computed with regression. These are stand ins
            results["corr"] = corr
            results["pval"] = pval 
            if plot == True:
                results["plot"] = sns.jointplot(ind_var,dep_var, data = df)
        else:
            iv_labels = pandas.unique(iv_vec)
            print("Found %s independent variables: %s" %(len(iv_labels),",".join(iv_labels.tolist())))
            if (len(iv_labels) == 2):
                vals1 = df[iv_vec == iv_labels[0]][dep_var]
                vals2 = df[iv_vec == iv_labels[1]][dep_var]
                tstat, pval = stats.ttest_ind(vals1,vals2) 
                results["tstat"] = tstat.tolist()
                results["pval_two_tailed"] = pval
                if plot == True:
                    results["plot"] = sns.boxplot(data = df, x = ind_var, y = dep_var)
    else:
        missing = [x for x in [dv,iv] if x not in df.columns]
        print "%s missing from data frame columns." %(",".join(missing))
    return results
