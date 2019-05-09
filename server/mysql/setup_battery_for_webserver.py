from expfactory.battery import *
from expfactory.utils import copy_directory
from expfactory.vm import download_repo
import argparse
from glob import glob
import os
import sys
import shutil
import tempfile


# Get CLI parameters
parser = argparse.ArgumentParser()
parser.add_argument('--output', dest="output", help='Battery output directory.')
parser.add_argument('--experiments', dest="experiments", help='Experiment(s) to use in the battery, separated by commas.')
parser.add_argument('--workingdir', dest="workingdir", help='Working directory, existing GIT repos are used if present and are not removed after execution.',default=None)

try:
    args = parser.parse_args()
except:
    parser.print_help()
    sys.exit(0)

if args.output == None or args.experiments == None:
    print("Output and experiments parameters are mandatory.")
    parser.print_help()
    sys.exit(1)

if os.path.exists(args.output):
    print("Output directory should not exist, remove and run again.")
    sys.exit(1)

battery_dest = args.output
working_dir = args.workingdir
is_temp_working_dir = False

script_dirname=os.path.dirname(__file__)
if script_dirname == "":
    script_dirname="."

if working_dir != None:
    if not (os.path.isdir(working_dir)):
        print("Working directory does not exist!")
        sys.exit(1)
else:
    is_temp_working_dir = True
    working_dir = tempfile.mkdtemp() # We will set up the repo downloads, etc, in a temporary place

experiments = args.experiments.split(",")

# Download the missing repos to working directory
battery_repo='battery'
experiment_repo='experiments'
survey_repo='surveys'
game_repo='games'

print('Downloading expfactory repos...')
for repo in (battery_repo, experiment_repo, survey_repo, game_repo):
    folder = "%s/%s" %(working_dir,repo)
    if not (os.path.isdir(folder)):
        download_repo(repo_type=repo,
                      destination=folder)

# Generate battery with the experiment(s)
print('Generating base...')
base = generate_base(battery_dest=battery_dest,
                     tasks=experiments,
                     experiment_repo="%s/%s" %(working_dir,experiment_repo),
                     survey_repo="%s/%s" %(working_dir,survey_repo),
                     game_repo="%s/%s" %(working_dir,game_repo),
                     add_experiments=True,
                     add_surveys=False,
                     add_games=False,
                     battery_repo="%s/%s" %(working_dir,battery_repo))

# Customize the battery
custom_variables = dict()
custom_variables["load"] = [("[SUB_TOTALTIME_SUB]", 30)]

template_exp = ("%s/templates/webserver-battery-template.html" %(script_dirname))
template_exp_output = "%s/index.html" %(battery_dest)

print('Generating experiment and battery templates...')

template_experiments(battery_dest=battery_dest,
                     battery_repo=base["battery_repo"],
                     valid_experiments=base["experiments"],
                     custom_variables=custom_variables,
                     template_exp=template_exp,
                     template_exp_output=template_exp_output)

# Copy needed php files there
add_files = glob("%s/*.php" %(script_dirname))
for add_file in add_files:
    shutil.copy(add_file, battery_dest)

# Cleanup
shutil.rmtree("%s/.git" %(battery_dest)) # Remove git data from the battery
if is_temp_working_dir:
    shutil.rmtree(working_dir)

print('Battery generated in %s' %(battery_dest))
