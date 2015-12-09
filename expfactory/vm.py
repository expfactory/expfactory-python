'''
vm.py: part of expfactory package
Functions to generate virtual machines to run expfactory batteries

'''
from expfactory.utils import get_template, sub_template, save_template, clean_fields
from git import Repo
import tempfile
import shutil
import os

def download_repo(repo_type,destination):
    '''download_repo
    Download a expfactory infrastructure repo "repo_type" to a "destination"
    :param repo_type: can be one of "experiments" "battery" "vm"
    :param destination: the full path to the destination for the repo
    '''
    acceptable_types = ["experiments","battery","vm"]
    if repo_type not in acceptable_types:
        print "repo_type must be in %s" %(",".join(acceptable_types))
    else:
        return Repo.clone_from("https://github.com/expfactory/expfactory-%s" %(repo_type), destination)


def custom_battery_download(tmpdir=None,repos=["experiments","battery"]):
    '''custom_battery_download
    Download battery and experiment repos to a temporary folder to build a custom battery, return the path to the tmp folders
    :param tmpdir: The directory to download to. If none, a temporary directory will be made
    :param repos: The repositories to download, valid choices are "experiments" "battery" and "vm"
    '''
    if isinstance(repos,str):
        repos = [repos]
    if not tmpdir:
        tmpdir = tempfile.mkdtemp()
    for repo in repos:
        download_repo(repo,"%s/%s/" %(tmpdir,repo))
    return tmpdir


def add_custom_logo(battery_repo,logo):
    '''add_custom_logo
    Add a custom logo to the vm battery
    :param battery_repo: the full path to the battery repo base, assumed to have an "img" folder
    :param logo: the full path to the logo to copy. Should ideally be png.
    '''
    shutil.copy(logo,"%s/img/logo.png" %(battery_repo))
    

def generate_database_url(dbtype=None,username=None,password=None,host=None,table=None,template=None):
    '''generate_database_url
    Generate a database url from input parameters, or get a template
    :param dbtype: the type of database, must be one of "mysql" or "postgresql"
    :param username: username to connect to the database
    :param password: password to connect to the database
    :param host: database host
    :para table: table in the database
    :param template: can be one of "mysql" "sqlite3" or "postgresql" If specified, all other parameters are ignored, and a default database URL is produced to work in a Vagrant VM produced by expfactory
    
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
        return "mysql://expfactory:expfactory@localhost:3306/expfactory"
    elif template == "sqlite3":
        return "sqlite:///participants.db" 
    elif template == "postgresql":
        return "postgresql://expfactory:expfactory@localhost:5432/expfactory"

def prepare_vm(battery_dest,fields=None,vm_repo=None,vm_type="vagrant"):
    '''prepare_vm
    Prepare virtual machine to run local with vagrant, or with vagrant-aws
    :param battery_dest: the battery destination folder
    :param fields: if specified, will be added to the config.txt
    :param vm_repo: the expfactory-vm repo to use for templates. If not provided, one will be downloaded to a temporary directory for use.
    :param vm_type: one of "vagrant" or "aws" Default is "vagrant" meaning a localvirtual machine with vagrant.
    
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
    '''specify_experiments
    Specify experiments for a Vagrantfile in an output folder
    :param battery_dest: destination folder for battery
    :param experiments: a list of experiment tags to include

    '''
    experiments = [e.encode("utf-8") for e in experiments]
    vagrantfile = "%s/Vagrantfile" %(battery_dest)
    if not os.path.exists(vagrantfile):
        prepare_vm(battery_dest)
    template = get_template(vagrantfile)
    template = sub_template(template,"[SUB_EXPERIMENTS_SUB]",str(experiments))
    save_template(vagrantfile,template)
    return template

def get_stylejs(experiment,url_prefix=""):
    '''get_stylejs
    return string for js and css scripts to insert into a page based on battery path structure
    '''
    js = ""
    css = ""
    scripts = experiment[0]["run"]
    tag = experiment[0]["tag"]
    for script in scripts:
        ext = script.split(".")[-1]

        # Do we have a relative experiment path?
        if len(script.split("/")) == 1:
            if ext == "js":
                js = "%s\n<script src='%sstatic/experiments/%s/%s'></script>" %(js,url_prefix,tag,script)
            elif ext == "css":
                css = "%s\n<link rel='stylesheet prefetch' href='%sstatic/experiments/%s/%s'>" %(css,url_prefix,tag,script)

        # Do we have a battery relative path?
        else:    
            if ext == "js":
                js = "%s\n<script src='%s%s'></script>" %(js,url_prefix,script)
            elif ext == "css":
                css = "%s\n<link rel='stylesheet prefetch' href='%s%s'>" %(css,url_prefix,script)

    return css,js
