import maya.cmds as mc
import os, re, sys, imp

import pymel.util

p = ''
for path in pymel.util.getEnv("MAYA_PLUG_IN_PATH").split(';'):
    if os.path.exists(path + '/PhotobashMaterialConverter'):
        p = path + '/PhotobashMaterialConverter'

sys.path.append(p)
import ui, texture_mapping, logic, arnold_rnd
print p

def initializePlugin(mobj):
    print "creating ui"
    ui.create_ui()

def uninitializePlugin(mobj):
    ui.delete_ui('Photobash Material Converter')
