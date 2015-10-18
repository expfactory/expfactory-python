'''
vm.py: part of psiturkpy package
Functions to generate virtual machines to run psiturk batteries

'''
from psiturkpy.utils import get_template, sub_template, save_template, clean_fields
from git import Repo
import tempfile
import shutil
import os

def download_repo(repo_type,destination):
    '''

    Download a psiturk infrastructure repo "repo_type" to a "destination"
  
       repo_type: can be one of "experiments" "battery" "vm" or "doc"
       destination: the full path to the destination for the repo

    '''
    acceptable_types = ["experiments","battery","vm","doc"]
    if repo_type not in acceptable_types:
        print "repo_type must be in %s" %(",".join(acceptable_types))
    else:
        return Repo.clone_from("https://github.com/psiturk/psiturk-%s" %(repo_type), destination)


def custom_battery_download(tmpdir=None,repos=["experiments","battery"]):
    '''

    custom_battery_download

    Download battery and experiment repos to a temporary folder to build a custom
    battery, return the path to the tmp folders

        tmpdir: The directory to download to. If none, a temporary directory will be made
        repos: The repositories to download, valid choices are "experiments" "battery" and "vm"

    '''
    if not tmpdir:
        tmpdir = tempfile.mkdtemp()
    for repo in repos:
        download_repo(repo,"%s/%s/" %(tmpdir,repo))
    return tmpdir


def add_custom_logo(battery_repo,logo):
    '''
    
    Add a custom logo to the vm battery

        battery_repo: the full path to the battery repo base, assumed to have an "img" folder
        logo: the full path to the logo to copy. Should ideally be png.
    '''
    shutil.copy(logo,"%s/img/logo.png" %(battery_repo))
    

def generate_database_url(dbtype=None,username=None,password=None,host=None,table=None,template=None):
    '''
    Generate a database url from input parameters, or get a template
        dbtype: the type of database, must be one of "mysql" or "postgresql"
        username: username to connect to the database
        password: password to connect to the database
        host: database host
        table: table in the database
        template: can be one of "mysql" "sqlite3" or "postgresql" If specified, all other parameters are
                  ignored, and a default database URL is produced to work in a Vagrant VM produced by
                  psiturkpy
    
    '''
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

def prepare_vm(battery_dest,fields=None,vm_repo=None,vm_type="vagrant"):
    '''
    Prepare virtual machine to run local with vagrant, or with vagrant-aws

        battery_dest: the battery destination folder
        fields: if specified, will be added to the config.txt
        vm_repo: the psiturk-vm repo to use for templates. If not provided,
                 one will be downloaded to a temporary directory for use.
        vm_type: one of "vagrant" or "aws" Default is "vagrant" meaning a local
                 virtual machine with vagrant.
    '''

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

    # Change file to be a custom install
    template = sub_template(template,'CUSTOM_INSTALL="False"','CUSTOM_INSTALL="True"')
        
    output_file = "%s/Vagrantfile" %(battery_dest)
    save_template(output_file,template)
    return template

def specify_experiments(battery_dest,experiments):
    '''
    Specify experiments for a Vagrantfile in an output folder

        battery_dest: destination folder for battery
        experiments: a list of experiment tags to include

    '''
    experiments = [e.encode("utf-8") for e in experiments]
    vagrantfile = "%s/Vagrantfile" %(battery_dest)
    if not os.path.exists(vagrantfile):
        prepare_vm(battery_dest)
    template = get_template(vagrantfile)
    template = sub_template(template,"[SUB_EXPERIMENTS_SUB]",str(experiments))
    save_template(vagrantfile,template)
    return template
