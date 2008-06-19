# -*- python -*-
# $Id: SConscript,v 1.3 2008/03/27 16:18:25 jchiang Exp $
# Authors: J. Chiang <jchiang@slac.stanford.edu>
# Version: likeGui-07-08-02
Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()

ObsSimBin = progEnv.Program('ObsSim', 'src/ObsSim.cxx')
ModelEditorBin = progEnv.Program('ModelEditor', 'src/ModelEditor.cxx')

progEnv.Tool('registerObjects', package = 'likeGui', 
             binaries = [ObsSimBin, ModelEditorBin],
             python = listFiles(['python/*.py'])
