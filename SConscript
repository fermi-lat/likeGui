# -*- python -*-
# $Id: SConscript,v 1.5 2008/06/26 15:28:07 glastrm Exp $
# Authors: J. Chiang <jchiang@slac.stanford.edu>
# Version: likeGui-07-09-00
Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()

ObsSimBin = progEnv.Program('ObsSim', 'src/ObsSim.cxx')
ModelEditorBin = progEnv.Program('ModelEditor', 'src/ModelEditor.cxx')

progEnv.Tool('registerObjects', package = 'likeGui', 
             binaries = [ObsSimBin, ModelEditorBin],
             python = listFiles(['python/*.py']))
