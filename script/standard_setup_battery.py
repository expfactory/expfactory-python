#!/usr/bin/python

from efactory.battery import generate
import sys

# Standard battery setup script
# This script will generate a battery for all valid experiments, taking as input
# a battery folder, an experiment folder, and an output directory.

battery_dest = sys.argv[1]

generate(battery_dest=battery_dest)
