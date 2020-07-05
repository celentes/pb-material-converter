import bpy
from . import texture_mapping as tm

TEXTURE_MAPPING = {
    "Diffuse" : "Albedo color",
    "Specular" : "Specular",
    "Metalness" : "Metallic",
    "Roughness" : "Roughness",
    "Bump" : "Bump",
    "Normal" : "Normal",
    "Displacement" : "Displacement",
    "Opacity" : "Opacity",
    "Emission" : "Emission",
}

def material_node():
    return 'ShaderNodeOctUniversalMat'

def surface_output():
    return 'OutMat'

def is_surface_correct(surfaceShader):
    return surfaceShader.bl_idname == material_node()

def map_displacement(material, img_node):
    displacement = material.node_tree.nodes.new('ShaderNodeOctDisplacementTex')
    surface = material.node_tree.nodes['Universal Material']
    material.node_tree.links.new(displacement.outputs['OutDisplacement'], surface.inputs['Displacement'])
    material.node_tree.links.new(img_node.outputs['Color'], displacement.inputs['Texture'])

def map_texture_type(textype):
    if textype in TEXTURE_MAPPING:
        return TEXTURE_MAPPING[textype]
    else:
        return tm.NOTMAPPED_STR
