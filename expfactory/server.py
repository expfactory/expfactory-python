'''
Copyright (c) 2016-2017 Vanessa Sochat

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

from expfactory.experiment import (
    get_experiments, 
    make_lookup,
    get_selection
)

from flask import Flask, render_template, request
from flask_restful import Resource, Api
from expfactory.logman import bot
from werkzeug import secure_filename
from expfactory.logman import bot
import jinja2
import tempfile
import shutil
import random
import sys
import os

# SERVER CONFIGURATION ##############################################
class EFServer(Flask):

    def __init__(self, *args, **kwargs):
            super(EFServer, self).__init__(*args, **kwargs)
 
            # Step 1: obtain installed and selected experiments (/scif/apps)
            self.selection = os.environ.get('EXPERIMENTS', [])
            self.base = os.environ.get('EXPFACTORY_BASE','/scif/apps')
            bot.log("User has selected: %s" %self.selection)
            available = get_experiments("%s" % self.base)
            bot.log("Experiments Available: %s" %"\n".join(available))

            # Create API endpoint to serve metadata
            self.experiments = get_selection(available, self.selection)
            self.lookup = make_lookup(self.experiments)
            bot.log("Final Set \n%s" %"\n".join(list(self.lookup.keys())))

            # Completed will go into list
            self.completed = []

app = EFServer(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg','gif'])

    
# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# This is how the command line version will run
def start(port=8088, debug=False):
    bot.info("Nobody ever comes in... nobody ever comes out...")
    app.run(host="0.0.0.0", debug=False,port=port)
    
if __name__ == '__main__':
    start()
