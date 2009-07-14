# -*- python -*-
# $Id: SConscript,v 1.6 2008/09/12 20:30:48 glastrm Exp $
# Authors: J. Chiang <jchiang@slac.stanford.edu>
# Version: likeGui-07-09-00
Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()

ObsSimBin = progEnv.Program('ObsSim', 'src/ObsSim.cxx')
ModelEditorBin = progEnv.Program('ModelEditor', 'src/ModelEditor.cxx')

progEnv.Tool('registerTargets', package = 'likeGui', 
             binaryCxts = [[ObsSimBin, progEnv], [ModelEditorBin, progEnv]],
             python = listFiles(['python/*.py']))
