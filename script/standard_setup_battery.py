#!/usr/bin/python

from psiturkpy.battery import generate
import sys

# Standard battery setup script
# This script will generate a battery for all valid experiments, taking as input
# a battery folder, an experiment folder, and an output directory.

battery_repo = sys.argv[1]
experiment_repo = sys.argv[2]
battery_dest = sys.argv[3]

generate(battery_repo,battery_dest,experiment_repo)
