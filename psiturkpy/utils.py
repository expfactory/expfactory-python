'''
utils.py: part of psiturkpy package

'''
import errno
import shutil
import os
import re

'''
Return directories (and sub) starting from a base

'''
def find_subdirectories(basepath):
    directories = []
    for root, dirnames, filenames in os.walk(basepath):
        new_directories = [d for d in dirnames if d not in directories]
        directories = directories + new_directories
    return directories
    
'''
Return directories at one level specified by user
(not recursive)

'''
def find_directories(root,fullpath=True):
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

"""
Copy an entire directory recursively

"""
 
def copy_directory(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

"""
get_template: read in and return a template file

"""
def get_template(template_file):
    filey = open(template_file,"rb")
    template = "".join(filey.readlines())
    filey.close()
    return template

"""
make a substitution for a template_tag in a template
"""
def sub_template(template,template_tag,substitution):
    return re.sub(template_tag,substitution,template)
