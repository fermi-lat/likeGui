#!/usr/bin/env python
"""
Interface to .par files.

@author J. Chiang
"""
#
#$Header: /nfs/slac/g/glast/ground/cvs/likeGui/python/pil.py,v 1.5 2004/10/08 15:11:06 jchiang Exp $
#

import os
import string
from pfilesPath import pfilesPath

def accept(line):
    if (line.find('#') == 0 or len(line.split()) == 0):
        return 0
    return 1

def name(line):
    return line.split(',')[0].strip()

def fields(line):
    return [item.strip() for item in line.split(',')[1:]]

def havePathToFile(file):
    basename = os.path.basename(file)
    path = file.split(basename)[0]
    return path != "" and basename in os.listdir() 

class Pil(object):
    def __init__(self, pfile, raiseKeyErrors=True):
        self.raiseKeyErrors = raiseKeyErrors
        self.params = {}
        self.names = []
        if not havePathToFile(pfile):
            parfile = os.path.join(pfilesPath(pfile), pfile)
        else:
            parfile = pfile
        file = open(parfile, 'r')
        for line in file:
            if accept(line):
                self.params[name(line)] = fields(line)
                self.names.append(name(line))
    def keys(self):
        return self.names
    def __getitem__(self, name):
        value = (self.params[name][2]).strip('"').strip("'")
        if self.params[name][0] == 'r':
            return string.atof(value)
        elif self.params[name][0] == 'i':
            return string.atoi(value)
        else:
            return value
    def __setitem__(self, name, value):
        if name in self.names:
            self.params[name][2] = `value`
        elif self.raiseKeyErrors:
            raise KeyError, name
    def __call__(self):
        args = ''
        for name in self.keys():
            args += ' ' + ''.join(('', name, '=', `self.__getitem__(name)`))
        return args

if __name__ == '__main__':
    pars = Pil('likelihood.par')
    print pars['event_file']
    print pars['Spacecraft_file_hdu']
    pars['Spacecraft_file_hdu'] = 3
    pars['event_file'] = 'foo'
    print pars['Spacecraft_file_hdu']
    print pars()

