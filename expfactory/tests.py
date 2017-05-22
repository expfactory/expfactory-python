'''
tests.py: part of expfactory package
tests for experiments and batteries, not for expfactory-python

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
from selenium.common.exceptions import WebDriverException, UnexpectedAlertPresentException, NoSuchElementException
from expfactory.experiment import validate, get_experiments, load_experiment, find_changed
from expfactory.views import generate_experiment_web, tmp_experiment
from expfactory.survey import read_survey_file, parse_questions, parse_validation
from numpy.testing import assert_equal, assert_string_equal
from expfactory.utils import find_directories, get_url
from selenium.webdriver.common.keys import Keys
from expfactory.vm import download_repo
from numpy.random import choice
from selenium import webdriver
from threading import Thread
import SimpleHTTPServer
from time import sleep
from logman import bot
import SocketServer
import webbrowser
import requests
import fnmatch
import pandas
import shutil
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

def get_web_server(port=None):
    '''get_web_server returns a httpd object (socket server) to run the experiment robot
    :param port: the port for the server, default is None will select one randomly between 8000 and 9999
    '''
    if port == None:
        port = choice(range(8000,9999),1)[0]
    Handler = ExpfactoryServer
    httpd = SocketServer.TCPServer(("", port), Handler)
    server = Thread(target=httpd.serve_forever)
    server.setDaemon(True)
    server.start()
    return httpd,port

## GENERAL VALIDATION #############################################################################


def validate_circle_yml(experiment_repo,repo_type="experiments"):
    '''validate_circle_yml will make sure that all experiment folders in a repo are tested with circle_ci_test in the circle.yml
    :param experiment_repo: the experiment repo folder that contains experiment subdirectories with config.json files
    '''
    if "CIRCLE_BRANCH" in os.environ.keys():
        circle_yml_file = "%s/circle.yml" %experiment_repo
        assert_equal(os.path.exists(circle_yml_file),True)
        circle_yml_file = open(circle_yml_file,"r")
        circle_yml = "".join([x.strip("\n").replace(" ","").replace("'","").replace('"',"") for x in circle_yml_file.readlines()])
        circle_yml = circle_yml.replace("(","").replace(")","")
        experiments = get_experiments(experiment_repo,load=True,warning=False,repo_type=repo_type)
        tags = [x[0]["exp_id"] for x in experiments] 

        for tag in tags:
            bot.log("TESTING if %s defined for circle ci testing in circle.yml..." %tag)
            if repo_type == "experiments":
                assert_equal(re.search("circle_ci_test%s" %tag,circle_yml)!=None,True)
            elif repo_type == "surveys":
                assert_equal(re.search("circle_ci_survey%s" %tag,circle_yml)!=None,True)
    else:
       bot.log("Not in a continuous integration (CircleCI) environment, skipping test.")
    bot.log("All experiments found in circle.yml for testing!")



## SURVEYS ########################################################################################

def circle_ci_survey(survey_tags,web_folder,survey_repo=None,delete=True,survey_file="survey.tsv"):
    '''circle_ci_survey checks format of surveys.tsv file
    :param survey_tags: list of survey folders (exp_id variables) to test
    :param web folder: folder with generated survey web
    :param survey_repo: folder with experiments to test. If None, will pull from master branch
    :param delete: delete experiment folders when finished
    '''

    if isinstance(survey_tags,str):
        survey_tags = [survey_tags]

    # If we are running on circle, only test changed experiments
    if "CIRCLE_BRANCH" in os.environ.keys():

        bot.log("DETECTED CONTINUOUS INTEGRATION ENVIRONMENT...")

        survey_repo = os.getcwd()
        master_folder = os.path.abspath(os.path.join(survey_repo,"master"))
        if not os.path.exists(master_folder):
            os.mkdir(master_folder)
            download_repo("surveys",master_folder)
        changed_surveys = [os.path.split(x)[-1] for x in find_changed(survey_repo,master_folder,repo_type="surveys")]    
        changed_surveys = [e for e in survey_tags if e in changed_surveys]
        
    if len(changed_surveys) > 0:
        validate_surveys(survey_tags=changed_surveys,survey_repo=survey_repo,survey_file=survey_file)
        generate_experiment_web(web_folder,survey_folder=os.path.abspath(survey_repo)) 
        survey_robot_web(web_folder,survey_tags=changed_surveys)
    else:
        bot.log("Skipping surveys %s, no changes detected." %",".join(survey_tags))


def validate_surveys(survey_tags,survey_repo,survey_file="survey.tsv",delim="\t",raise_error=True):
    '''validate_surveys validates an experiment factory survey folder
    :param survey_tags: a list of surveys to validate
    :param survey_repo: the survey repo with the survey folders to validate
    :param survey_file: the default file to validate
    :param raise_error: throw the error (meaning don't return True or False instead)
    '''
    if isinstance(survey_tags,str):
        survey_tags = [survey_tags]

    for survey_tag in survey_tags:
        try:
            survey_folder = "%s/%s" %(survey_repo,survey_tag)
            bot.log("Testing load of config.json for %s" %survey_folder)
            survey = load_experiment("%s" %survey_folder)
            survey_questions = "%s/%s" %(survey_folder,survey_file)       
            bot.log("Testing valid columns in %s" %survey[0]["exp_id"])
            df = read_survey_file(survey_questions,delim=delim)
            assert_equal(isinstance(df,pandas.DataFrame),True)
            bot.log("Testing survey generation of %s" %survey[0]["exp_id"])
            questions,required_count = parse_questions(survey_questions,
                                                       exp_id=survey[0]["exp_id"],
                                                       validate=True)
            bot.log("Testing validation generation of %s" %survey[0]["exp_id"])
            validation = parse_validation(required_count)
        except:
            if raise_error == False:
                return False
            raise
    return True


def survey_robot_web(web_folder,survey_tags=None,port=None,pause_time=100):
    '''survey_robot_web
    Robot to automatically click through surveys, to work with an experiment web folder (meaning produced with views.get_experiment_web. This folder has the standard battery structure with experiment pre-generated as html files. 
    :param web_folder: experimentweb generated folder with generate_experiment_web
    :param survey_tags: list of experiment folders to test
    :param pause_time: time to wait between tasks, in addition to time specified in jspsych
    :param port: port. Randomly selected if None is selected
    '''
    web_base = os.path.abspath(web_folder)
    httpd,port = get_web_server(port=port)

    # Set up a web browser
    os.chdir(web_base)
    browser = get_browser() 
    browser.implicitly_wait(3) # if error, will wait 3 seconds and retry
    browser.set_page_load_timeout(10)

    # Find surveys
    surveys = get_experiments("%s/static/surveys" %web_base,load=True,warning=False,repo_type="surveys")

    if survey_tags != None:
        surveys = [s for s in surveys if s[0]["exp_id"] in survey_tags]
    
    bot.log("Found %s surveys to test." %len(surveys))

    for survey in surveys:
 
        bot.log("STARTING TEST OF SURVEY %s" %survey[0]["exp_id"])
        get_page(browser,"http://localhost:%s/%s.html" %(port,survey[0]["exp_id"]))
        
        sleep(3)

        count=1
        while True:
            bot.log("Testing page %s of %s" %(count,survey[0]["exp_id"]))
            try:
                finished = advance_survey(browser,pause_time)
                if finished == True:
                    break
                count+=1
            except UnexpectedAlertPresentException:
                bot.log("Found alert: closing.")
                try:
                    alert = browser.switch_to_alert()
                    alert.accept()
                except:
                    pass

        bot.log("FINISHING TEST OF SURVEY %s" %(survey[0]["exp_id"]))

    # Stop the server
    httpd.server_close()


def advance_survey(browser,pause_time):
    '''advance_survey will click the next button and fill in current page question content / questions
    :param browser: the web browser generated with get_browser
    :param pause_time: time to pause between pages
    '''

    # Click all checkboxes and radio buttons
    browser.execute_script('$(":radio").click();')
    browser.execute_script('$(":checkbox").click();')

    # If there are text boxes on the page, fill them (numeric and regular)
    textfields = browser.execute_script('var elements = []; var tmp = $(".mdl-textfield__input"); $.each(tmp,function(i,e){elements.push(e)}); return elements;')
    for text in textfields:
        element_id = text.get_attribute('id')
        textbox_type = text.get_attribute('type')
        if textbox_type == "number":
            fill_input = str('$("input[id=%s]").val(711);' %(element_id))
        elif textbox_type == 'text':
            fill_input = str('$("input[id=%s]").val("beep boop!");' %(element_id))
        browser.execute_script(fill_input)
    
    # Click the forward button, click it
    forward = browser.find_element_by_class_name('forward').click()
    
    # Have we reached the end?
    finished = browser.execute_script("return expfactory_finished;")

    return finished    


## EXPERIMENTS ####################################################################################

def validate_experiment_tag(experiment_folder):
    '''validate_experiment_tag looks for definition of exp_id as the tag somewhere in experiment.js. We are only requiring one definition for now (a more lax approach), but this standard might be changed.
    '''
    experiments = find_directories(experiment_folder)
    bot.log("Testing %s experiment for definition of exp_id in experiment.js...")
    for contender in experiments:
        if validate(contender,warning=False) == True:
            experiment = load_experiment(contender)
            tag = experiment[0]["exp_id"]

            # Experiment MUST contain experiment.js to run main experiment
            bot.log("TESTING %s for exp_id in experiment.js..." %tag)
            assert_equal("experiment.js" in experiment[0]["run"],True)

            if "experiment.js" in experiment[0]["run"]:
                experiment_js_file = open("%s/%s/experiment.js" %(experiment_folder,tag),"r") 
                experiment_js_list = [x.strip("\n").replace("'","").replace('"',"").replace(" ","") for x in experiment_js_file.readlines()]
                experiment_js_file.close()
                experiment_js = "".join(experiment_js_list)
                [x]
                has_exp_id = re.search("exp_id:%s" %tag,experiment_js) != None or re.search("exp_id=%s" %tag,experiment_js) != None 
                assert_equal(has_exp_id,True)
                # Ensure all are formatted correctly
                exp_id_instances = [re.findall("exp_id[=|:].+",x) for x in experiment_js_list if len(re.findall("exp_id[=|:].+,",x)) != 0]
                line_numbers = [x+1 for x in range(len(experiment_js_list)) if len(re.findall("exp_id[=|:].+,",experiment_js_list[x])) != 0]
                for e in range(len(exp_id_instances)):
                    exp_id_instance = exp_id_instances[e]
                    line_number = line_numbers[e]
                    bot.log("Checking %s on line %s..." %(exp_id_instance[0],line_number))
                    assert_equal(re.search(tag,exp_id_instance[0])!=None,True) 


def circle_ci_test(experiment_tags,web_folder,experiment_repo=None,delete=True,pause_time=500,repo_type="experiments"):
    '''circle_ci_test
    Deploy experiment testing robot, requires generation of web folder, and can be deleted on finish.
    :param experiment_tags: list of experiment folders (exp_id variables) to test
    :param web_folder: output web folder to generate experiment web. Will be created if does not exist
    :param experiment_repo: folder with experiments to test. If None, will pull from master branch
    :param delete: delete experiment folders when finished
    :param pause_time: The time to pause between experiments, in addition to post trial times
    '''

    if isinstance(experiment_tags,str):
        experiment_tags = [experiment_tags]

    # If we are running on circle, only test changed experiments
    if "CIRCLE_BRANCH" in os.environ.keys():

        bot.log("DETECTED CONTINUOUS INTEGRATION ENVIRONMENT...")

        master_folder = os.path.abspath(os.path.join(os.getcwd(),"master"))
        if not os.path.exists(master_folder):
            os.mkdir(master_folder)
            download_repo(repo_type,master_folder)
        changed_experiments = [os.path.split(x)[-1] for x in find_changed(os.getcwd(),master_folder)]    
        changed_experiments = [e for e in experiment_tags if e in changed_experiments]
        
    if len(changed_experiments) > 0:
        generate_experiment_web(web_folder,experiment_folder=os.path.abspath(experiment_repo),make_surveys=False) 
        experiment_robot_web(web_folder,experiment_tags=changed_experiments)
    else:
        bot.log("Skipping %s %s, no changes detected." %(repo_type,",".join(experiment_tags)))
        

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
             187:Keys.EQUALS,
             "leftarrow":Keys.LEFT,
             "rightarrow":Keys.RIGHT,
             "uparrow":Keys.UP,
             "downarrow":Keys.DOWN}
    if keyid not in lookup.keys():
        if isinstance(keyid,str) or isinstance(keyid,unicode):
            return str(keyid.lower())
    return lookup[keyid]

def experiment_robot_web(web_folder,experiment_tags=None,port=None,pause_time=100):
    '''experiment_robot_web
    Robot to automatically run and test experiments, to work with an experiment web folder (meaning produced with views.get_experiment_web. This folder has the standard battery structure with experiment pre-generated as html files. 
    :param web_folder: experimentweb generated folder with generate_experiment_web
    :param experiment_tags: list of experiment folders to test
    :param pause_time: time to wait between tasks, in addition to time specified in jspsych
    :param port: port. Randomly selected if None is selected
    '''
    experimentweb_base = os.path.abspath(web_folder)

    httpd,port = get_web_server(port=port)

    # Set up a web browser
    os.chdir(experimentweb_base)
    browser = get_browser() 
    browser.implicitly_wait(3) # if error, will wait 3 seconds and retry
    browser.set_page_load_timeout(10)

    # Find experiments 
    experiments = get_experiments("%s/static/experiments" %experimentweb_base,load=True,warning=False)

    if experiment_tags != None:
        experiments = [e for e in experiments if e[0]["exp_id"] in experiment_tags]
    
    bot.log("Found %s experiments to test." %len(experiments))

    for experiment in experiments:
 
        bot.log("STARTING TEST OF EXPERIMENT %s" %experiment[0]["exp_id"])
        get_page(browser,"http://localhost:%s/%s.html" %(port,experiment[0]["exp_id"]))
        
        sleep(3)

        count=0
        wait_time=0
        while True:
            bot.log("Testing command %s of %s" %count,experiment[0]["exp_id"])
            try:
                wait_time,finished = test_block(browser,experiment,pause_time,wait_time)
                if finished == True:
                    break
                count+=1
            except UnexpectedAlertPresentException:
                bot.log("Found alert: closing.")
                try:
                    alert = browser.switch_to_alert()
                    alert.accept()
                except:
                    pass

        bot.log("FINISHING TEST OF EXPERIMENT %s" %(experiment[0]["exp_id"]))

    # Stop the server
    httpd.server_close()

def test_block(browser,experiment,pause_time=0,wait_time=0):
    '''test_block
    test a single experiment block, given a browser, running experiment, and pause/wait times
    :param browser: web browser, by way of selenium
    :param pause_time: time to wait between tasks, in addition to time specified in jspsych
    :param wait_time: initial wait time, or previously generated wait time based on experiment
    '''
    # Is the task finished?
    finished = browser.execute_script("return expfactory_finished;")

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
    if "pages" in block and not re.search("survey-multi-choice",block["type"]):
        number_pages = len(block["pages"])
        for p in range(number_pages):
            if "cont_key" in block:
                continue_key = get_continue_key(block)
            elif "show_clickable_nav" in block:
                if block["show_clickable_nav"] == True:  
                    try:  
                        browser.execute_script("document.querySelector('#jspsych-instructions-next').click();")
                    except WebDriverException as e:
                        pass
            elif 'key_forward' in block:
                continue_key = key_lookup(block["key_forward"])
                browser.find_element_by_tag_name('html').send_keys(continue_key)
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
        try:
            buttons = browser.find_elements_by_class_name('%s' %block["button_class"])
            button = choice(buttons,1)[0]
            if button.is_enabled() == False:
                browser.execute_script('document.getElementsByClassName("%s")[0].disabled = false' %block["button_class"])
            button.click()
            sleep(0.5)
        except WebDriverException as e:
            pass


    elif "cont_key" in block:
        continue_key = get_continue_key(block)
        browser.find_element_by_tag_name('html').send_keys(continue_key)

    elif "choices" in block:
        choices = block["choices"]
        if choices != None and len(choices) > 0:
            try:
                random_choice = choice(choices,1)[0]
                continue_key = key_lookup(random_choice)
                browser.find_element_by_tag_name('html').send_keys(continue_key)
            except ValueError:
                bot.log("ValueError, %s found as choices." %(choices))
        else:
                browser.find_element_by_tag_name('html').send_keys(Keys.ENTER)
        if "type" in block:
            if "type" == "writing":
                browser.execute_script("document.querySelector('#jspsych-writing-box').text = 'beep boop';")

    if "type" in block:
        # Radio buttons
        if re.search("survey-multi-choice",block["type"]):
            try:    
                browser.execute_script("$(':radio').click();");
                sleep(1)
                browser.execute_script("document.querySelector('#jspsych-survey-multi-choice-next').click();")
            except WebDriverException as e:
                pass


        elif re.search("radio-buttonlist",block["type"]):
            try:    
                browser.execute_script("$(':radio').click();");
                sleep(2)
                browser.execute_script("document.querySelector('#jspsych-radio-buttonlist-next').click();")
            except WebDriverException as e:
                pass

        # Free text response
        elif re.search("survey-text",block["type"]):
            try:    
                browser.execute_script("document.querySelector('#jspsych-survey-text-next').click();")
            except WebDriverException as e:
                pass

    elif "key_answer" in block:
        continue_key = get_continue_key(block,block_tag="key_answer")
        browser.find_element_by_tag_name('html').send_keys(continue_key)

    elif len(block) == 0:
        # Check for fullscreen
        fullscreen = browser.execute_script("return jsPsych.initSettings().fullscreen;")
        if fullscreen == True:
            try:
                browser.execute_script("document.querySelector('#jspsych-fullscreen-btn').click();")
            except WebDriverException as e:
                pass
    return wait_time,finished 

def check_errors(browser):
   
    # Look at log from last call
    log = browser.get_log("browser")
    for log_entry in log:
        assert_equal(log_entry["level"] in ["WARNING","INFO"],True)


def get_continue_key(block,block_tag="cont_key"):
    if not isinstance(block[block_tag],list):
        block[block_tag] = [block[block_tag]]
    # Not specifying a key means "any key"
    if len(block[block_tag]) == 0:
        continue_key = Keys.ENTER
    else:
        continue_key = key_lookup(block[block_tag][0])
    return continue_key


def get_browser():
    return webdriver.Firefox()

    
def get_page(browser,url):
    browser.get(url)


# Run javascript and get output
def run_javascript(browser,code):
    return browser.execute_script(code)


def test_experiment(folder=None,battery_folder=None,port=None,pause_time=2000):
    '''test_experiment
    test an experiment locally with the --test tag and the expfactory robot
    :param folder: full path to experiment folder to preview. If none specified, PWD is used
    :param battery_folder: full path to battery folder to use as a template. If none specified, the expfactory-battery repo will be used.
    :param port: the port number, default will be randomly generated between 8000 and 9999
    '''
    if folder==None:
        folder=os.path.abspath(os.getcwd())

    # Deploy experiment with battery to temporary directory
    tmpdir = tmp_experiment(folder,battery_folder)
    experiment = load_experiment("%s" %folder)

    try:
        if port == None:
            port = choice(range(8000,9999),1)[0]
            Handler = ExpfactoryServer
            httpd = SocketServer.TCPServer(("", port), Handler)
            server = Thread(target=httpd.serve_forever)
            server.setDaemon(True)
            server.start()

        # Set up a web browser
        browser = get_browser()
        browser.implicitly_wait(3) # if error, will wait 3 seconds and retry
        browser.set_page_load_timeout(10)
 
        bot.log("STARTING TEST OF EXPERIMENT %s" %(experiment[0]["exp_id"]))
        get_page(browser,"http://localhost:%s" %(port))
        
        sleep(3)

        count=0
        wait_time=1000
        while True:
            bot.log("Testing block %s of %s" %(count,experiment[0]["exp_id"]))
            wait_time,finished = test_block(browser,experiment,pause_time,wait_time)
            if finished == True:
                break
            count+=1
        bot.log("FINISHING TEST OF EXPERIMENT %s" %(experiment[0]["exp_id"]))

    except:
        bot.log("Stopping web server...")
        httpd.server_close()
        shutil.rmtree(tmpdir)
