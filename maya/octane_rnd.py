import maya.cmds as mc
import os
import logic
import texture_mapping as tm

def create_image(filename, uv):
    name, ext = os.path.splitext(os.path.basename(filename))
    img = mc.shadingNode('octaneImageTexture', name=name, asTexture=True)
    mc.setAttr("%s.File" % img, filename, type='string')
    return img

def set_base_color(mat, img):
    logic.connect_attribute(img, 'outTex', mat, 'Albedo')

def set_metalness(mat, img):
    logic.connect_attribute(img, 'outTex', mat, 'Metallic')

def set_roughness(mat, img):
    logic.connect_attribute(img, 'outTex', mat, 'Roughness')

def set_normal(mat, img):
    #normal = mc.shadingNode('aiNormalMap', name='%s_normal' % mat, asUtility=True)
    #logic.connect_attribute(normal, 'outValue', mat, 'normalCamera')
    logic.connect_attribute(img, 'outTex', mat, 'Normal')

def set_specular(mat, img):
    logic.connect_attribute(img, 'outTex', mat, 'Specular')

def set_emission(mat, img):
    emi = mc.shadingNode('octaneTextureEmission', name="%s_texEmission" % mat, asUtility=True)
    logic.connect_attribute(img, 'outTex', emi, 'Efficiency')
    logic.connect_attribute(emi, 'outEmission', mat, 'Emission')

def set_displacement(mat, sg, img):
    disp = mc.shadingNode('octaneDisplacementNode', name="%s_displacement" % mat, asUtility=True)
    mc.setAttr("%s.DetLevel" % disp, 12)
    mc.setAttr("%s.DisplacementDir" % disp, 3)
    mc.setAttr("%s.Offset" % disp, 0.5)
    mc.setAttr("%s.Height" % disp, 1.0)
    mc.setAttr("%s.frozen" % disp, True)
    logic.connect_attribute(img, 'outTex', disp, 'Texture')
    logic.connect_attribute(disp, 'outDisp', mat, 'Displacement')

def set_opacity(mat, img):
    logic.connect_attribute(img, 'outTex', mat, 'Opacity')

def set_bump(mat, img):
    logic.connect_attribute(img, 'outTex', mat, 'Bump')

def bind_texture(mat, sg, img, tex_type):
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
        return set_displacement(mat, sg, img)
    if tex_type == "Opacity":
        return set_opacity(mat, img)
    if tex_type == "Bump":
        return set_bump(mat, img)

def get_binding_name(tex_type):
    if tex_type == "Diffuse":
        return "Albedo"
    if tex_type == "Metalness":
        return "Metallic"
    if tex_type == "Specular":
        return "Specular"
    if tex_type == "Roughness":
        return "Roughness"
    if tex_type == "Normal":
        return "Normal"
    if tex_type == "Emission":
        return "Emission"
    if tex_type == "Displacement":
        return "Displacement"
    if tex_type == "Opacity":
        return "Opacity"
    if tex_type == "Bump":
        return "Bump"
    return tm.NOTMAPPED_STR

def upgrade_material(mat, directory):
    name = logic.truncate_material_name(mat)
    texfiles = tm.get_texture_filenames([directory], name)

    surface, sg = logic.create_material(mat, "octaneUniversalMaterial", "%s_mtl" % name)
    uv = mc.shadingNode('place2dTexture', name="%s_uv" % name, asUtility=True)
    for tex_path in texfiles:
        tex_type = tm.get_texture_type(name, tex_path)
        binding = get_binding_name(tex_type)
        if binding == tm.NOTMAPPED_STR:
            continue
        else:
            img = create_image(tex_path, uv)
            bind_texture(surface, sg, img, tex_type)

    return surface
