# -*- python -*-
#$Id: SConscript,v 1.2 2008/02/26 03:42:25 glastrm Exp $

Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()

ObsSimBin = progEnv.Program('ObsSim', 'src/ObsSim.cxx')
ModelEditorBin = progEnv.Program('ModelEditor', 'src/ModelEditor.cxx')

progEnv.Tool('registerObjects', package = 'likeGui', 
             binaries = [ObsSimBin, ModelEditorBin],
             python = listFiles(['python/*.py'])
