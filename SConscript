# -*- python -*-
# $Id: SConscript,v 1.7 2009/07/14 23:22:54 jrb Exp $
# Authors: J. Chiang <jchiang@slac.stanford.edu>
# Version: likeGui-07-09-01
Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()

ObsSimBin = progEnv.Program('ObsSim', 'src/ObsSim.cxx')
ModelEditorBin = progEnv.Program('ModelEditor', 'src/ModelEditor.cxx')

progEnv.Tool('registerTargets', package = 'likeGui', 
             binaryCxts = [[ObsSimBin, progEnv], [ModelEditorBin, progEnv]],
             python = listFiles(['python/*.py']))
