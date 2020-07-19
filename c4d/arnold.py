import c4d
import texture_mapping as tm
import os

# from api/include/util/Constants.h
C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_PARAM1 = 2001
C4DTOA_MSG_PARAM2 = 2002
C4DTOA_MSG_PARAM3 = 2003
C4DTOA_MSG_PARAM4 = 2004
C4DTOA_MSG_RESP1 = 2011
C4DTOA_MSG_ADD_SHADER = 1029
C4DTOA_MSG_ADD_CONNECTION = 1031
C4DTOA_MSG_CONNECT_ROOT_SHADER = 1033

# from c4dtoa_symbols.h
ARNOLD_SHADER_NETWORK = 1033991
ARNOLD_SHADER_GV = 1033990

# from api/include/util/ArnolShaderNetworkUtil.h
ARNOLD_BEAUTY_PORT_ID = 537905099
ARNOLD_DISPLACEMENT_PORT_ID = 537905100

# from api/include/util/NodeIds.h
C4DAIN_STANDARD_SURFACE = 314733630
C4DAIN_NORMAL_MAP = 1512478027
C4DAIN_IMAGE = 262700200
C4DAINGV_DISPLACEMENT = 102727166

# from res/description/ainode_normal_map.h
C4DAIP_NORMAL_MAP_NORMAL = 423473794

# from res/description/ainode_standard_surface.h
C4DAI_STANDARD_SURFACE_MATERIAL_TYPE = 1630484996
C4DAIP_STANDARD_SURFACE_BASE_COLOR = 1044225467
C4DAIP_STANDARD_SURFACE_DIFFUSE_ROUGHNESS = 2099493681
C4DAIP_STANDARD_SURFACE_NORMAL = 244376085
C4DAIP_STANDARD_SURFACE_SPECULAR_COLOR = 801517079
C4DAIP_STANDARD_SURFACE_SPECULAR_ROUGHNESS = 1876347704
C4DAIP_STANDARD_SURFACE_METALNESS  = 1875191464
C4DAIP_STANDARD_SURFACE_EMISSION = 108737517
C4DAIP_STANDARD_SURFACE_EMISSION_COLOR = 274240561
C4DAIP_STANDARD_SURFACE_OPACITY = 784568645

# from res/description/gvaishader_displacement.h
C4DAI_NORMAL_DISPLACEMENT_INPUT = 737403364

# from res/description/ainode_image.h
C4DAIP_IMAGE_FILENAME = 1737748425

# from res/description/arnold_shader_network_material.h
C4DAI_SNMATERIAL_ALPHA_TEXTURE = 206
C4DAI_SNMATERIAL_ALPHA_MODE = 211
C4DAI_SNMATERIAL_ALPHA__TEXTURE = 1

def create_shader(material, nodeId, posx, posy):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_ADD_SHADER)
    msg.SetInt32(C4DTOA_MSG_PARAM1, ARNOLD_SHADER_GV)
    msg.SetInt32(C4DTOA_MSG_PARAM2, nodeId)
    msg.SetInt32(C4DTOA_MSG_PARAM3, posx)
    msg.SetInt32(C4DTOA_MSG_PARAM4, posy)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetLink(C4DTOA_MSG_RESP1)

def set_root_shader(material, shader, rootPortId):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_CONNECT_ROOT_SHADER)
    msg.SetLink(C4DTOA_MSG_PARAM1, shader)
    msg.SetInt32(C4DTOA_MSG_PARAM2, 0)
    msg.SetInt32(C4DTOA_MSG_PARAM3, rootPortId)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetBool(C4DTOA_MSG_RESP1)

def add_connection(material, srcNode, dstNode, dstPortId):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_ADD_CONNECTION)
    msg.SetLink(C4DTOA_MSG_PARAM1, srcNode)
    msg.SetInt32(C4DTOA_MSG_PARAM2, 0)
    msg.SetLink(C4DTOA_MSG_PARAM3, dstNode)
    msg.SetInt32(C4DTOA_MSG_PARAM4, dstPortId)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetBool(C4DTOA_MSG_RESP1)

def create_texture(mat, filename):
    image = create_shader(mat, C4DAIN_IMAGE, 0, 50)
    image.GetOpContainerInstance().SetFilename(C4DAIP_IMAGE_FILENAME, filename)
    image.SetName(os.path.basename(filename))
    return image

def set_base_color(mat, filename, dstNode):
    image = create_texture(mat, filename)
    return add_connection(mat, image, dstNode, C4DAIP_STANDARD_SURFACE_BASE_COLOR)

def set_metalness(mat, filename, dstNode):
    image = create_texture(mat, filename)
    return add_connection(mat, image, dstNode, C4DAIP_STANDARD_SURFACE_METALNESS)

