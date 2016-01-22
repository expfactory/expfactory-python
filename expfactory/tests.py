'''
tests.py: part of expfactory package
tests for experiments and batteries, not for expfactory-python

'''
from selenium import webdriver
from expfactory.experiment import validate, get_experiments
from numpy.testing import assert_equal, assert_string_equal
from selenium.webdriver.common.keys import Keys
from expfactory.utils import find_directories, get_url
from numpy.random import choice
from threading import Thread
import SimpleHTTPServer
from time import sleep
import SocketServer
import webbrowser
import requests
import numpy
import json
import re
import sys
import os

# subclass SimpleHTTPServer to capture error messages
class ExpfactoryServer(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write("%s - - [%s] %s\n" %
                     (self.address_string(),
                      self.log_date_time_string(),
                      format%args))
        # This is a workaround for jspsych error trying to GET html
        if not re.search("div",format%args) and not re.search("function",format%args):
            if re.search("404",format%args):
                # closing server will trigger error
                raise IOError(format%args)
    def log_error(self, format, *args):
        # We will catch errors in log_messages
        pass

def validate_experiment_directories(experiment_folder):
    experiments = find_directories(experiment_folder)
    for contender in experiments:
        assert_equal(validate(contender),True)


def key_lookup(keyid):
    lookup = {13:Keys.ENTER,
             8:Keys.BACKSPACE,
             9:Keys.TAB,
             16:Keys.SHIFT,
             17:Keys.CONTROL,
             18:Keys.ALT,
             19:Keys.PAUSE,
             27:Keys.ESCAPE,
             32:Keys.SPACE,
             33:Keys.PAGE_UP,
             34:Keys.PAGE_DOWN,
             35:Keys.END,
             36:Keys.HOME,
             37:Keys.LEFT,
             38:Keys.UP,
             39:Keys.RIGHT,
             40:Keys.DOWN,
             45:Keys.INSERT,
             46:Keys.DELETE,
             48:"0",
             49:"1",
             50:"2",
             51:"3",
             52:"4",
             53:"5",
             54:"6",
             55:"7",
             56:"8",
             57:"9",
             65:"a",
             66:"b",
             67:"c",
             68:"d",
             69:"e",
             70:"f",
             71:"g",
             72:"h",
             73:"i",
             74:"j",
             75:"k",
             76:"l",
             77:"m",
             78:"n",
             79:"o",
             80:"p",
             81:"q",
             82:"r",
             83:"s",
             84:"t",
             85:"u",
             86:"v",
             87:"w",
             88:"x",
             89:"y",
             90:"z",
             96:Keys.NUMPAD0,
             97:Keys.NUMPAD1,
             98:Keys.NUMPAD2,
             99:Keys.NUMPAD3,
             100:Keys.NUMPAD4,
             101:Keys.NUMPAD5,
             102:Keys.NUMPAD6,
             103:Keys.NUMPAD7,
             104:Keys.NUMPAD8,
             105:Keys.NUMPAD8,
             106:Keys.MULTIPLY,
             107:Keys.ADD,
             109:Keys.SUBTRACT,
             110:Keys.DECIMAL,
             111:Keys.DIVIDE,
             112:Keys.F1,
             113:Keys.F2,
             114:Keys.F3,
             115:Keys.F4,
             116:Keys.F5,
             117:Keys.F6,
             118:Keys.F7,
             119:Keys.F8,
             120:Keys.F9,
             121:Keys.F10,
             122:Keys.F11,
             123:Keys.F12,
             186:Keys.SEMICOLON,
             187:Keys.EQUALS}
    return lookup[keyid]

def experiment_robot_web(experimentweb_base,experiment_tags=None,port=None,pause_time=2000):
    '''experiment_robot_web
    Robot to automatically run and test experiments, to work with an experiment web folder (meaning produced with views.get_experiment_web. This folder has the standard battery structure with experiment pre-generated as html files. A separate function will/should eventually be made for single experiment preview.
    :param experiment_folders: list of experiment folders to test
    :param pause_time: time to wait between tasks, in addition to time specified in jspsych
    '''
    experimentweb_base = os.path.abspath(experimentweb_base)

    if port == None:
        port = choice(range(8000,9999),1)[0]
    Handler = ExpfactoryServer
    httpd = SocketServer.TCPServer(("", port), Handler)
    server = Thread(target=httpd.serve_forever)
    server.setDaemon(True)
    server.start()

    # Set up a web browser
    os.chdir(experimentweb_base)
    browser = get_browser() # will need to figure out how to do this on circle
    browser.implicitly_wait(3) # if error, will wait 3 seconds and retry
    browser.set_page_load_timeout(10)

    # Find experiments 
    experiments = get_experiments("%s/static/experiments" %experimentweb_base,load=True)

    if experiment_tags != None:
        experiments = [e for e in experiments if e[0]["tag"] in experiment_tags]
    
    # If we are running on circle, only test changed experiments
    if "CIRCLE_BRANCH" in os.environ.keys():

        print "DETECTED CONTINUOUS INTEGRATION ENVIRONMENT..."

        current_build = int(os.environ["CIRCLE_BUILD_NUM"])

        current_build_url = "https://circleci.com/api/v1/project/expfactory/expfactory-experiments/%s" %(current_build)
        headers = {'Accept' : 'application/json'}
        current_build = requests.get(current_build_url, headers=headers).json()

        # Get the last commit id
        last_successful_build = current_build["previous_successful_build"]["build_num"]
        last_successful_build_url = "https://circleci.com/api/v1/project/expfactory/expfactory-experiments/%s" %(last_successful_build)
        last_build = requests.get(last_successful_build_url, headers=headers).json()

        # Compare commits
        current_commit = current_build["all_commit_details"][-1]["commit"]
        last_commit = last_build["all_commit_details"][-1]["commit"]
        files_changed  = os.popen("git diff %s %s --name-only" %(current_commit,last_commit)).readlines()

        # Get unique, changed folders, filter experiments again
        experiment_tags = numpy.unique([os.path.dirname(x.strip("\n")) for x in files_changed if os.path.dirname(x.strip("\n")) != ""]).tolist()
        experiments = [e for e in experiments if e[0]["tag"] in experiment_tags]
        print "Found %s changed experiments to test." %(len(experiments))

    else:
        print "Found %s experiments to test." %(len(experiments))

    for experiment in experiments:
 
        print "STARTING TEST OF EXPERIMENT %s" %(experiment[0]["tag"])
        get_page(browser,"http://localhost:%s/%s.html" %(port,experiment[0]["tag"]))
        
        sleep(3)

        count=0
        wait_time=1000
        while True:

            # Is the task finished?
            finished = browser.execute_script("return expfactory_finished;")
            if finished == True:
                break

            print "Testing block %s of %s" %(count,experiment[0]["tag"])

            # Pause from the last block
            sleep(float(pause_time)/1000 + wait_time/1000) # convert milliseconds to seconds
            wait_time = 0

            # Get the current trial (not defined on first page)
            block = browser.execute_script("return jsPsych.currentTrial();")

            wait_time = wait_time + pause_time
            if "timing_post_trial" in block:
                wait_time = wait_time + block["timing_post_trial"]
            if "timing_feedback_duration" in block:
                wait_time = wait_time + block["timing_feedback_duration"]

            # This is typically for instruction text, etc.
            if "pages" in block:
                number_pages = len(block["pages"])
                for p in range(number_pages):
                    if "cont_key" in block:
                        continue_key = key_lookup(block["cont_key"][0])
                        browser.find_element_by_tag_name('html').send_keys(continue_key)
                    elif "show_clickable_nav" in block:
                        if block["show_clickable_nav"] == True:   
                            browser.execute_script("document.querySelector('#jspsych-instructions-next').click();")
                    # Give time for page to reload 
                    sleep(1)

            # This is for the experiment
            elif "timeline" in block:
                timeline = block["timeline"]
                for time in timeline:
                    if "choices" in block:
                        if len(block["choices"])>0:
                            choices = block["choices"]
                            # Make a random choice
                            random_choice = choice(choices,1)[0]
                            continue_key = key_lookup(random_choice)
                            browser.find_element_by_tag_name('html').send_keys(continue_key)
                    elif "button_class" in time:
                        browser.execute_script("document.querySelector('.%s').click();" %time["button_class"])
                    # Give time for page to reload 
                    sleep(1)

            elif "button_class" in block:
                browser.execute_script("document.querySelector('.%s').click();" %block["button_class"])

            elif "cont_key" in block:
                continue_key = key_lookup(block["cont_key"][0])
                browser.find_element_by_tag_name('html').send_keys(continue_key)

            elif "choices" in block:
                choices = block["choices"]
                random_choice = choice(choices,1)[0]
                continue_key = key_lookup(random_choice)
                browser.find_element_by_tag_name('html').send_keys(continue_key)

            # Free text response
            elif "type" in block:
                if re.search("survey-text",block["type"]):
                    browser.execute_script("document.querySelector('#jspsych-survey-text-next').click();")
                 
            count+=1

        print "FINISHING TEST OF EXPERIMENT %s" %(experiment[0]["tag"])

    # Stop the server
    httpd.server_close()

def check_errors(browser):
   
    # Look at log from last call
    log = browser.get_log("browser")
    for log_entry in log:
        assert_equal(log_entry["level"] in ["WARNING","INFO"],True)

def get_browser():
    return webdriver.Firefox()
    
def get_page(browser,url):
    browser.get(url)

# Run javascript and get output
def run_javascript(browser,code):
    return browser.execute_script(code)
