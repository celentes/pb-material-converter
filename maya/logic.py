import maya.cmds as mc

def truncate_material_name(mat):
    name = mat
    if re.search("_ncl1_1", mat):
        name = mat[:-7]
    idx = name.rfind(":")
    if idx != -1:
        name = name[-idx+1:]
    return name

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

def get_directory(mats):
    texture_paths = []
    for m in mats:
        texture_paths.extend(get_material_texture_paths(m))
    dir_hints = get_directory_hints(texture_paths) # tm
    return dir_hints[0]

def get_materials_and_directory():
    mats = [x for x in get_materials()]
    return [mats, get_directory(mats)]

def connect_attribute(nodeOut, attrOut, nodeIn, attrIn):
    mc.connectAttr("%s.%s" % (nodeOut, attrOut), "%s.%s" % (nodeIn, attrIn), force=True)

def create_material(type, name):
    surface = mc.shadingNode(type, name=name, asShader=True)
    sg = mc.sets(name="%s_SG" % name, renderable=True, noSurfaceShader=True, empty=True)
    connect_attribute(surface, "outColor", sg, "surfaceShader")
    return [surface, sg]
