#!/usr/bin/env python
"""
Extract sources from a flux-style xml source catalog and create a
Likelihood-style source model xml file and a ds9 region file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header: /nfs/slac/g/glast/ground/cvs/likeGui/python/extractSources.py,v 1.12 2007/11/21 04:27:41 jchiang Exp $
#
import os, sys, string, copy
from xml.dom import minidom

import Tkinter
import tkSimpleDialog
from FileDialog import LoadFileDialog, SaveFileDialog

import celgal
from xmlSrcLib import *
from readXml import Source
from facilities import py_facilities

os_environ = py_facilities.commonUtilities_getEnvironment
#_3EG_catalog = os.path.join(os.environ['OBSERVATIONSIMROOT'],
_3EG_catalog = os.path.join(os_environ('OBSERVATIONSIMROOT'),
                            'xml', '3EG_catalog_20-1e6MeV.xml')

class LikeSource(object):
    def __init__(self, src):
        self.src = src
        self.dir = self._getDir(src)
        self.flux = self._getFlux(src)
        self.name = src.getAttribute("name").encode()
    def _getFlux(self, src):
        spectrum = src.getElementsByTagName('spectrum')[0]
        pars = spectrum.getElementsByTagName('parameter')
        for par in pars:
            if par.getAttribute('name').encode() == "Integral":
                flux = (float(par.getAttribute('value'))
                        *float(par.getAttribute('scale'))*1e4)
                return flux
        return None
    def _getDir(self, src):
        dir_info = src.getElementsByTagName('spatialModel')[0]
        pars = dir_info.getElementsByTagName('parameter')
        try:
            pars[0].getAttribute('RA')
            ra = float(pars[0].getAttribute('value'))
            dec = float(pars[1].getAttribute('value'))
        except:
            ra = float(pars[1].getAttribute('value'))
            dec = float(pars[0].getAttribute('value'))
        return ra, dec
    def dist(self, ra, dec):
        return celgal.dist(self.dir, (ra, dec))
    def __getattr__(self, attrname):
        return getattr(self.src, attrname)

class LikeSourceList(object):
    def __init__(self, xmlFile):
        self.doc = minidom.parse(xmlFile)
        self.srcs = []
        for src in self.doc.getElementsByTagName('source'):
            try:
                self.srcs.append(LikeSource(src))
            except:
                pass
        if len(self.srcs) == 0:
            raise RuntimeError, "No sources loaded from %s" % xmlFile
    def extract(self, outfile, cone, fluxLimit=1e-2, useDiffuse=False,
                useCatVal=None):
        ra, dec, radius = cone
        output = open(outfile, 'w')
        output.write('<?xml version="1.0" ?>\n')
        output.write('<source_library title="%s">\n' % outfile)
        for src in self.srcs:
            if (src.dist(ra, dec) < radius and
                (src.flux is None or src.flux >= fluxLimit)):
                src.writexml(output)
        output.write('</source_library>\n')
        output.close()
    def write_region_file(self, outfile):
        regfile = ds9_region_file(outfile, fk5=1)
        for src in self.srcs:
            regfile.addSource(src.name, Source(src.src))
        regfile.write()

class SourceList(object):
    def __init__(self, inputFile=_3EG_catalog):
        self.inputFile = inputFile
    def _isPtSrc(self, src):
        dirs = src.getElementsByTagName('celestial_dir')
        if len(dirs) != 1: return False
        specs = src.getElementsByTagName('power_law')
        if len(specs) != 1 or not specs[0].hasAttribute('gamma'): return False
        particles = src.getElementsByTagName('particle')
        if (len(particles) != 1
            or particles[0].getAttribute('name').encode('ascii') != 'gamma'):
            return False
        return True
    def extract(self, outputFile, roiCone, fluxLimit=1e-2, useDiffuse=False,
                useCatVal=True):
        ra0, dec0, radius = roiCone
        ds9File = ds9_region_file('ds9.reg', fk5=1)
        ds9File.setSR(ra0, dec0, radius)
        outfile = open(outputFile, 'w')
        outfile.write('<?xml version="1.0" ?>\n')
        outfile.write('<source_library title="source library">\n')
        doc = minidom.parse(self.inputFile)
        srcList = doc.getElementsByTagName('source')
        if useDiffuse:
            outfile.write(EGDiffuse().toxml() + '\n')
            outfile.write(GalDiffuse().toxml() + '\n')
        for src in srcList[:-1]:
            if self._isPtSrc(src):
                dir = src.getElementsByTagName('celestial_dir')[0]
                ra = string.atof(dir.getAttribute('ra').encode('ascii'))
                dec = string.atof(dir.getAttribute('dec').encode('ascii'))
                flux = string.atof(src.getAttribute('flux').encode('ascii'))
                if (celgal.dist((ra0, dec0), (ra, dec)) < radius
                    and flux >= fluxLimit):
                    outfile.write(PointSource(src, useCatVal=useCatVal)
                                  .write() + '\n')
                    ds9File.addSrc(src)
        outfile.write('</source_library>\n')
        outfile.close()
        ds9File.write()

class PointSource(object):
    def __init__(self, fluxSrc, prefix='my', useCatVal=False):
        self.use_cat_val = useCatVal
        self.ptsrc = copy.deepcopy(ptSrc())
        self.ptsrc.setAttribute('name', prefix + fluxSrc.getAttribute('name'))
        self.fluxSrc = fluxSrc
        self._setDir()
        self._getSpecParams()
        self._setIndex()
        self._setPrefactor()
        self._setFlux()
    def _setDir(self):
        dir = self.fluxSrc.getElementsByTagName('celestial_dir')[0]
        spatialModel = self.ptsrc.getElementsByTagName('spatialModel')[0]
        coords = spatialModel.getElementsByTagName('parameter')
        for coord in coords:
            if coord.getAttribute('name').encode('ascii') == 'RA':
                coord.setAttribute('value', dir.getAttribute('ra'))
            if coord.getAttribute('name').encode('ascii') == 'DEC':
                coord.setAttribute('value', dir.getAttribute('dec'))
    def _getSpecParams(self):
        powerlaw = self.fluxSrc.getElementsByTagName('power_law')[0]
        self.gamma = string.atof(powerlaw.getAttribute('gamma'))
        self.emin = string.atof(powerlaw.getAttribute('emin'))/100.
        self.emax = string.atof(powerlaw.getAttribute('emax'))/100.
    def _setIndex(self):
        if self.use_cat_val:
            self._setSpecParam('Index', -self.gamma)
        else:
            self._setSpecParam('Index', -2)
    def _setPrefactor(self):
        if self.use_cat_val:
            flux = string.atof(self.fluxSrc.getAttribute('flux').
                               encode('ascii'))
            prefactor = (flux*1e5*(self.gamma-1)/100.
                         /(self.emin**(1-self.gamma)
                           - self.emax**(1-self.gamma)))
            self._setSpecParam('Prefactor', prefactor)
        else:
            self._setSpecParam('Prefactor', 1)
    def _setFlux(self):
        if self.use_cat_val:
            flux = string.atof(self.fluxSrc.getAttribute('flux').
                               encode('ascii'))*1e-04/1e-6
            self._setSpecParam('Integral', flux)
        else:
            self._setSpecParam('Integral', 1)
    def _setSpecParam(self, paramName, value):
        spectrum = self.ptsrc.getElementsByTagName('spectrum')[0]
        params = spectrum.getElementsByTagName('parameter')
        for param in params:
            if param.getAttribute('name').encode('ascii') == paramName:
                param.setAttribute('value', "%.3e" % value)
    def write(self):
        return self.ptsrc.toxml()

class ds9_region_file:
    def __init__(self, filename, targets=(), fk5=0):
        self.filename = filename
        self.fk5 = fk5
        self.SR = None
        self.targets = targets
        self.srcs = {}
    def addSrc(self, src):
        name = src.getAttribute('name').encode()
        dir = src.getElementsByTagName('celestial_dir')[0]
        self.srcs[name] = ( dir.getAttribute('ra').encode('ascii'),
                            dir.getAttribute('dec').encode('ascii') )
    def addSource(self, srcName, src):
        ra, dec = `src.spatialModel.RA.value`, `src.spatialModel.DEC.value`
        self.srcs[srcName] = [ra, dec]
        sourceType = src.node.getAttribute('sourceType').encode()
        if sourceType == 'DRP':
            self.srcs[srcName].append('red')
        elif sourceType == 'Blazar':
            self.srcs[srcName].append('blue')
    def setSR(self, ra, dec, radius):
        self.SR = (ra, dec, radius)
    def write(self):
        file = open(self.filename, 'w')
        file.write("# Region file format: DS9 version 3.0\n")
        file.write('global color=green font="helvetica 10 normal" '
                   + 'select=1 edit=1 move=1 delete=1 include=1 '
                   + 'fixed=0 source\n')
        for src in self.srcs:
            if self.fk5:
                file.write('fk5;point(%s, %s) # point=circle'
                           % tuple(self.srcs[src][:2]))
            else:
                file.write('physical;point(%s, %s) # point=circle' %
                           tuple(self.srcs[src][:2]))
            if src in self.targets:
                file.write(', color=red')
            else:
                try:
                    file.write(', color=%s' % self.srcs[src][2])
                except IndexError:
                    pass
            file.write('\n')
        if self.SR is not None:
            if self.fk5:
                file.write('fk5;circle(%s, %s, %s) # color=red\n' % self.SR)
            else:
                file.write('physical;circle(%s, %s, %s) # color=red\n'
                           % self.SR)

class DefaultValues(object):
    def __init__(self, ra, dec, radius, flux, infile, outfile):
        self.ra, self.dec, self.radius = ra, dec, radius
        self.flux, self.infile, self.outfile = flux, infile, outfile
    def set(self, dialogObject):
        self.ra = dialogObject.ra.value()
        self.dec = dialogObject.dec.value()
        self.radius = dialogObject.radius.value()
        self.flux = dialogObject.fluxLimit.value()
        self.infile = dialogObject.infile.value()
        self.outfile = dialogObject.filename.value()

_defaults = DefaultValues(266.4, -28.9, 20, 0.01,
                          _3EG_catalog, 'my_source_model.xml')
        
class SourceRegionDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent):
        self.parent = parent
        tkSimpleDialog.Dialog.__init__(self, parent)
    def body(self, parent):
        dataFrame = Tkinter.Frame(self)
        dataFrame.pack(anchor=Tkinter.N, expand=Tkinter.YES, fill=Tkinter.X)
        self.title("Source Extraction Region")
        self.ra = ParamDoubleEntry(parent, 'RA', 0, default=_defaults.ra)
        self.dec = ParamDoubleEntry(parent, 'DEC', 1, default=_defaults.dec)
        self.radius = ParamDoubleEntry(parent, 'radius', 2,
                                       default=_defaults.radius)
        self.fluxLimit = ParamDoubleEntry(parent, 'flux limit', 3,
                                          default=_defaults.flux)
        self.infile = ParamFileEntry(parent, 'input file', 4,
                                     default=_defaults.infile)
        self.filename = ParamFileEntry(parent, 'output file', 5,
                                       default=_defaults.outfile)
    def apply(self):
        try:
            srcList = LikeSourceList(self.infile.value())
        except RuntimeError:
            srcList = SourceList(self.infile.value())
        roiCone = (self.ra.value(), self.dec.value(), self.radius.value())
        srcList.extract(self.filename.value(), roiCone,
                        fluxLimit=self.fluxLimit.value())
        _defaults.set(self)
    def ok(self, x=0):
        self.haveSources = 1
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.close()
    def cancel(self):
        self.haveSources = 0
        self.close()
    def close(self):
        self.parent.focus_set()
        self.destroy()

class ParamDoubleEntry:
    def __init__(self, parent, label, row, default=0):
        self.parent = parent
        self.variable = Tkinter.DoubleVar()
        self.variable.set(default)
        name = Tkinter.Label(parent, text=label)
        name.grid(column=0, row=row, sticky=Tkinter.E)
        entry = Tkinter.Entry(parent, textvariable=self.variable,
                              state=Tkinter.NORMAL, width=30)
        entry.grid(column=1, row=row)
    def value(self):
        return self.variable.get()

class ParamStringEntry:
    def __init__(self, parent, label, row, default=''):
        self.parent = parent
        self.variable = Tkinter.StringVar()
        self.variable.set(default)
        name = Tkinter.Label(parent, text = label)
        name.grid(column=0, row=row, sticky=Tkinter.E)
        entry = Tkinter.Entry(parent, textvariable=self.variable,
                              width=30, state=Tkinter.NORMAL)
        entry.grid(column=1, row=row)
    def value(self):
        return self.variable.get()

class ParamFileEntry:
    def __init__(self, parent, label, row, default='', expand=True,
                 pattern=None):
        self.parent = parent
        self.pattern = pattern
        self.expand = expand
        self.variable = Tkinter.StringVar()
        self.variable.set(default)
        file = Tkinter.Button(parent, text=label, command=self.getFile, bd=1)
        file.grid(column=0, row=row, sticky=Tkinter.E)
        entry = Tkinter.Entry(parent, textvariable=self.variable,
                              width=30, state=Tkinter.NORMAL)
        entry.grid(column=1, row=row)
    def value(self):
        return self.variable.get()
    def getFile(self):
        if self.pattern is None:
            file = LoadFileDialog(self.parent).go()
        else:
            file = LoadFileDialog(self.parent).go(self.pattern)
        if file:
            if not self.expand:
                file = os.path.basename(file)
            self.variable.set(file)

if __name__ == '__main__':
    from pil import Pil
    from pfilesPath import *
    try:
        pfile = os.path.join(pfilesPath("extractSources.par"),
                             "extractSources.par")
        pars = Pil(pfile)
        if pars['input_file'] == 'DEFAULT':
            input_file = _3EG_catalog
        else:
            input_file = pars['input_file']
        srcList = SourceList(input_file)
        srcList.extract(pars['output_file'],
                        (pars['ra0'], pars['dec0'], pars['radius']),
                        pars['flux_limit'])
    except ParFileError:
        SourceRegionDialog(Tkinter.Tk())
