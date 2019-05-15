#!/usr/bin/python

"""
Test experiments
"""

import unittest
import shutil
from expfactory.experiment import validate, load_experiment, load_experiments, \
get_experiments, make_lookup
from expfactory.utils import copy_directory, get_installdir
import tempfile
import json
import os

class TestExperiment(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.battery_folder = "%s/testing/data" % self.pwd
        self.experiment = os.path.abspath("%s/testing/data/test_task/" %self.pwd)
        self.tmpdir = tempfile.mkdtemp()
        with open("%s/testing/data/test_task/config.json" %self.pwd,"r") as filey:
            self.config = json.load(filey)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_find_experiments(self):

        # Test loading experiment folder path
        experiments = get_experiments(self.battery_folder)
        print(experiments)
        self.assertEqual(len(experiments),1)
        self.assertTrue(isinstance(experiments[0],str))

        # Test loading experiment dictionary
        config = get_experiments(self.battery_folder,load=True)
        self.assertTrue(isinstance(config[0][0],dict))

        loaded_experiment = load_experiment(self.experiment)  
        self.assertTrue(isinstance(loaded_experiment[0],dict))

    def test_make_lookup(self):
        lookup = make_lookup([self.config],"exp_id")
        self.assertTrue("test_task" in lookup)

    def test_validate(self):
        validation = validate(self.experiment)
        self.assertTrue(validation)

        # Create temporary directory and test invalid config.json
        broken_experiment = "%s/broken_experiment" %self.tmpdir
        copy_directory(self.experiment,broken_experiment)

        # Missing file specified
        shutil.copyfile("%s/experiment.js" %broken_experiment,"%s/pizza.js" %broken_experiment)
        os.remove("%s/experiment.js" %broken_experiment)
        self.assertFalse(validate(broken_experiment))
        shutil.copyfile("%s/pizza.js" %broken_experiment,"%s/experiment.js" %broken_experiment)

        # Invalid field for template
        broken_config = self.config[:]
        broken_config[0]["template"] = "invalid_framework"
        self.save_config(broken_config,broken_experiment)
        self.assertFalse(validate(broken_experiment))

        # Missing required field
        broken_config = self.config[:]
        del broken_config[0]["exp_id"]
        self.save_config(broken_config,broken_experiment)
        self.assertFalse(validate(broken_experiment))

    def save_config(self,config_file,directory):
        with open("%s/config.json"% directory,"w") as filey:
            filey.writelines(json.dumps(config_file))

if __name__ == '__main__':
    unittest.main()
