#!/usr/bin/env python

'''
script.py: part of expfactory api
Runtime executable

'''
from expfactory.views import preview_experiment, run_battery
from expfactory.experiment import validate
from glob import glob
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
    description="generate experiments and infrastructure to serve them.")
    parser.add_argument("--folder", dest='folder', help="full path to single experiment folder (for single experiment run with --run) or folder with many experiments (for battery run with --runbat)", type=str, default=None)
    parser.add_argument("--subid", dest='subid', help="subject id to embed in experiments data in the case of a battery run with --runbat", type=str, default=None)
    parser.add_argument("--experiments", dest='experiments', help="comma separated list of experiments for a local battery", type=str, default=None)
    parser.add_argument("--port", dest='port', help="port to preview experiment", type=int, default=None)
    parser.add_argument("--battery", dest='battery_folder', help="full path to local battery folder to use as template", type=str, default=None)
    parser.add_argument("--time", dest='time', help="maximum number of minutes for battery to endure, to select experiments", type=int, default=99999)
    parser.add_argument('--preview', help="preview an experiment locally (development function)", dest='preview', default=False, action='store_true')
    parser.add_argument('--run', help="run a single experiment or battery locally", dest='run', default=False, action='store_true')
    parser.add_argument('--validate', dest='validate', help="validate an experiment folder", default=False, action='store_true')
    parser.add_argument('--test', dest='test', help="test an experiment folder with the experiment robot", default=False, action='store_true')

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)

    # Check if the person wants to preview experiment or battery
    if args.preview == True:
        preview_experiment(folder=args.folder,battery_folder=args.battery_folder,port=args.port)

    # Run a local battery
    elif args.run == True:

        # Warn the user about using repos for experiments and battery
        if args.battery_folder == None:
            print "No battery folder specified. Will pull latest battery from expfactory-battery repo"

        if args.folder == None:
            print "No experiments folder specified. Will pull latest experiments from expfactory-experiments repo"

        if args.experiments != None:
            experiments = args.experiments.split(",")
            run_battery(experiments=experiments,
                        experiment_folder=args.folder,
                        subject_id=args.subid,
                        battery_folder=args.battery_folder,
                        port=args.port,
                        time=args.time)
        else:
            print "Please specify list of comma separated experiments with --experiments"

    # Validate a config.json
    elif args.validate == True:
        validate(experiment_folder=args.folder)

    # Run the experiment robot
    elif args.test == True:
        from expfactory.tests import test_experiment
        test_experiment(folder=args.folder,battery_folder=args.battery_folder,port=args.port)

    # Otherwise, just open the expfactory interface
    else:        
        from expfactory.interface import start
        start(port=args.port)    

if __name__ == '__main__':
    main()
