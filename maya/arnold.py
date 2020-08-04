import maya.cmds as mc
import os
#from . import logic as l

def create_image(filename, uv):
    name, ext = os.path.splitext(os.path.basename(filename))
    img = mc.shadingNode('file', name=name, asTexture=True)
    mc.setAttr("%s.fileTextureName" % img, filename, type='string')
    connect_attribute(uv, 'outUV', img, 'uvCoord')
    return img

def set_base_color(mat, img):
    connect_attribute(img, 'outColor', mat, 'baseColor')
    # change base color weight from 0.8 to 1.0
    mc.setAttr("%s.base" % mat, 1.0)

def set_metalness(mat, img):
    connect_attribute(img, 'outAlpha', mat, 'metalness')

def set_roughness(mat, img):
    connect_attribute(img, 'outAlpha', mat, 'specularRoughness')

def set_normal(mat, img):
    normal = mc.shadingNode('aiNormalMap', name='%s_normal' % mat, asUtility=True)
    connect_attribute(normal, 'outValue', mat, 'normalCamera')
    connect_attribute(img, 'outColor', normal, 'input')

def set_specular(mat, img):
    connect_attribute(img, 'outAlpha', mat, 'specular')

def set_emission(mat, img):
    connect_attribute(img, 'outAlpha', mat, 'emission')

def set_displacement(mat, img):
    disp = mc.shadingNode('displacementShader', name="%s_displacement" % mat, asShader=True)
    connect_attribute(disp, 'displacement', "%s_SG" % mat, 'displacementShader')
    connect_attribute(img, 'outAlpha', disp, 'displacement')

def set_opacity(mat, img):
    connect_attribute(img, 'outColor', mat, 'opacity')

def bind_texture(mat, img, tex_type):
    if tex_type == "Diffuse":
        return set_base_color(mat, img)
    if tex_type == "Metalness":
        return set_metalness(mat, img)
    if tex_type == "Specular":
        return set_specular(mat, img)
    if tex_type == "Roughness":
        return set_roughness(mat, img)
    if tex_type == "Normal":
        return set_normal(mat, img)
    if tex_type == "Emission":
        return set_emission(mat, img)
    if tex_type == "Displacement":
        return set_displacement(mat, img)
    if tex_type == "Opacity":
        return set_opacity(mat, img)

def get_binding_name(tex_type):
    if tex_type == "Diffuse":
        return "Base Color"
    if tex_type == "Metalness":
        return "Metalness"
    if tex_type == "Specular":
        return "Specular"
    if tex_type == "Roughness":
        return "Specular Roughness"
    if tex_type == "Normal":
        return "Normal"
    if tex_type == "Emission":
        return "Emission"
    if tex_type == "Displacement":
        return "Displacement"
    if tex_type == "Opacity":
        return "Opacity"
    return NOTMAPPED_STR # tm

def upgrade_material(mat, directory):
    name = truncate_material_name(mat) # logic
    texfiles = get_texture_filenames([directory], name) # tm

    surface, sg = create_material("standardSurface", "%s_arnold" % name) # logic
    uv = mc.shadingNode('place2dTexture', name="%s_uv" % name, asUtility=True)
    for tex_path in texfiles:
        tex_type = get_texture_type(name, tex_path)
        binding = get_binding_name(tex_type)
        if binding == NOTMAPPED_STR: # tm
            continue
        else:
            img = create_image(tex_path, uv)
            bind_texture(surface, img, tex_type)

    return surface
