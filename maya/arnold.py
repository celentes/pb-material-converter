import maya.cmds as mc
from . import logic as l

def create_material(name):
    return l.create_material("standardSurface", "%s_arnold" % name)
