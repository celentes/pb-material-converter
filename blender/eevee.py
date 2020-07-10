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
    "Displacement" : "Displacement",
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

def map_displacement(material, img_node):
    displacement = material.node_tree.nodes.new('ShaderNodeDisplacement')
    material.node_tree.links.new(displacement.outputs['Displacement'], material.node_tree.nodes['Material Output'].inputs['Displacement'])
    material.node_tree.links.new(img_node.outputs['Color'], displacement.inputs['Height'])
    normals = [x for x in material.node_tree.nodes if x.bl_idname == 'ShaderNodeNormalMap']
    if len(normals) > 0:
        material.node_tree.links.new(normals[0].outputs['Normal'], displacement.inputs['Normal'])
