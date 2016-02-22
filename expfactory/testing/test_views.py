#!/usr/bin/python

"""
Test experiments
"""

from expfactory.utils import copy_directory, get_installdir
from expfactory.vm import custom_battery_download
from expfactory.experiment import load_experiment
from expfactory.views import *
import tempfile
import unittest
import shutil
import json
import os
import re

class TestViews(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.experiment = os.path.abspath("%s/testing/data/test_task/" %self.pwd)
        self.config = json.load(open("%s/testing/data/test_task/config.json" %self.pwd,"rb"))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_embed_experiment(self):
        html_snippet = embed_experiment(self.experiment)
        self.assertTrue(re.search("<!DOCTYPE html>",html_snippet)!=None)
        self.assertTrue(re.search("style.css",html_snippet)!=None)
        self.assertTrue(re.search("experiment.js",html_snippet)!=None)
        self.assertTrue(re.search("test_task",html_snippet)!=None)

    def test_experiment_web(self):
       
        generate_experiment_web(self.tmpdir)
        self.assertTrue(os.path.exists("%s/templates" %self.tmpdir))
        self.assertTrue(os.path.exists("%s/static" %self.tmpdir))
        self.assertTrue(os.path.exists("%s/data" %self.tmpdir))
        self.assertTrue(os.path.exists("%s/index.html" %self.tmpdir))
        self.assertTrue(os.path.exists("%s/table.html" %self.tmpdir))

    def test_get_experiment_html(self):

        html_snippet = get_experiment_html(self.config,self.experiment)
        self.assertTrue(re.search("<!DOCTYPE html>",html_snippet)!=None)
        self.assertTrue(re.search("style.css",html_snippet)!=None)
        self.assertTrue(re.search("experiment.js",html_snippet)!=None)
        self.assertTrue(re.search("test_task",html_snippet)!=None)
                
    def test_cognitiveatlas_hierarchy(self):

        html_snippet = get_cognitiveatlas_hierarchy(get_html=True)
        self.assertTrue(re.search("<!DOCTYPE html>",html_snippet)!=None)
        self.assertTrue(re.search("The Experiment Factory",html_snippet)!=None)

    def test_tmp_experiment(self):
        battery = custom_battery_download("%s/battery"%self.tmpdir,repos=["battery"])
        tmp_exp = tmp_experiment(self.experiment,"%s/battery"%self.tmpdir)
        self.assertTrue(os.path.exists("%s/battery/static" %tmp_exp))
        self.assertTrue(os.path.exists("%s/battery/index.html" %tmp_exp))
        shutil.rmtree(tmp_exp)

if __name__ == '__main__':
    unittest.main()
