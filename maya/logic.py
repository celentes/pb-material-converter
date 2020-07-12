import maya.cmds as mc
import maya.utils

def get_materials():
    for shading_engine in mc.ls(type='shadingEngine'):
        if mc.sets(shading_engine, q=True):
            for mat in mc.ls(mc.listConnections(shading_engine), materials=True):
                yield mat

def get_material_texture_paths(mat):
    fileNodes = []
    fileNodes.extend(mc.listConnections(mat, type="file"))

    nConnections = mc.listConnections("%s.normalCamera" % mat)
    for c in nConnections:
        fileNodes.extend(mc.listConnections(c, type="file"))

    return [mc.getAttr("%s.fileTextureName" % f) for f in fileNodes]
