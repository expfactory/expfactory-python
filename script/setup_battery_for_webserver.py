#!/opt/conda/bin/python
from expfactory.battery import *
from expfactory.vm import download_repo
from expfactory.utils import get_installdir
import sys
import shutil
import os
import argparse

# Get CLI parameters
parser = argparse.ArgumentParser()
parser.add_argument('battery', help='Battery destination directory')
parser.add_argument('experiment', help='Experiment to use in the battery')
args = parser.parse_args()

experiments = [args.experiment]
battery_dest = args.battery

# Download the missing repos
battery_repo='battery'
experiment_repo='experiments'
survey_repo='surveys'
game_repo='games'

for repo in (battery_repo, experiment_repo, survey_repo, game_repo):
    if not (os.path.isdir(repo)):
        download_repo(repo, repo)

# Generate battery with the experiment
base = generate_base(battery_dest=battery_dest,
                     tasks=experiments,
                     experiment_repo=experiment_repo,
                     survey_repo=survey_repo,
                     game_repo=game_repo,
                     add_experiments=True,
                     add_surveys=False,
                     add_games=False,
                     battery_repo=battery_repo)

# Customize the battery
custom_variables = dict()
custom_variables["load"] = [("[SUB_TOTALTIME_SUB]", 30)]

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