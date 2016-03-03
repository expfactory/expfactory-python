'''
utils.py: part of expfactory package

'''
from urllib2 import Request, urlopen, HTTPError
import errno
import collections
import filecmp
import shutil
import json
import os
import re
import __init__


def get_installdir():
    return os.path.dirname(os.path.abspath(__init__.__file__))


def find_changed(new_repo,comparison_repo,return_experiments=True):
    '''find_changed returns a list of changed files or experiments between two repos
    :param new_repo: the updated repo - any new files, or changed files, will be returned
    :param comparison_repo: the old repo to compare against. A file changed or missing in this repo in the new_repo indicates it should be tested
    :param return_experiments: return experiment folders. Default is True. If False, will return complete file list
    ''' 
    # First find all experiment folders in current repo
    experiment_folders = get_experiments(new_repo,load=False)
    file_list = []
    # Find all files
    for experiment_folder in experiment_folders:
        for root, dirnames, filenames in os.walk(experiment_folder):
            for filename in filenames:
                file_list.append(os.path.join(root, filename))
    # Compare against master
    changed_files = []
    for contender_file in file_list:
        old_file = contender_file.replace("%s/expfactory-experiments" %(os.environ["HOME"]),comparison_repo)
        # If the old file exists, check if it's changed
        if os.path.exists(old_file):
            if not filecmp.cmp(old_file,contender_file):
                changed_files.append(contender_file)
        # If it doesn't exist, we check
        else:
            changed_files.append(contender_file)

    # Find differences with compare
    print "Found files changed: %s" %(",".join(changed_files))

    if return_experiments == True:
        return numpy.unique([os.path.dirname(x.strip("\n")) for x in changed_files if os.path.dirname(x.strip("\n")) != ""]).tolist()
        
    return changed_files


def find_subdirectories(basepath):
    '''
    Return directories (and sub) starting from a base

    '''

    directories = []
    for root, dirnames, filenames in os.walk(basepath):
        new_directories = [d for d in dirnames if d not in directories]
        directories = directories + new_directories
    return directories
    
def find_directories(root,fullpath=True):
    '''
    Return directories at one level specified by user
    (not recursive)

    '''

    directories = []
    for item in os.listdir(root):
        # Don't include hidden directories
        if not re.match("^[.]",item):
            if os.path.isdir(os.path.join(root, item)):
                if fullpath:
                    directories.append(os.path.abspath(os.path.join(root, item)))
                else:
                    directories.append(item)
    return directories

def remove_unicode_dict(input_dict):
    """
    remove unicode keys and values from dict, encoding in utf8

    """
    if isinstance(input_dict, basestring):
        return str(input_dict)
    elif isinstance(input_dict, collections.Mapping):
        return dict(map(remove_unicode_dict, input_dict.iteritems()))
    elif isinstance(input_dict, collections.Iterable):
        return type(input_dict)(map(remove_unicode_dict, input_dict))
    else:
        return input_dict
 
def copy_directory(src, dest):
    """
    Copy an entire directory recursively

    """

    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

def get_template(template_file):
    """
    get_template: read in and return a template file

    """

    filey = open(template_file,"rb")
    template = "".join(filey.readlines())
    filey.close()
    return template

def sub_template(template,template_tag,substitution):
    """
    make a substitution for a template_tag in a template
    """

    template = template.replace(template_tag,substitution)
    return template

def save_template(output_file,html_snippet):
    filey = open(output_file,"w")
    filey.writelines(html_snippet)
    filey.close()

def save_pretty_json(outfile,myjson):
    filey = open(outfile,'wb')
    filey.write(json.dumps(myjson, sort_keys=True,indent=4, separators=(',', ': ')))
    filey.close()


def is_type(var,types=[int,float,list]):
    """
    Check type
    """

    for x in range(len(types)):
        if isinstance(var,types[x]):
            return True
    return False

def clean_fields(mydict):
    """
    Ensure utf-8
    """

    newdict = dict()
    for field,value in mydict.iteritems():
        cleanfield = field.encode("utf-8")
        if isinstance(value,float):
            newdict[cleanfield] = value
        if isinstance(value,int):
            newdict[cleanfield] = value
        if isinstance(value,list):
            newlist = []
            for x in value:
                if not is_type(x):
                    newlist.append(x.encode("utf-8"))
                else:
                    newlist.append(x)
            newdict[cleanfield] = newlist
        else:
            newdict[cleanfield] = value.encode("utf-8")
    return newdict


def get_url(url):
    """get_url
    return a url as string
    """
    request = Request(url)
    response = urlopen(request)
    return response.read()
