#!/usr/bin/python

from psiturkpy.battery import generate

# Location of battery repo, and experiment repo
# In future, these will not be required
battery_repo = "/home/vanessa/Documents/Dropbox/Code/psiturk/psiturk-battery"
experiment_repo = "/home/vanessa/Documents/Dropbox/Code/psiturk/psiturk-experiments"
battery_dest = "/home/vanessa/Desktop/battery"

# Not specifying experiments will include all valid
generate(battery_repo,battery_dest,experiment_repo)
