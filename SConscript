# -*- python -*-
# $Id: SConscript,v 1.14 2015/03/06 03:01:22 jchiang Exp $
# Authors: J. Chiang <jchiang@slac.stanford.edu>
# Version: likeGui-07-11-01
Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()

ObsSimBin = progEnv.Program('ObsSim', 'src/ObsSim.cxx')
ModelEditorBin = progEnv.Program('ModelEditor', 'src/ModelEditor.cxx')

python_files = ['python/EditFileDialog.py', 
                'python/FuncFactory.py', 
                'python/ModelEditor.py', 
                'python/ParamDialog.py',
                'python/ThreadedClient.py', 
                'python/celgal.py', 
                'python/saclay_celgal.py', 
                'python/ds9.py', 
                'python/extractSources.py',
                'python/mySimpleDialog.py',
                'python/ObsSim/ObsSim.py',
                'python/ObsSim/SourceLibrary.py',
                'python/ObsSim/create_library.py',
                'python/ObsSim/__init__.py']

progEnv.Tool('registerTargets', package='likeGui', 
             binaryCxts=[[ObsSimBin, progEnv], [ModelEditorBin, progEnv]],
             python=python_files)
