'''
utils.py: part of expfactory package

'''
import errno
import shutil
import os
import re
import __init__


def get_installdir():
    return os.path.dirname(os.path.abspath(__init__.__file__))

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

def remove_unicode_dict(input_dict,encoding="utf-8"):
    """
    remove unicode keys and values from dict, encoding in utf8

    """

    output_dict = dict()
    for key,value in input_dict.iteritems():
        if isinstance(input_dict[key],list):
            output_new = [x.encode(encoding) for x in input_dict[key]]
        elif isinstance(input_dict[key],int):
            output_new = input_dict[key]
        elif isinstance(input_dict[key],float):
            output_new = input_dict[key]
        else:
            output_new = input_dict[key].encode(encoding)
        output_dict[key.encode(encoding)] = output_new
    return output_dict

 
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
