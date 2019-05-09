#!/usr/bin/python

"""
Test experiments
"""

import unittest
import shutil
from expfactory.experiment import get_experiments
from expfactory.battery import generate, get_experiment_run, get_load_js, \
get_concat_js, get_timing_js
from expfactory.utils import copy_directory, get_installdir
import tempfile
import json
import os
import re

class TestBattery(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.battery = "%s/battery"%self.tmpdir
        self.experiment = os.path.abspath("%s/testing/data/test_task/" %self.pwd)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        
    def test_experiment_run(self):
        experiment_run = get_experiment_run([self.experiment])
        self.assertTrue("test_task" in experiment_run)
        self.assertTrue(re.search("expfactory_finished",experiment_run["test_task"])!=None)

    def test_get_files(self):

        loadjs = get_load_js([self.experiment])
        self.assertTrue(re.search("test_task",loadjs)!=None)
        self.assertTrue(re.search("loadjscssfile",loadjs)!=None)
        self.assertTrue(re.search("experiment.js",loadjs)!=None)

        concatjs = get_concat_js([self.experiment])
        self.assertTrue(re.search("test_task",concatjs)!=None)
        self.assertTrue(re.search("experiments.concat",concatjs)!=None)

        timingjs = get_timing_js([self.experiment])
        self.assertTrue(timingjs[0]["name"]=="test_task")
        self.assertTrue(timingjs[0]["time"]==1)

if __name__ == '__main__':
    unittest.main()
