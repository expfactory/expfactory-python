'''
logman.py: he prints the logs

The error names (prefix) and integer level are assigned as follows:

ABRT -4
ERROR -3
WARNING -2
LOG -1
QUIET 0
INFO 1
VERBOSE 2
VERBOSE2 3
DEBUG 4

VERBOSE is equivalent to VERBOSE1 (this is mirroring the C code)
and for each level, calling it corresponds to calling the class'
function for it. E.g., DEBUG --> bot.debug('This is the message!')

The following levels are to stderr:

4,3,2,1,-1,-2,-3,-4

The following levels are only to stdout

1

The following levels do nothing (quiet)

0

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

import os
import sys

ABRT = -4
ERROR = -3
WARNING = -2
LOG = -1
QUIET = 0
INFO = 1
VERBOSE = 2
VERBOSE2 = 3
DEBUG = 4


class ExpfactoryMessage:

    def __init__(self,MESSAGELEVEL=None):
        self.level = get_logging_level()
        self.history = []
        self.errorStream = sys.stderr
        self.outputStream = sys.stdout
        self.colorize = self.useColor()
        self.colors = {ABRT:"\033[31m",    # dark red
                       ERROR: "\033[91m",  # red
                       WARNING:"\033[93m", # dark yellow
                       LOG:"\033[95m",     # purple
                       DEBUG:"\033[36m",   # cyan
                       'OFF':"\033[0m"}    # end sequence


    # Colors --------------------------------------------

    def useColor(self):
        '''useColor will determine if color should be added
        to a print. Will check if being run in a terminal, and
        if has support for asci'''
        COLORIZE = get_user_color_preference()
        if COLORIZE is not None:
            return COLORIZE
        streams = [self.errorStream,self.outputStream]
        for stream in streams:
            if not hasattr(stream, 'isatty'):
                return False
            if not stream.isatty():
                return False
        return True


    def addColor(self,level,text):
        '''addColor to the prompt (usually prefix) if terminal
        supports, and specified to do so'''
        if self.colorize:
            if level in self.colors:
                text = "%s%s%s" %(self.colors[level],
                                  text,
                                  self.colors["OFF"])
        return text


    def emitError(self,level):
        '''determine if a level should print to
        stderr, includes all levels but INFO and QUIET'''
        if level in [ABRT,
                     ERROR,
                     WARNING,
                     LOG,
                     VERBOSE,
                     VERBOSE2,
                     DEBUG ]:
            return True
        return False


    def emitOutput(self,level):
        '''determine if a level should print to stdout
        only includes INFO'''
        if level in [INFO]:
            return True
        return False


    def isEnabledFor(self,messageLevel):
        '''check if a messageLevel is enabled to emit a level
        '''
        if messageLevel <= self.level:
            return True
        return False


    def emit(self,level,message,prefix=None):
        '''emit is the main function to print the message
        optionally with a prefix
        :param level: the level of the message
        :param message: the message to print
        :param prefix: a prefix for the message
        '''

        if prefix is not None:
            prefix = self.addColor(level,"%s " %(prefix))
        else:
            prefix = ""
            message = self.addColor(level,message)

        # Add the prefix 
        message = "%s%s" %(prefix,message)

        if not message.endswith('\n'):
            message = "%s\n" %message

        # If the level is quiet, only print to error
        if self.level == QUIET:
            pass

        # Otherwise if in range print to stdout and stderr
        elif self.isEnabledFor(level):
            if self.emitError(level):
                self.write(self.errorStream,message)
            else:
                self.write(self.outputStream,message)

        # Add all log messages to history
        self.history.append(message)


    def write(self,stream,message):
        '''write will write a message to a stream, 
        first checking the encoding
        '''
        if isinstance(message,bytes):
            message = message.decode('utf-8')
        stream.write(message)


    def get_logs(self,join_newline=True):
        ''''get_logs will return the complete history, joined by newline
        (default) or as is.
        '''
        if join_newline:
            return '\n'.join(self.history)
        return self.history
        


    def show_progress(self,iteration,total,length=40,min_level=0,prefix=None,
                      carriage_return=True,suffix=None,symbol=None):
        '''create a terminal progress bar, default bar shows for verbose+
        :param iteration: current iteration (Int)
        :param total: total iterations (Int)
        :param length: character length of bar (Int)
        '''
        percent = 100 * (iteration / float(total))
        progress = int(length * iteration // total)

        if suffix is None:
            suffix = ''

        if prefix is None:
            prefix = 'Progress'

        # Download sizes can be imperfect, setting carriage_return to False
        # and writing newline with caller cleans up the UI
        if percent >= 100:
            percent = 100
            progress = length

        if symbol is None:
            symbol = "="

        if progress < length:
            bar = symbol * progress + '|' + '-' * (length - progress - 1)
        else:
            bar = symbol * progress + '-' * (length - progress)

        # Only show progress bar for level > min_level
        if self.level > min_level:
            percent = "%5s" %("{0:.1f}").format(percent)
            output = '\r' + prefix +  " |%s| %s%s %s" % (bar, percent, '%', suffix)            
            sys.stdout.write(output),
            if iteration == total and carriage_return: 
                sys.stdout.write('\n')
            sys.stdout.flush()



    def abort(self,message):
        self.emit(ABRT,message,'ABRT')        

    def error(self,message):
        self.emit(ERROR,message,'ERROR')        

    def warning(self,message):
        self.emit(WARNING,message,'WARNING')        

    def log(self,message):
        self.emit(LOG,message,'LOG')        

    def info(self,message):
        self.emit(INFO,message)        

    def verbose(self,message):
        self.emit(VERBOSE,message,"VERBOSE")        

    def verbose2(self,message):
        self.emit(VERBOSE2,message,'VERBOSE2')        

    def debug(self,message):
        self.emit(DEBUG,message,'DEBUG')        

    def is_quiet(self):
        '''is_quiet returns true if the level is under 1
        '''
        if self.level < 1:
            return False
        return True
    

def get_logging_level():
    '''get_logging_level will configure a logging to standard out based on the user's
    selected level, which should be in an environment variable called
    '''
    return int(os.environ.get("EXPFACTORY_MESSAGELEVEL",4))
    

def get_user_color_preference():
    COLORIZE = os.environ.get('EXPFACTORY_COLORIZE',None)
    if COLORIZE is not None:
        COLORIZE = convert2boolean(COLORIZE)
    return COLORIZE


def convert2boolean(arg):
  '''convert2boolean is used for environmental variables that must be
  returned as boolean'''
  if not isinstance(arg,bool):
      return arg.lower() in ("yes", "true", "t", "1","y")
  return arg


bot = ExpfactoryMessage()
