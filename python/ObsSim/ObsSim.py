#!/usr/bin/env python
"""
Prototype GUI for obsSim

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header: /nfs/slac/g/glast/ground/cvs/likeGui/python/ObsSim/ObsSim.py,v 1.17 2006/02/07 22:45:56 jchiang Exp $
#
import os, sys, time
import Tkinter as Tk
import tkFileDialog
from tkMessageBox import showwarning
from FileDialog import LoadFileDialog, SaveFileDialog

sys.path.insert(0, os.path.join(os.environ['LIKEGUIROOT'], 'python'))

from SourceLibrary import SourceLibrary
from ParamDialog import ParamDialog
from EditFileDialog import *
from ThreadedClient import runInThread
from pil import Pil
from pfilesPath import pfilesPath
from create_library import makeSrcLib

# @todo replace these with GtApp objects
obsSim = os.path.join(os.environ["OBSERVATIONSIMROOT"],
                      os.environ["BINDIR"], 'gtobssim.exe')
orbSim = os.path.join(os.environ["OBSERVATIONSIMROOT"],
                      os.environ["BINDIR"], 'gtorbsim.exe')
if not os.path.exists(obsSim):
    obsSim = "gtobssim"
if not os.path.exists(orbSim):
    orbSim = "gtorbsim"

class RootWindow(Tk.Tk):
    def __init__(self, file=None):
        Tk.Tk.__init__(self)
        self.title("obsSim GUI")
        menuBar = MenuBar(self)

        inputFrames = Tk.Frame(self)
        inputFrames.pack(side=Tk.LEFT, fill=Tk.BOTH)
        self.srcLibs = SourceLibraries(self, inputFrames)
        self.candidates = CandidateSources(self, inputFrames)

        outputFrame = Tk.Frame(self)
        outputFrame.pack(side=Tk.RIGHT, fill=Tk.BOTH)
        self.sourceList = SourceList(self, outputFrame)

        self.cwd = os.path.abspath('.')

        if file is not None:
            self.srcLibs.addLibs(file)
        else:
            try:
                defaultFiles = open('xmlFiles.txt')
            except:
                xmlFiles = os.path.join(os.environ['OBSERVATIONSIMROOT'],
                                        'xml', 'xmlFiles.txt')
                defaultFiles = open(xmlFiles, 'r')
            for file in defaultFiles:
                if file.strip() != '':
                    self.srcLibs.addLibs(expandEnvVar(file).strip())
    def loadDefaultXmlFiles(self):
        xmlFiles = os.path.join(os.environ['OBSERVATIONSIMROOT'],
                                'xml', 'xmlFiles.txt')
        defaultFiles = open(xmlFiles, 'r')
        for file in defaultFiles:
            if file.strip() != '' and file.find('#') != 0:
                self.srcLibs.addLibs(expandEnvVar(file).strip())
    def open(self, xmlFile=None):
        if xmlFile is None:
            pattern = os.path.join(self.cwd, '*.xml')
            xmlFile = LoadFileDialog(self).go(pattern=pattern)
            try:
                self.cwd = os.path.abspath(os.path.dirname(xmlFile))
            except:
                pass
        if xmlFile is not None:
            try:
                self.srcLibs.addLibs(xmlFile)
            except:
                showwarning("XML Parsing Error: ", "Cannot read " + xmlFile)
        self.save()
    def save(self):
        self.srcLibs.writeXmlFileList()
    def importSrcList(self):
        try:
            inputFile = LoadFileDialog(self, title='Input ascii file:').go()
            time.sleep(0.5)
            saveDialog = SaveFileDialog(self, title='Output xml file:')
            outputFile = saveDialog.go(pattern='*.xml')
            src_lib = makeSrcLib(inputFile)
            outfile = open(outputFile, 'w')
            for line in src_lib:
                outfile.write(line + "\n")
            outfile.close()
            self.open(outputFile)
        except:
            showwarning("Import Error: ", "Cannot parse " + inputFile)
    def cd(self):
        file = tkFileDialog.askdirectory(title="Change working directory:",
                                         mustexist=1)
        try:
            os.chdir(file)
        except:
            pass
        self.cwd = os.path.abspath('.')
    def obsSim(self, xmlList='xmlFiles.txt', sourceNames='source_names.txt'):
        self.srcLibs.writeXmlFileList(xmlList)
        self.sourceList.writeSourceNames(sourceNames)
        pfile = 'gtobssim.par'
        pars = Pil(pfile)
        pars['xml_source_file'] = xmlList
        pars['source_list'] = sourceNames
        pars.write(os.path.join(pfilesPath(), pfile))
        dialog = ParamDialog(self, pfile)
        if dialog.paramString:
            command = " ".join((obsSim, dialog.paramString))
            runInThread(commandApp(command))
    def orbSim(self):
        pfile = 'gtorbsim.par'
        pars = Pil(pfile)
        dialog = ParamDialog(self, pfile)
        if dialog.paramString:
            command = " ".join((orbSim, dialog.paramString))
            runInThread(commandApp(command))
        
class MenuBar(Tk.Menu):
    def __init__(self, parent):
        Tk.Menu.__init__(self)
        self.add_cascade(label="File", menu=FileMenu(parent), underline=0)
        self.add_cascade(label="Run", menu=SimMenu(parent), underline=0)
        self.add_cascade(label="ds9", menu=Ds9Menu(parent), underline=0)
        parent.config(menu=self)

class FileMenu(Tk.Menu):
    def __init__(self, root):
        Tk.Menu.__init__(self, tearoff=0)
        self.add_command(label="cd...", underline=0, command=root.cd)
        self.add_command(label="Quit", underline=0, command=root.quit)
        
class SimMenu(Tk.Menu):
    def __init__(self, root):
        Tk.Menu.__init__(self, tearoff=0)
        self.add_command(label="gtobssim...", command=root.obsSim, underline=1)
        self.add_command(label="gtorbSim...", command=root.orbSim, underline=1)

class Ds9Menu(Tk.Menu):
    def __init__(self, root):
        Tk.Menu.__init__(self, tearoff=0)
        self.add_command(label="Events...", underline=0, command=Ds9(root, 1))
        self.add_command(label="Image...", underline=0, command=Ds9(root))

class Ds9(object):
    def __init__(self, root, events=0):
        self.root = root
        self.events = events
    def __call__(self):
        file = EditFileDialog(self.root).go(pattern='*.fits')
        if file:
            if self.events:
                command = 'ds9 "' + file + '[1][bin=ra,dec]"'
            else:
                command = 'ds9 ' + file
            runInThread(commandApp(command))

class SourceLibraries(Tk.Frame):
    def __init__(self, root, parentFrame):
        self.root = root
        Tk.Frame.__init__(self)
        libFrame = Tk.Frame(parentFrame)
        libFrame.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.menuButton = Tk.Menubutton(libFrame, text='Source Libraries',
                                        relief=Tk.RAISED, bd=2, underline=0)
        self.menuButton.pack(side=Tk.TOP, fill=Tk.X)
        self.menuButton['menu'] = SourceLibMenu(self, self.menuButton)

        self.xScroll = Tk.Scrollbar(libFrame, orient=Tk.HORIZONTAL)
        self.xScroll.pack(side=Tk.BOTTOM, fill=Tk.X)
        self.yScroll = Tk.Scrollbar(libFrame, orient=Tk.VERTICAL)
        self.yScroll.pack(side=Tk.RIGHT, fill=Tk.Y)
        self.listBox = Tk.Listbox(libFrame, selectmode=Tk.BROWSE,
                                  xscrollcommand=self.xScroll.set,
                                  yscrollcommand=self.yScroll.set,
                                  width=30)
        self.listBox.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=Tk.YES)
        btags = self.listBox.bindtags()
        self.listBox.bindtags(btags[1:] + btags[:1])
        self.listBox.bind('<ButtonRelease-1>', self.selectLibrary)
        self.xScroll["command"] = self.listBox.xview
        self.yScroll["command"] = self.listBox.yview
        self.libs = map()
        self.files = []
    def fill(self):
        self.listBox.delete(0, Tk.END)
        for lib in self.libs.ordered_keys:
            self.listBox.insert(Tk.END, lib)
    def addLibs(self, file):
        try:
            srcLibs = SourceLibrary(file)
            file = os.path.abspath(file)
            for lib in srcLibs:
                if lib not in self.libs:
                    self.libs[lib] = (srcLibs[lib], file)
            self.fill()
            if file not in self.files:
                self.files.append(file)
        except:
            showwarning("XML Parsing Error: ", "Cannot read " + file)
    def selectLibrary(self, event=None):
        libname = self.listBox.get('active')
        self.root.candidates.setSrcLib(self.libs[libname][0], libname)
    def deleteSelected(self):
        name = self.listBox.get('active')
        targetfile = self.libs[name][1]
        self.files.remove(targetfile)
        targets = self.libs.keys()
        for lib in targets:
            if self.libs[lib][1] == targetfile:
                del self.libs[lib]
                self.libs.ordered_keys.remove(lib)
        self.fill()
        self.root.candidates.clearAll()
        self.root.candidates.menuButton.config(text='Candidate Sources')
        self.writeXmlFileList()
    def writeXmlFileList(self, file='xmlFiles.txt'):
        outfile = open(file, 'w')
        for item in self.files:
            outfile.write(item + "\n")
        outfile.close()

class SourceLibMenu(Tk.Menu):
    def __init__(self, root, parentFrame):
        Tk.Menu.__init__(self, parentFrame, tearoff=0)
        self.add_command(label='Add source library file...', underline=0,
                         command=root.root.open)
        self.add_command(label='Load default files', underline=0,
                         command=root.root.loadDefaultXmlFiles)
        self.add_command(label='Delete selected', underline=0,
                         command=root.deleteSelected)
        self.add_separator()
        self.add_command(label='Import source list...', underline=0,
                         command=root.root.importSrcList)

class CandidateSources(Tk.Frame):
    def __init__(self, root, parentFrame):
        self.root = root
        Tk.Frame.__init__(self)
        srcFrame = Tk.Frame(parentFrame)
        srcFrame.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.menuButton = Tk.Menubutton(srcFrame, text='Candidate Sources',
                                        relief=Tk.RAISED, bd=2, underline=0)
        self.menuButton.pack(side=Tk.TOP, fill=Tk.X)
        self.menuButton['menu'] = CandidateMenu(self, self.menuButton)

        self.xScroll = Tk.Scrollbar(srcFrame, orient=Tk.HORIZONTAL)
        self.xScroll.pack(side=Tk.BOTTOM, fill=Tk.X)
        self.yScroll = Tk.Scrollbar(srcFrame, orient=Tk.VERTICAL)
        self.yScroll.pack(side=Tk.RIGHT, fill=Tk.Y)
        self.listBox = Tk.Listbox(srcFrame, selectmode=Tk.MULTIPLE,
                                  xscrollcommand=self.xScroll.set,
                                  yscrollcommand=self.yScroll.set,
                                  width=30)
        self.listBox.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=Tk.YES)
        btags = self.listBox.bindtags()
        self.listBox.bindtags(btags[1:] + btags[:1])
        self.listBox.bind('<Button-3>', self.printXml)
        self.listBox.bind('<Double-ButtonRelease-1>', self.addSource)
        self.xScroll["command"] = self.listBox.xview
        self.yScroll["command"] = self.listBox.yview
    def setSrcLib(self, srcLib, libName):
        if len(libName) > 30:
            libName = libName[:30]
        self.menuButton.config(text=libName)
        srcElts = srcLib.getElementsByTagName('source')
        self.sources = map()
        for src in srcElts:
            name = src.getAttribute('name').encode().strip()
            self.sources[name] = src
        self.listBox.delete(0, Tk.END)
        for src in self.sources.ordered_keys:
            self.listBox.insert(Tk.END, src)
    def addSource(self, event):
        src = self.listBox.get('active')
        self.root.sourceList.addSource((src, self.sources[src]))
    def addSelected(self):
        selected = self.selectedSources()
        for srcName in selected:
            self.root.sourceList.addSource((srcName, self.sources[srcName]))
    def selectedSources(self):
        indices = self.listBox.curselection()
        selected = []
        for indx in indices:
            selected.append(self.sources.ordered_keys[int(indx)])
        return selected        
    def addAll(self):
        self.selectAll()
        self.addSelected()
    def selectAll(self):
        self.listBox.selection_set(0, self.listBox.size())
    def unSelectAll(self):
        self.listBox.selection_clear(0, self.listBox.size())
    def clearAll(self):
        self.listBox.delete(0, Tk.END)
        self.root.sourceList.deleteAll()
    def printXml(self, event=None):
        selected = self.selectedSources()
        for name in selected:
            print self.sources[name].toxml() + '\n'

class CandidateMenu(Tk.Menu):
    def __init__(self, root, parentFrame):
        Tk.Menu.__init__(self, parentFrame, tearoff=0)
        self.add_command(label='Add selected', underline=0,
                         command=root.addSelected)
        self.add_command(label='Add all', command=root.addAll)
        self.add_command(label='Select all', underline=0,
                         command=root.selectAll)
        self.add_command(label='Un-select all', underline=0,
                         command=root.unSelectAll)
        self.add_command(label='Print xml', underline=0,
                         command=root.printXml)

class SourceList(Tk.Frame):
    def __init__(self, root, parentFrame):
        Tk.Frame.__init__(self)
        self.root = root
        srcFrame = Tk.Frame(parentFrame)
        srcFrame.pack(side=Tk.RIGHT, fill=Tk.BOTH)

        self.menuButton = Tk.Menubutton(srcFrame, text='Model Sources',
                                        relief=Tk.RAISED, bd=2, underline=0)
        self.menuButton.pack(side=Tk.TOP, fill=Tk.X)
        self.menuButton['menu'] = ModelMenu(self, self.menuButton)

        self.xScroll = Tk.Scrollbar(srcFrame, orient=Tk.HORIZONTAL)
        self.xScroll.pack(side=Tk.BOTTOM, fill=Tk.X)
        self.yScroll = Tk.Scrollbar(srcFrame, orient=Tk.VERTICAL)
        self.yScroll.pack(side=Tk.RIGHT, fill=Tk.Y)
        self.listBox = Tk.Listbox(srcFrame, selectmode=Tk.MULTIPLE,
                                  xscrollcommand=self.xScroll.set,
                                  yscrollcommand=self.yScroll.set,
                                  width=30)
        self.listBox.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=Tk.YES)
        btags = self.listBox.bindtags()
        self.listBox.bindtags(btags[1:] + btags[:1])
        self.listBox.bind('<Double-ButtonRelease-1>', self.printXml)
        self.xScroll["command"] = self.listBox.xview
        self.yScroll["command"] = self.listBox.yview
        self.srcs = map()
    def addSource(self, src):
        if src[0] not in self.srcs:
            self.srcs[src[0]] = src[1]
        self.fill()
    def fill(self):
        self.listBox.delete(0, Tk.END)
        for src in self.srcs.ordered_keys:
            self.listBox.insert(Tk.END, src)
    def deleteSelected(self):
        indices = self.listBox.curselection()
        targets = []
        for indx in indices:
            targets.append(self.srcs.ordered_keys[int(indx)])
        for target in targets:
            self.srcs.delete(target)
        self.fill()
    def deleteAll(self):
        self.selectAll()
        self.deleteSelected()
    def selectAll(self):
        self.listBox.selection_set(0, self.listBox.size())
    def unSelectAll(self):
        self.listBox.selection_clear(0, self.listBox.size())
    def writeSourceNames(self, file='source_names.txt'):
        outfile = open(file, 'w')
        for src in self.srcs.ordered_keys:
            outfile.write(src + "\n")
        outfile.close()
    def printXml(self, event=None):
        name = self.listBox.get('active')
        print self.srcs[name].toxml() + '\n'

class ModelMenu(Tk.Menu):
    def __init__(self, root, parentFrame):
        Tk.Menu.__init__(self, parentFrame, tearoff=0)
        self.add_command(label='Delete selected', underline=0,
                         command=root.deleteSelected)
        self.add_command(label='Delete all', underline=0,
                         command=root.deleteAll)
        self.add_command(label='Select all', underline=0,
                         command=root.selectAll)
        self.add_command(label='Un-select all', underline=0,
                         command=root.unSelectAll)
        
class commandApp:
    def __init__(self, command):
        self.command = command
    def __call__(self):
        output = os.system(self.command)

class map(dict):
    def __init__(self):
        dict.__init__(self)
        self.ordered_keys = []
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if key not in self.ordered_keys:
            self.ordered_keys.append(key)
    def delete(self, key):
        self.ordered_keys.remove(key)        
        del self[key]

def expandEnvVar(filename):
    if filename.find('$(') != -1:
        envVar = filename.split('$(')[1].split(')')[0]
        remainder = filename.split('$(')[1].split(')')[1]
        return os.environ[envVar] + remainder
    else:
        return filename

def ObsSim(filename=None):
    if filename is not None:
        root = RootWindow(filename)
    else:
        root = RootWindow()
    root.mainloop()

if __name__ == "__main__":
    if sys.argv[1:]:
        ObsSim(sys.argv[1])
    else:
        ObsSim()
