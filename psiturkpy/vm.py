'''
vm.py: part of psiturkpy package
Functions to generate virtual machines to run psiturk batteries

'''
from psiturkpy.utils import get_template, sub_template, save_template, clean_fields
from git import Repo
import tempfile
import shutil
import os

"""

Download a psiturk infrastructure repo "repo_type" to a "destination"
repo_type: can be one of "experiments" "battery" "vm" or "doc"

"""
def download_repo(repo_type,destination):
    acceptable_types = ["experiments","battery","vm","doc"]
    if repo_type not in acceptable_types:
        print "repo_type must be in %s" %(",".join(acceptable_types))
    else:
        return Repo.clone_from("https://github.com/psiturk/psiturk-%s" %(repo_type), destination)


"""

custom_battery_download

Download battery and experiment repos to a temporary folder to build a custom
battery, return the path to the tmp folders

"""
def custom_battery_download(tmpdir=None,repos=["experiments","battery"]):
    if not tmpdir:
        tmpdir = tempfile.mkdtemp()
    for repo in repos:
        download_repo(repo,"%s/%s/" %(tmpdir,repo))
    return tmpdir


"""

Add a custom logo to the vm battery

"""

def add_custom_logo(battery_repo,logo):
    shutil.copy(logo,"%s/img/logo.png" %(battery_repo))
    

"""
Generate a database url from input parameters, or get a template

"""
def generate_database_url(dbtype=None,username=None,password=None,host=None,table=None,template=None):
    if not template:
        if not dbtype or not username or not password or not host or not table:
            print "Please provide all inputs: dbtype,username,password,host,table."
        else:
            return "%s://%s:%s@%s/%s"  %(dbtype,
                                         username,
                                         password,
                                         host,
                                         table)
    elif template == "mysql":
        return "mysql://psiturkpy:psiturkpy@localhost:3306/psiturkpy"
    elif template == "sqlite3":
        return "sqlite:///participants.db" 
    elif template == "postgresql":
        return "postgresql://psiturkpy:psiturkpy@localhost:5432/psiturkpy"

"""
Prepare virtual machine to run local with vagrant, or with vagrant-aws

"""
def prepare_vm(battery_dest,fields=None,vm_repo=None,vm_type="vagrant"):

    # Download vm_repo if it hasn't been specified
    if not vm_repo:
        download_repo("vm","%s/vm" %battery_dest)

    # Grab the appropriate vagrantfile template
    if vm_type == "aws":
        template = get_template("%s/vm/VagrantfileAWS" %(battery_dest))
    else:
        template = get_template("%s/vm/VagrantfileLocal" %(battery_dest))

    # If the user has custom config fields, write to file
    if fields != None:
        fields = clean_fields(fields)
        template = sub_template(template,"[SUB_CONFIG_SUB]",str(fields))
    else:
        template = sub_template(template,"[SUB_CONFIG_SUB]","None")
        
    output_file = "%s/Vagrantfile" %(battery_dest)
    save_template(output_file,template)
    return template

"""
Specify experiments for a Vagrantfile in an output folder

"""
def specify_experiments(battery_dest,experiments):
    experiments = [e.encode("utf-8") for e in experiments]
    vagrantfile = "%s/Vagrantfile" %(battery_dest)
    if not os.path.exists(vagrantfile):
        prepare_vm(battery_dest)
    template = get_template(vagrantfile)
    template = sub_template(template,"[SUB_EXPERIMENTS_SUB]",str(experiments))
    save_template(vagrantfile,template)
    return template
