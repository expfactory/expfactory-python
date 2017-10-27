#!/usr/bin/env python

'''
script.py: part of expfactory api
Runtime executable

Copyright (c) 2016-2017 Vanessa Sochat, Stanford University

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from glob import glob
import argparse
import sys
import os



def get_parser():

    parser = argparse.ArgumentParser(
    description="generate experiments and infrastructure to serve them.")

    parser.add_argument("--list", dest='list', 
                         help="list available experiments.", 
                         default=False, action='store_true')

    parser.add_argument("--experiments", dest='experiments', 
                         help="comma separated list of experiments for a local battery", 
                         type=str, default=None)

    parser.add_argument("--subid", dest='subid', 
                         help="subject id for saving database",
                         type=str, default=None)

    parser.add_argument("--base", dest='base', 
                         help="base folder with experiment subfolders (defaults to /scif/apps)",
                         type=str, default='/scif/apps')

    parser.add_argument("--port", dest='port', 
                         help="port to preview experiment", 
                         type=int, default=None)

    parser.add_argument("--time", dest='time',
                         help="maximum number of minutes for battery to endure, to select experiments",
                         type=int, default=99999)

    parser.add_argument('--run', dest="run",
                         help="run a single experiment/survey or battery locally",
                         default=False, action='store_true')

    #TODO: if the user does test or validate, just show all available and allow to choose- or make this default?
    parser.add_argument('--validate', dest='validate', help="validate an experiment folder", default=False, action='store_true')
    parser.add_argument('--test', dest='test', help="test an experiment folder with the experiment robot", default=False, action='store_true')
    return parser

    # STOPED HERE - create singularity image with experiments

def main():

    from expfactory.logman import bot
    # This will also import and set defaults

    parser = get_parser()

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)


    # Export environment variables for the client
    experiments = args.experiments
    if experiments is None:
        experiments = " ".join(glob("%s/*" %args.base))

    os.environ['EXPERIMENTS'] = experiments

    # Does the base folder exist?
    if not os.path.exists(args.base):
        bot.error("Base folder %s does not exist." %args.base)
        sys.exit(1)

    os.environ['EXPFACTORY_BASE'] = args.base
    os.environ['EXPFACTORY_SUBID'] = args.subid

    from expfactory.server import start
    start(port=args.port)

if __name__ == '__main__':
    main()
