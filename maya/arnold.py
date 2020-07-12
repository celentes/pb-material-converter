import maya.cmds as mc

def create_material(name):
    mat = mc.shadingNode("standardSurface", name=name, asShader=True)
    ss = mc.sets(name="%sSG" % mat, renderable=True, noSurfaceShader=True, empty=True)
    mc.connectAttr("%s.outColor" % mat, "%s.surfaceShader" % ss, force=True)
    return [mat, ss]
