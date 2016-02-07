#!/usr/bin/python

"""
Test analysis functions
"""

from expfactory.analysis.utils import load_result, clean_df
from expfactory.analysis.stats import compute_contrast
from expfactory.analysis.maths import check_numeric
from expfactory.utils import get_installdir
import pandas
import tempfile
import unittest
import shutil
import json
import os
import re

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.csv = os.path.abspath("%s/testing/data/results/stroop_results.csv" %self.pwd)
        self.json = os.path.abspath("%s/testing/data/results/jsPsychData.json" %self.pwd)
        self.tsv = os.path.abspath("%s/testing/data/results/results_df.tsv" %self.pwd)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_check_numeric(self):
        not_numeric = ["hello","goodbye"]
        numeric_float = [1.1,2.2,3.3]
        numeric_int = [1,2,3]
        not_numeric_mixed = ["hello",2,3.0]
        self.assertTrue(check_numeric(numeric_float))
        self.assertTrue(check_numeric(numeric_int))
        self.assertTrue(check_numeric(not_numeric)==False)
        self.assertTrue(check_numeric(not_numeric_mixed)==False)

    def test_load_result(self):
        df = load_result(self.csv)
        self.assertTrue(isinstance(df,pandas.DataFrame))
        df = load_result(self.json)
        self.assertTrue(isinstance(df,pandas.DataFrame))
        df = load_result(self.tsv)
        self.assertTrue(isinstance(df,pandas.DataFrame))

    def test_clean_df(self):
        df = load_result(self.csv)
        df = clean_df(df)
        self.assertTrue(df.isnull().any().any()==False)

    def test_compute_contrast(self):
        df = load_result(self.csv)
        df = clean_df(df)
        result = compute_contrast(df,ind_var="condition",dep_var="rt")
        self.assertTrue(isinstance(result,dict))
        self.assertTrue(len([x for x in ["plot","pval_two_tailed","tstat"] if x in result.keys()])==3)

if __name__ == '__main__':
    unittest.main()
