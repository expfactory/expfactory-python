'''
analysis/maths.py: part of expfactory package
math functions

'''
import numpy

def check_numeric(v):
    if (v.dtype == numpy.float64 or v.dtype == numpy.int64):
        return True
    else:
        return False
