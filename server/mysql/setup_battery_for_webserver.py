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
parser.add_argument('--output', dest="output", help='Battery output directory',default=None)
parser.add_argument('--experiments', dest="experiments", help='Experiment(s) to use in the battery, separated by commas.')

try:
    args = parser.parse_args()
except:
    parser.print_help()
    sys.exit(0)

if args.output != None:
    if os.path.exists(args.output):
        print("Output directory should not exist, remove and run again.")
        sys.exit(0)


# We will set up the repo downloads, etc, in a temporary place
working_dir = tempfile.mkdtemp()
experiments = ",".split(args.experiments)

# Download the missing repos
battery_repo='battery'
experiment_repo='experiments'
survey_repo='surveys'
game_repo='games'

# Download repos to working directory
print('Downloading expfactory repos...')
for repo in (battery_repo, experiment_repo, survey_repo, game_repo):
    folder = "%s/%s" %(working_dir,repo)
    if not (os.path.isdir(folder)):
        download_repo(repo_type=repo, 
                      destination=folder)

battery_dest = "%s/%s" %(working_dir,battery_repo)

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
                     battery_repo=battery_dest)

# Customize the battery
custom_variables = dict()
custom_variables["load"] = [("[SUB_TOTALTIME_SUB]", 30)]

template_exp = "templates/webserver-battery-template.html"
template_exp_output = "%s/index.html" %(base["battery_repo"])

print('Generating experiment and battery templates...')
template_experiments(battery_dest=base["battery_repo"],
                     battery_repo=base["battery_repo"],
                     valid_experiments=base["experiments"],
                     custom_variables=custom_variables,
                     template_exp=template_exp,
                     template_exp_output=template_exp_output)

# Copy needed php files there
add_files = glob("%s/*.php" %os.getcwd())
for add_file in add_files:
    shutil.copyfile(add_file,"%s/%s" %(base['battery_repo'],
                                       os.path.basename(add_file)))

# Remove git data from the battery
if args.output != None:
    copy_directory(base["battery_repo"],args.output)    
    battery_dest = args.output

print('Battery generated in %s' %(battery_dest))
shutil.rmtree(working_dir)
