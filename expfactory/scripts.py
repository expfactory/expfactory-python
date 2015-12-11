#!/usr/bin/env python

'''
script.py: part of expfactory api
Runtime executable

'''
from expfactory.views import preview_experiment
from glob import glob
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
    description="generate experiments and infrastructure to serve them.")
    parser.add_argument("--folder", dest='folder', help="full path to experiment folder", type=str, default=None)
    parser.add_argument("--port", dest='port', help="port to preview experiment", type=int, default=None)
    parser.add_argument("--battery", dest='battery_folder', help="full path to local battery folder to use as template", type=str, default=None)
    parser.add_argument('--preview', dest='preview', default=False, action='store_true')

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    
    # Check if the person wants to preview experiment
    if args.preview == True:
        preview_experiment(folder=args.folder,battery_folder=args.battery_folder,port=args.port)
    else:        
        from expfactory.interface import start
        start(port=args.port)    

if __name__ == '__main__':
    main()
