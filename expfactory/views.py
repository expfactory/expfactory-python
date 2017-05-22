'''
views.py

part of the experiment factory package
functions for developing experiments and batteries, viewing and testing things

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

from expfactory.utils import copy_directory, get_installdir, sub_template, get_template, write_json
from expfactory.battery import get_experiment_run, generate_local, move_experiments, generate_base
from expfactory.vm import custom_battery_download, get_stylejs, get_jspsych_init
from expfactory.experiment import load_experiment, get_experiments
from cognitiveatlas.api import get_concept, get_task
from expfactory.survey import generate_survey
from logman import bot
from numpy.random import choice
import SimpleHTTPServer
import SocketServer
import webbrowser
import tempfile
import json
import numpy
import shutil
import pandas
import os
import re

def embed_experiment(folder,url_prefix=""):
    '''embed_experiment
    return an html snippet for embedding into an application. This assumes the same directory structure, that all jspsych files can be found in static/js/jspych, and experiments under static/experiments/[folder]
    :param folder: full path to experiment folder with config.json
    '''
    folder = os.path.abspath(folder)
    experiment = load_experiment("%s" %folder)
    return get_experiment_html(experiment,folder,url_prefix=url_prefix)


def run_single(exp_id,repo_type,destination=None,source_repo=None,battery_repo=None,port=None,subject_id=None):
    '''run_survey runs or previews an entire battery locally with the --run tag. If no experiments are provided, all in the folder will be used.
    :param destination: destination folder for battery. If none provided, tmp directory is used
    :param exp_id: exp_id for survey, experiment, or game to run (unique ID)
    :param repo_type: must be within experiments,surveys, or games
    :param source_repo: a source repo for the experiment, survey, or game
    :param subject_id: subject id to embed into result. If none, will be randomly generated
    :param battery_folder: full path to battery folder to use as a template. If none specified, the expfactory-battery repo will be used.
    :param port: the port number, default will be randomly generated between 8000 and 9999
    '''
    valid_repos = ["experiments","games","surveys"]
    if repo_type not in valid_repos:
        bot.error("Repo type must be in %s" %(",".join(valid_repos)))
        sys.exit(1)

    bot.debug("Deploying %s %s" %(repo_type[:-1],exp_id))

    # Default uses downloaded repos
    experiment_repo = None
    survey_repo = None
    game_repo = None

    if source_repo is not None:
        if repo_type == "experiments":
            experiment_repo = source_repo
        elif repo_type == "surveys":
            survey_repo = source_repo
        elif repo_type == "games":
            game_repo = source_repo

    if destination == None:
        destination = tempfile.mkdtemp()
        shutil.rmtree(destination)

    # We can only generate a battery to a folder that does not exist, to be safe
    if not os.path.exists(destination):

        base = generate_base(battery_dest=destination,
                             tasks=[exp_id],
                             survey_repo=survey_repo,
                             experiment_repo=experiment_repo,
                             game_repo=game_repo,
                             add_experiments = False,
                             battery_repo=battery_repo,
                             warning=False)

        if port == None:
            port = choice(range(8000,9999),1)[0]

        # Currently only support one survey
        output_folder = "%s/%s" %(base["%s_repo" %(repo_type[:-1])],exp_id)
        if output_folder in base[repo_type]:
            preview_experiment(folder=output_folder,battery_folder=base["battery_repo"],port=port)
        else:
            bot.error("Invalid %s %s not found in surveys repo!" %(repo_type[:-1],exp_id))

    else:
        bot.error("Folder exists at %s, cannot generate." %(destination))


def run_battery(destination=None,experiments=None,experiment_folder=None,subject_id=None,battery_folder=None,port=None,time=30):
    '''run_battery runs or previews an entire battery locally with the --run tag. If no experiments are provided, all in the folder will be used.
    :param destination: destination folder for battery. If none provided, tmp directory is used
    :param experiments: list of experiment tags to add to battery
    :param experiment_folder: the folder of experiments to deploy the battery from.
    :param subject_id: subject id to embed into battery. If none, will be randomly generated
    :param battery_folder: full path to battery folder to use as a template. If none specified, the expfactory-battery repo will be used.
    :param port: the port number, default will be randomly generated between 8000 and 9999
    :param time: total number of minutes for experiments to add to battery
    '''
    bot.debug("Generating custom battery selecting from experiments for maximum of %s minutes, please wait..." %(time))

    if destination == None:
        destination = tempfile.mkdtemp()
        shutil.rmtree(destination)

    # Deploy experiment with battery to temporary directory   
    tmpdir = generate_local(battery_dest=destination,
                            subject_id=subject_id,
                            battery_repo=battery_folder,
                            experiment_repo=experiment_folder,
                            experiments=experiments,
                            warning=False,
                            time=time)
    os.chdir(tmpdir)
    
    try:
        if port == None:
            port = choice(range(8000,9999),1)[0]
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", port), Handler)
        bot.info("Preview experiment at localhost:%s" %port)
        webbrowser.open("http://localhost:%s" %(port))
        httpd.serve_forever()
    except:
        bot.info("Stopping web server...")
        httpd.server_close()
        shutil.rmtree(tmpdir)

    
def preview_experiment(folder=None,battery_folder=None,port=None):
    '''preview_experiment
    preview an experiment locally with the --preview tag (for development)
    :param folder: full path to experiment folder to preview. If none specified, PWD is used
    :param battery_folder: full path to battery folder to use as a template. If none specified, the expfactory-battery repo will be used.
    :param port: the port number, default will be randomly generated between 8000 and 9999
    :param robot: if True, a web server is started as a separate process for a robot to run
    '''

    # Deploy experiment with battery to temporary directory
    tmpdir = tmp_experiment(folder,battery_folder)
    
    try:
        if port == None:
            port = choice(range(8000,9999),1)[0]
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", port), Handler)
        bot.info("Preview experiment at localhost:%s" %port)
        webbrowser.open("http://localhost:%s" %(port))
        httpd.serve_forever()
    except:
        bot.info("Stopping web server...")
        httpd.server_close()
        shutil.rmtree(tmpdir)

def generate_experiment_web(output_dir,experiment_folder=None,survey_folder=None,games_folder=None,
                            make_table=True,make_index=True,make_experiments=True,make_data=True,
                            make_surveys=True,make_games=True):
    '''get_experiment_table
    Generate a table with links to preview all experiments
    :param experiment_folder: folder with experiments inside
    :param survey_folder: folder with surveys inside
    :param games_folder: folder with games inside
    :param output_dir: output folder for experiment and table html, and battery files 
    :param make_table: generate table.html 
    :param make_index: generate d3 visualization index  
    :param make_experiments: generate experiment preview files (linked from table and index) 
    :param make_data: generate json/tsv data to download 
    :param make_surveys: generate static files for surveys repos 
    :param make_games: generate static files for games repos 
    '''
    repos=["experiments","battery"]
    if make_surveys == True:
        repos.append("surveys")

    if make_games == True:
        repos.append("games")     

    tmpdir = custom_battery_download(repos=repos)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if experiment_folder == None:
        experiment_folder = "%s/experiments" %tmpdir
    experiments = get_experiments(experiment_folder,load=True, warning=False)
    experiment_tags = [x[0]["exp_id"] for x in experiments]
    battery_repo = "%s/battery" %(tmpdir)
    if survey_folder == None:
        survey_folder = "%s/surveys" %tmpdir
    if games_folder == None:
        games_folder = "%s/games" %tmpdir

    # If the user wants surveys and/or games, add them on to tasks
    tasks = experiments
    if make_surveys == True:
        surveys = get_experiments(survey_folder,load=True,warning=False,repo_type="surveys")
        survey_tags = [x[0]["exp_id"] for x in surveys]
        tasks = experiments + surveys

    if make_games == True:
        games = get_experiments(games_folder,load=True,warning=False,repo_type="games")
        games_tags = [x[0]["exp_id"] for x in games]
        tasks = tasks + games

    # Fields to keep for the table
    fields = ['preview','exp_id','template',
              'contributors','time',
              'cognitive_atlas_task_id']

    valid = pandas.DataFrame(columns=fields)
   
    # Make a table of experiment information
    for experiment in tasks:
        for field in experiment[0].keys():
            if field in fields:
                values = experiment[0][field]
                # Join lists with a comma
                if field == "reference":
                    if values != '':
                        values = '<a href="%s" target="_blank">%s</a>' %(values,values)
                if isinstance(values,list):
                    values = ",".join(values)
                valid.loc[experiment[0]["exp_id"],field] = values

        # Add a preview link
        valid.loc[experiment[0]["exp_id"],"preview"] = '<a href="%s.html" target="_blank">DEMO</a>' %(experiment[0]["exp_id"])
        
    # If the user wants to create the index page
    if make_index == True:
        output_index = os.path.abspath("%s/index.html" %output_dir)

        # For each experiment, we will prepare an interactive node for the site
        nodes = []
        for experiment in tasks:
            nodes.append('{"cluster": 1, "radius": "10", "color": colors[%s], "exp_id": "%s" }' %(choice([0,1,2]),experiment[0]["exp_id"]))

        # Generate index page
        index_template = get_template("%s/templates/expfactory_index.html" %get_installdir())        
        index_template = index_template.replace("[SUB_NODES_SUB]",",".join(nodes))
        index_template = index_template.replace("[SUB_TOTAL_SUB]",str(len(nodes)))
        filey = open(output_index,"wb")
        filey.writelines(index_template)
        filey.close()


    # Update entire static directory
    old_dirs = ["templates","static"]
    for folder in old_dirs:
        copy_to = os.path.abspath("%s/%s" %(output_dir,folder))
        copy_from = "%s/battery/%s" %(tmpdir,folder)
        if os.path.exists(copy_to):
            shutil.rmtree(copy_to)
        copy_directory(copy_from,copy_to)

    # Copy the favicon to web base
    shutil.copyfile("%s/battery/static/favicon.ico" %tmpdir,"%s/favicon.ico" %output_dir)

    # Clear old experiments
    experiment_dir = os.path.abspath("%s/static/experiments/" %output_dir)
    if os.path.exists(experiment_dir):
        shutil.rmtree(experiment_dir)

    # Clear old surveys, copy updated valid surveys into survey directory
    if make_surveys == True:
        survey_dir = os.path.abspath("%s/static/surveys/" %output_dir)
        if os.path.exists(survey_dir):
            shutil.rmtree(survey_dir)
        valid_surveys = ["%s/%s" %(survey_folder,x[0]["exp_id"]) for x in surveys]
        move_experiments(valid_surveys,battery_dest=output_dir,repo_type="surveys")

    # Clear old surveys, copy updated valid surveys into survey directory
    if make_games == True:
        games_dir = os.path.abspath("%s/static/games/" %output_dir)
        if os.path.exists(games_dir):
            shutil.rmtree(games_dir)
        valid_games = ["%s/%s" %(games_folder,x[0]["exp_id"]) for x in games]
        move_experiments(valid_games,battery_dest=output_dir,repo_type="games")

    # Copy updated valid experiments into our experiment directory
    valid_experiments = ["%s/%s" %(experiment_folder,x[0]["exp_id"]) for x in experiments]
    move_experiments(valid_experiments,battery_dest=output_dir)

    # If the user wants to make a table
    if make_table == True:

        table_template = get_template("%s/templates/table.html" %get_installdir())
        output_table = os.path.abspath("%s/table.html" %output_dir)

        # First prepare rendered table
        table = '<table id="fresh-table" class="table">\n<thead>\n'
        for field in fields:
            table = '%s<th data-field="%s" data-sortable="true">%s</th>' %(table,field,field)
        table = '%s\n</thead>\n<tbody>\n' %(table)

        for row in valid.iterrows():
            table = "%s<tr>\n" %(table)
            for field in row[1]:
                table = "%s<td>%s</td>\n" %(table,field)
            table = "%s</tr>\n" %(table)

        table = "%s</tbody></table>\n" %(table)

        # Write the new table
        table_template = table_template.replace("[[SUB_TABLE_SUB]]",table)
        filey = open("%s/table.html" %output_dir,"wb")
        filey.writelines(table_template)
        filey.close()

    if make_experiments == True:
        experiments_template = get_template("%s/templates/experiments_categories.html" %get_installdir())
        output_exp = os.path.abspath("%s/experiments.html" %output_dir)

        if "CIRCLE_BRANCH" in os.environ.keys():
            experiment_page = table_template    
        else:
            experiment_page = get_cognitiveatlas_hierarchy(experiment_tags=experiment_tags,get_html=True)

        # Write the new table
        filey = open(output_exp,"wb")
        filey.writelines(experiment_page)
        filey.close()
        
        # For each experiment, we will generate a demo page
        for experiment in experiments:
            demo_page = os.path.abspath("%s/%s.html" %(output_dir,experiment[0]["exp_id"]))
            exp_template = get_experiment_html(experiment,"%s/%s" %(experiment_folder,experiment[0]["exp_id"]))
            filey = open(demo_page,"wb")
            filey.writelines(exp_template)
            filey.close()

    # if the user wants to make surveys
    if make_surveys == True:
        for experiment in surveys:
            demo_page = os.path.abspath("%s/%s.html" %(output_dir,experiment[0]["exp_id"]))
            exp_template = get_experiment_html(experiment,"%s/%s" %(survey_folder,experiment[0]["exp_id"]))
            filey = open(demo_page,"wb")
            filey.writelines(exp_template)
            filey.close()


    # if the user wants to make surveys
    if make_games == True:
        for experiment in games:
            demo_page = os.path.abspath("%s/%s.html" %(output_dir,experiment[0]["exp_id"]))
            exp_template = get_experiment_html(experiment,"%s/%s" %(games_folder,experiment[0]["exp_id"]))
            filey = open(demo_page,"wb")
            filey.writelines(exp_template)
            filey.close()

    # If the user wants to make data
    if make_data == True:
        data_folder = os.path.abspath("%s/data" %output_dir)
        if not os.path.exists(data_folder):
            os.mkdir(data_folder)
        write_json(json.loads(valid.to_json(orient="records")),"%s/expfactory-experiments.json" %(data_folder))
        valid.to_csv("%s/expfactory-experiments.tsv" %(data_folder),sep="\t",index=None)
        valid.to_pickle("%s/expfactory-experiments.pkl" %(data_folder))


def get_experiment_html(experiment,experiment_folder,url_prefix="",deployment="local"):
    '''get_experiment_html
    return the html template to test a single experiment
    :param experiment: the loaded config.json for an experiment (json)
    :param experiment_folder: the experiment folder, needed for reading in a survey
    :param url_prefix: prefix to put before paths, in case of custom deployment
    :param deployment: deployment environment, one of docker, docker-preview, or local [default]
    '''

    css,js = get_stylejs(experiment,url_prefix)
    validation = ""

    # JsPsych experiment
    if experiment[0]["template"] in ["jspsych"]:
        html = ""
        runcode = get_experiment_run(experiment,deployment=deployment)[experiment[0]["exp_id"]]
        template_base = "experiment"

    # HTML survey
    elif experiment[0]["template"] in ["survey"]:
        html,validation = generate_survey(experiment,experiment_folder)
        runcode = ""
        template_base = "survey"

    # Phaser game
    elif experiment[0]["template"] in ["phaser"]:
        html = ""
        runcode = experiment[0]["deployment_variables"]["run"]
        template_base = "phaser"


    exp_template = "%s/templates/%s.html" %(get_installdir(),template_base)

    # Make substitutions
    exp_template = "".join(open(exp_template,"r").readlines())
    exp_template = sub_template(exp_template,"{{js}}",js)
    exp_template = sub_template(exp_template,"{{css}}",css)
    exp_template = sub_template(exp_template,"{{run}}",runcode)
    exp_template = sub_template(exp_template,"{{html}}",html)
    exp_template = sub_template(exp_template,"{{validation}}",validation)
    exp_template = sub_template(exp_template,"{{exp_id}}",experiment[0]["exp_id"])
    return exp_template


def get_cognitiveatlas_hierarchy(experiment_tags=None,get_html=False):
    '''get_cognitiveatlas_hierarchy
    return 
    :param experiment_tags: a list of experiment exp_id tags to include. If None provided, all valid experiments will be used.
    :param get_html: if True, returns rendered HTML template with hierarchy. False returns json data structure.
    '''
    from cognitiveatlas.datastructure import concept_node_triples
    from expfactory.graph import make_tree_from_triples

    tmpdir = custom_battery_download()
    experiment_folder = "%s/experiments" %tmpdir
    experiments = get_experiments(experiment_folder,load=True,warning=False)
    if experiment_tags != None:
        experiments = [e for e in experiments if e[0]["exp_id"] in experiment_tags]
    
    # We need a dictionary to look up experiments by task ids
    unique_tasks = numpy.unique([e[0]["cognitive_atlas_task_id"] for e in experiments]).tolist()

    experiment_lookup = dict()
    for u in unique_tasks:
        matching_tasks = numpy.unique([e[0]["exp_id"] for e in experiments if e[0]["cognitive_atlas_task_id"]==u])
        experiment_lookup[u] = matching_tasks.tolist()

    triples = concept_node_triples(image_dict=experiment_lookup,save_to_file=False,lookup_key_type="task")

    # Experiments not in the tree get added to parent node 1
    undefined_experiments = [x[0]["exp_id"] for x in experiments if x[0]["exp_id"] not in triples.name.tolist()]
    undefined_experiments.sort()

    last_defined_node = [x for x in triples.id.tolist() if re.search("node_",x)]
    last_defined_node.sort()
    last_defined_node = int(last_defined_node[-1].replace("node_",""))
    idx = triples.index.tolist()[-1]+1
    for i in range(idx,idx+len(undefined_experiments)):
        undefined_experiment = undefined_experiments.pop(0)
        triples.loc[i] = ["node_%s" %(last_defined_node+1),1,undefined_experiment]
        last_defined_node+=1

    # We want to add meta data for the experiments
    meta_data = dict()
    for experiment in experiments:
        node_ids = triples.id[triples.name==experiment[0]["exp_id"]].tolist()
        for node_id in node_ids:
            meta_data[node_id] = experiment[0]

    # Generate a data structure with task/concept hierarchy, prune_tree default is True 
    if get_html == True:
        tree = make_tree_from_triples(triples,output_html=True,meta_data=meta_data)
    else:
        tree = make_tree_from_triples(triples,output_html=False) 
    return tree

def tmp_experiment(folder=None,battery_folder=None):
    '''generate temporary directory with experiment
    :param folder: full path to experiment folder to preview (experiment, survey, or game). If none specified, PWD is used
    :param battery_folder: full path to battery folder to use as a template. If none specified, the expfactory-battery repo will be used.
    '''
    if folder==None:
        folder=os.path.abspath(os.getcwd())

    if battery_folder == None:
        tmpdir = custom_battery_download(repos=["battery"])
    # If user has supplied a local battery folder, copy to tempdir
    else:
        tmpdir = tempfile.mkdtemp()
        copy_directory(battery_folder,"%s/battery" %tmpdir)
        
    experiment = load_experiment("%s" %folder)
    tag = experiment[0]["exp_id"]

    # Determine experiment template
    experiment_type = "experiments"
    if experiment[0]["template"] == "survey":
        experiment_type = "surveys"
    elif experiment[0]["template"] == "phaser":
        experiment_type = "games"

    # We will copy the entire experiment into the battery folder
    battery_folder = "%s/battery" %(tmpdir)
    experiment_folder = "%s/static/%s/%s" %(battery_folder,experiment_type,tag)
    if os.path.exists(experiment_folder):
        shutil.rmtree(experiment_folder)
    copy_directory(folder,experiment_folder)
    index_file = "%s/index.html" %(battery_folder)
        
    # Generate code for js and css
    exp_template = get_experiment_html(experiment,experiment_folder)
    filey = open(index_file,"w")
    filey.writelines(exp_template)
    filey.close()
    os.chdir(battery_folder)
    return tmpdir
