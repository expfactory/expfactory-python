'''
utils.py: part of psiturkpy package

'''
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
        if not re.match("^[.]*",item):
            if os.path.isdir(os.path.join(root, item)):
                if fullpath:
                    directories.append(os.path.abspath(os.path.join(root, item)))
                else:
                    directories.append(item)
    return directories
