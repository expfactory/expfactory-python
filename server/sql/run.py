#!/opt/conda/bin/python
import sys
import os
import tempfile
import argparse

# Get CLI parameters
parser = argparse.ArgumentParser()
parser.add_argument('--output', dest="output", help='Battery output directory',default=None)
parser.add_argument('--experiments', dest="experiments" help='Experiment(s) to use in the battery, separated by commas.')
parser.add_argument('--keep', default=False, action='store_true',help='Keep the config file for the battery generation')
args = parser.parse_args()

# If the user doesn't specify an output directory, use temporary
try:
    args = parser.parse_args()
except:
    parser.print_help()
    sys.exit(0)

battery_dest = args.output
if battery_dest == None:
    battery_dest = tempfile.mkdtemp()

experiments = ",".split(args.experiments)

# TODO Make config file with custom variables, also need to get DB params
#tmp = tempfile.mkftemp()
#config = open()

# Customize the battery
#custom_variables = dict()
#custom_variables["load"] = [("[SUB_TOTALTIME_SUB]", 30)]

template_exp = "webserver-battery-template.html"
template_exp_output = "%s/index.html" %(battery_dest)

template_experiments(battery_dest=battery_dest,
                     battery_repo=base["battery_repo"],
                     valid_experiments=base["experiments"],
                     custom_variables=custom_variables,
                     template_exp=template_exp,
                     template_exp_output=template_exp_output)

# Remove git data from the battery
shutil.rmtree("%s/.git" %(battery_dest))
