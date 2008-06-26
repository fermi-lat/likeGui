# -*- python -*-
# $Id: SConscript,v 1.4 2008/06/19 23:24:38 glastrm Exp $
# Authors: J. Chiang <jchiang@slac.stanford.edu>
# Version: likeGui-07-08-02
Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()

ObsSimBin = progEnv.Program('ObsSim', 'src/ObsSim.cxx')
ModelEditorBin = progEnv.Program('ModelEditor', 'src/ModelEditor.cxx')

progEnv.Tool('registerObjects', package = 'likeGui', 
             binaries = [ObsSimBin, ModelEditorBin],
             python = listFiles(['python/*.py']))
