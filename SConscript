# -*- python -*-
# $Id: SConscript,v 1.8 2009/07/15 18:33:41 glastrm Exp $
# Authors: J. Chiang <jchiang@slac.stanford.edu>
# Version: likeGui-07-09-02
Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()

ObsSimBin = progEnv.Program('ObsSim', 'src/ObsSim.cxx')
ModelEditorBin = progEnv.Program('ModelEditor', 'src/ModelEditor.cxx')

progEnv.Tool('registerTargets', package = 'likeGui', 
             binaryCxts = [[ObsSimBin, progEnv], [ModelEditorBin, progEnv]],
             python = listFiles(['python/*.py']))