def set_roughness(mat, filename, dstNode):
    image = create_texture(mat, filename)
    return add_connection(mat, image, dstNode, C4DAIP_STANDARD_SURFACE_SPECULAR_ROUGHNESS)

def set_specular(mat, filename, dstNode):
    image = create_texture(mat, filename)
    return add_connection(mat, image, dstNode, C4DAIP_STANDARD_SURFACE_SPECULAR_COLOR)

def set_emission(mat, filename, dstNode):
    image = create_texture(mat, filename)
    dstNode[C4DAIP_STANDARD_SURFACE_EMISSION] = 1.0
    return add_connection(mat, image, dstNode, C4DAIP_STANDARD_SURFACE_EMISSION_COLOR)

def set_normal(mat, filename, dstNode):
    image = create_texture(mat, filename)
    normal_map = create_shader(mat, C4DAIN_NORMAL_MAP, 0, 50)
    add_connection(mat, image, normal_map, C4DAIP_NORMAL_MAP_NORMAL)
    return add_connection(mat, normal_map, dstNode, C4DAIP_STANDARD_SURFACE_NORMAL)

def set_displacement(mat, filename, _=None):
    image = create_texture(mat, filename)
    displacement = create_shader(mat, C4DAINGV_DISPLACEMENT, 150, 200)
    displacement.SetName("displacement")
    set_root_shader(mat, displacement, ARNOLD_DISPLACEMENT_PORT_ID)
    return add_connection(mat, image, displacement, C4DAI_NORMAL_DISPLACEMENT_INPUT)

def set_opacity(mat, filename, dstNode):
    image = create_texture(mat, filename)
    return add_connection(mat, image, dstNode, C4DAIP_STANDARD_SURFACE_OPACITY)
    #image = c4d.BaseShader(c4d.Xbitmap)
    #image[c4d.BITMAPSHADER_FILENAME] = filename
    #mat[C4DAI_SNMATERIAL_ALPHA_MODE] = C4DAI_SNMATERIAL_ALPHA__TEXTURE
    #mat[c4d.C4DAI_SNMATERIAL_ALPHA_LINK] = image
    #return True

def create_material(name):
    mat = c4d.BaseMaterial(ARNOLD_SHADER_NETWORK)
    mat.SetName(name)

    standard_surface = create_shader(mat, C4DAIN_STANDARD_SURFACE, 150, 100)
    standard_surface.SetName("standard_surface")
    standard_surface[C4DAI_STANDARD_SURFACE_MATERIAL_TYPE] = 0

    set_root_shader(mat, standard_surface, ARNOLD_BEAUTY_PORT_ID)
    return [mat, standard_surface]

def get_binding_name(tex_type):
    if tex_type == "Diffuse":
        return "Color < Base < Main"
    if tex_type == "Metalness":
        return "Metalness < Base < Main"
    if tex_type == "Specular":
        return "Color < Specular < Main"
    if tex_type == "Roughness":
        return "Roughness < Specular < Main"
    if tex_type == "Normal":
        return "Normal < Geometry < Main"
    if tex_type == "Emission":
        return "Color < Emission < Main"
    if tex_type == "Displacement":
        return "Displacement < Main"
    if tex_type == "Opacity":
        return "Cutout opacity < Geometry < Main"
    return tm.NOTMAPPED_STR

def bind_texture(mat, ss, tex_path, tex_type):
    if tex_type == "Diffuse":
        return set_base_color(mat, tex_path, ss)
    if tex_type == "Metalness":
        return set_metalness(mat, tex_path, ss)
    if tex_type == "Specular":
        return set_specular(mat, tex_path, ss)
    if tex_type == "Roughness":
        return set_roughness(mat, tex_path, ss)
    if tex_type == "Normal":
        return set_normal(mat, tex_path, ss)
    if tex_type == "Emission":
        return set_emission(mat, tex_path, ss)
    if tex_type == "Displacement":
        return set_displacement(mat, tex_path, ss)
    if tex_type == "Opacity":
        return set_opacity(mat, tex_path, ss)

def upgrade_material(mat, directories):
    name = mat.GetName()
    texfiles = tm.get_texture_filenames(directories, name)

    arn_mat, ss = create_material(name)
    for tex_path in texfiles:
        tex_type = tm.get_texture_type(name, tex_path)
        binding = get_binding_name(tex_type)
        if binding == tm.NOTMAPPED_STR:
            continue
        else:
            bind_texture(arn_mat, ss, tex_path, tex_type)
    doc = c4d.documents.GetActiveDocument()
    doc.InsertMaterial(arn_mat)
    return arn_mat
