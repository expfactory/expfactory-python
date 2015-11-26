#!/usr/bin/python

from efactory.vm import custom_battery_download
import sys

# Standard battery setup script
# This script will generate a battery for all valid experiments, taking as input
# a battery folder, an experiment folder, and an output directory.

battery_dest = sys.argv[1]

custom_battery_download(tmpdir=battery_dest,repos=["experiments","battery","vm"])
