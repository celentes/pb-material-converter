import maya.cmds as mc

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

def connect_attribute(nodeOut, attrOut, nodeIn, attrIn):
    mc.connectAttr("%s.%s" % (nodeOut, attrOut), "%s.%s" % (nodeIn, attrIn), force=True)

def create_material(type, name):
    surface = mc.shadingNode(type, name=name, asShader=True)
    sg = mc.sets(name="%s_SG", renderable=True, noSurfaceShader=True, emtpy=True)
    connect_attribute(surface, "outColor", sg, "surfaceShader")
    return [surface, sg]
