#!/usr/bin/env python
"""
Prototype GUI for obsSim

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import sys
import copy
import string
import Tkinter as Tk

sys.path.insert(0, '..')

from FileDialog import Dialog, LoadFileDialog, SaveFileDialog
from tkMessageBox import showwarning
import mySimpleDialog

from SourceLibrary import SourceLibrary
import FuncFactory as funcFactory
import findSrcs
ds9 = None

class RootWindow(Tk.Tk):
    def __init__(self):
        Tk.Tk.__init__(self)
        menuBar = MenuBar(self)

        outputFrame = Tk.Frame(self)
        outputFrame.pack(side=Tk.RIGHT, fill=Tk.BOTH)
        self.sourceList = SourceList(self, outputFrame)

        inputFrames = Tk.Frame(self)
        inputFrames.pack()
        self.srcLibs = SourceLibraries(self, inputFrames)
        self.candidates = CandidateSources(self, inputFrames)

    def open(self, xmlFile=None):
        if xmlFile is None:
            xmlFile = LoadFileDialog(self).go(pattern='*.xml')
        self.srcLibs.addLibs(xmlFile)
    def save(self):
        pass
    def saveAs(self):
        pass
        
class MenuBar(Tk.Menu):
    def __init__(self, parent):
        Tk.Menu.__init__(self)
        self.add_cascade(label="File", menu=FileMenu(parent), underline=0)
        if ds9 is not None:
            self.add_cascade(label="ds9", menu=ds9Menu(parent), underline=0)
        parent.config(menu=self)

class FileMenu(Tk.Menu):
    def __init__(self, root):
        Tk.Menu.__init__(self, tearoff=0)
        self.root = root
        self.add_command(label="Open...", underline=0, command=root.open)
        self.add_command(label="Save", underline=0, command=root.save)
        self.add_command(label="Save as...", command=root.saveAs)
        self.add_command(label="Quit", underline=0, command=root.quit)

class SourceList(Tk.Frame):
    def __init__(self, root, parentFrame):
        Tk.Frame.__init__(self)
        self.root = root
        srcFrame = Tk.Frame(parentFrame)
        srcFrame.pack(side=Tk.RIGHT, fill=Tk.BOTH)

        self.menuButton = Tk.Menubutton(srcFrame, text='Model Sources',
                                        relief=Tk.RAISED, bd=2, underline=0)
        self.menuButton.pack(side=Tk.TOP, fill=Tk.X)
        self.menuButton['menu'] = ModelMenu(self.menuButton)

        self.xScroll = Tk.Scrollbar(srcFrame, orient=Tk.HORIZONTAL)
        self.xScroll.pack(side=Tk.BOTTOM, fill=Tk.X)
        self.yScroll = Tk.Scrollbar(srcFrame, orient=Tk.VERTICAL)
        self.yScroll.pack(side=Tk.RIGHT, fill=Tk.Y)
        self.listBox = Tk.Listbox(srcFrame, selectmode=Tk.BROWSE,
                                  xscrollcommand=self.xScroll.set,
                                  yscrollcommand=self.yScroll.set,
                                  width=30)
        self.listBox.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=Tk.YES)
        btags = self.listBox.bindtags()
        self.listBox.bindtags(btags[1:] + btags[:1])
#        self.listBox.bind('<ButtonRelease-1>', self.selectLibrary)
        self.xScroll["command"] = self.listBox.xview
        self.yScroll["command"] = self.listBox.yview
        self.srcs = {}
    def addSource(self, src):
        if src not in self.srcs:
            self.srcs[src] = src

class Foo(object):
    def __init__(self, name):
        self.name = name
    def __call__(self):
        print self.name

def pwd():
    print ds9.cd()

class ds9Menu(Tk.Menu):
    def __init__(self, root):
        Tk.Menu.__init__(self, tearoff=0)
        self.add_command(label="Display sources", underline=0,
                         command=ds9Display(root))

class ds9Display(object):
    def __init__(self, root, file="ds9.reg"):
        self.root = root
        self.file = file
    def __call__(self):
        try:
            ds9.cd(os.path.abspath(os.curdir))
            ds9.clear_regions()
            try:
                os.remove(self.file)
            except OSError:
                pass
            region_file = findSrcs.ds9_region_file(self.file, fk5=1)
            for srcName in self.root.srcModel.names():
                src = self.root.srcModel[srcName]
                if src.type == "PointSource":
                    region_file.addSource(src)
                    region_file.write()
            ds9.load_regions(self.file)
        except RuntimeError:
            pass

class SourceLibraries(Tk.Frame):
    def __init__(self, root, parentFrame):
        self.root = root
        self.parentFrame = parentFrame
        Tk.Frame.__init__(self)
        libFrame = Tk.Frame(self.parentFrame)
        libFrame.pack(side=Tk.TOP, fill=Tk.BOTH)
        label = Tk.Label(libFrame, text='Source Libraries')
        label.pack(side=Tk.TOP, fill=Tk.X)
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
        self.libs = {}
    def fill(self):
        self.listBox.delete(0, Tk.END)
        for lib in self.libs:
            self.listBox.insert(Tk.END, lib)
    def addLibs(self, file):
        srcLibs = SourceLibrary(file)
        for lib in srcLibs:
            if lib not in self.libs:
                self.libs[lib] = srcLibs[lib]
        self.fill()
    def selectLibrary(self, event=None):
        libname = self.listBox.get('active')
        self.root.candidates.setSrcLib(self.libs[libname])

class CandidateSources(Tk.Frame):
    def __init__(self, root, parentFrame):
        self.root = root
        self.parentFrame = parentFrame
        Tk.Frame.__init__(self)
        srcFrame = Tk.Frame(self.parentFrame)
        srcFrame.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.menuButton = Tk.Menubutton(srcFrame, text='Candidate Sources',
                                        relief=Tk.RAISED, bd=2, underline=0)
        self.menuButton.pack(side=Tk.TOP, fill=Tk.X)
        self.menuButton['menu'] = CandidateMenu(self.menuButton)

        self.xScroll = Tk.Scrollbar(srcFrame, orient=Tk.HORIZONTAL)
        self.xScroll.pack(side=Tk.BOTTOM, fill=Tk.X)
        self.yScroll = Tk.Scrollbar(srcFrame, orient=Tk.VERTICAL)
        self.yScroll.pack(side=Tk.RIGHT, fill=Tk.Y)
        self.listBox = Tk.Listbox(srcFrame, selectmode=Tk.BROWSE,
                                  xscrollcommand=self.xScroll.set,
                                  yscrollcommand=self.yScroll.set,
                                  width=30)
        self.listBox.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=Tk.YES)
        btags = self.listBox.bindtags()
        self.listBox.bindtags(btags[1:] + btags[:1])
        self.listBox.bind('<ButtonRelease-1>', self.selectSource)
        self.xScroll["command"] = self.listBox.xview
        self.yScroll["command"] = self.listBox.yview
    def setSrcLib(self, srcLib):
        srcElts = srcLib.getElementsByTagName('source')
        self.sources = []
        for src in srcElts:
            self.sources.append(src.getAttribute('name').encode())
        self.listBox.delete(0, Tk.END)
        for src in self.sources:
            self.listBox.insert(Tk.END, src)
    def selectSource(self, event=None):
        src = self.listBox.get('active')
        print src

class CandidateMenu(Tk.Menu):
    def __init__(self, root):
        Tk.Menu.__init__(self, root, tearoff=0)
        self.add_command(label='Add selected', underline=0,
                         command=Foo('Add selected'))
        self.add_command(label='Select all', underline=0,
                         command=Foo('Select all'))
        self.add_command(label='Clear all', underline=0,
                         command=Foo('Clear all'))

class ModelMenu(Tk.Menu):
    def __init__(self, root):
        Tk.Menu.__init__(self, root, tearoff=0)
        self.add_command(label='Delete selected', underline=0,
                         command=Foo('Add selected'))
        self.add_command(label='Select all', underline=0,
                         command=Foo('Select all'))
        self.add_command(label='Clear all', underline=0,
                         command=Foo('Clear all'))


if __name__ == "__main__":
    root = RootWindow()
    root.mainloop()
