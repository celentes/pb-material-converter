import maya.cmds as mc
import os
import logic
import texture_mapping as tm

def create_image(filename, uv):
    name, ext = os.path.splitext(os.path.basename(filename))
    img = mc.shadingNode('file', name=name, asTexture=True)
    mc.setAttr("%s.fileTextureName" % img, filename, type='string')
    logic.connect_attribute(uv, 'outUV', img, 'uvCoord')
    return img

def set_base_color(mat, img):
    logic.connect_attribute(img, 'outColor', mat, 'color')

def set_metalness(mat, img):
    logic.connect_attribute(img, 'outAlpha', mat, 'metalness')

def set_roughness(mat, img):
    iv = mc.shadingNode('reverse', name='%s_rgh_reverse' % mat, asUtility=True)
    logic.connect_attribute(img, 'outAlpha', iv, 'inputX')
    logic.connect_attribute(iv, 'outputX', mat, 'reflectionGlossiness')

def set_normal(mat, img):
    logic.connect_attribute(img, 'outColor', mat, 'bumpMap')

def set_specular(mat, img):
    logic.connect_attribute(img, 'outColor', mat, 'reflectionColor')

def set_emission(mat, img):
    logic.connect_attribute(img, 'outColor', mat, 'illumColor')

def set_displacement(mat, img):
    disp = mc.shadingNode('displacementShader', name="%s_displacement" % mat, asShader=True)
    logic.connect_attribute(disp, 'displacement', "%s_SG" % mat, 'displacementShader')
    logic.connect_attribute(img, 'outAlpha', disp, 'displacement')

def set_opacity(mat, img):
    logic.connect_attribute(img, 'outColor', mat, 'opacityMap')

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
        return "Color"
    if tex_type == "Metalness":
        return "Metalness"
    if tex_type == "Specular":
        return "Reflection Color"
    if tex_type == "Roughness":
        return "Reflection Glossines (inverted)"
    if tex_type == "Normal":
        return "Bump Map"
    if tex_type == "Emission":
        return "Illum Color"
    if tex_type == "Displacement":
        return "Displacement"
    if tex_type == "Opacity":
        return "Opacity Map"
    return tm.NOTMAPPED_STR

def upgrade_material(mat, directory):
    name = logic.truncate_material_name(mat)
    texfiles = tm.get_texture_filenames([directory], name)

    surface, sg = logic.create_material("VRayMtl", "%s_mtl" % name)
    uv = mc.shadingNode('place2dTexture', name="%s_uv" % name, asUtility=True)
    for tex_path in texfiles:
        tex_type = tm.get_texture_type(name, tex_path)
        binding = get_binding_name(tex_type)
        if binding == tm.NOTMAPPED_STR:
            continue
        else:
            img = create_image(tex_path, uv)
            bind_texture(surface, img, tex_type)

    return surface
