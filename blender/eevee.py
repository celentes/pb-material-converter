import bpy
from . import texture_mapping as tm

TEXTURE_MAPPING = {
    "Diffuse" : "Base Color",
    "Specular" : "Specular",
    "Metalness" : "Metallic",
    "Roughness" : "Roughness",
    "Emission" : "Emission",
    "Normal" : "Normal",
    "Opacity" : "Alpha",
}

def material_node():
    return 'ShaderNodeBsdfPrincipled'

def surface_output():
    return 'BSDF'

def is_surface_correct(surfaceShader):
    return surfaceShader.bl_idname == material_node()

def map_texture_type(textype):
    if textype in TEXTURE_MAPPING:
        return TEXTURE_MAPPING[textype]
    else:
        return tm.NOTMAPPED_STR


