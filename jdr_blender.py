import bpy
import os

# retrieving objects sample
objs = [x for x in bpy.data.objects if x.active_material is not None]

# get particular material
cube_mat = bpy.data.objects['ScifiCube_01'].active_material

# get all nodes in material
[x.bl_idname for x in cube_mat.node_tree.nodes]

# get all links in node tree, check to_node, to_socket, from_node, from_socket
[x for x in cube_mat.node_tree.links]

# get texcoord node
texcoord = [x for x in cube_mat.node_tree.nodes if x.bl_idname == 'ShaderNodeTexCoord'][0]

# create new uv mapping node
rgh_map_node = cube_mat.node_tree.nodes.new('ShaderNodeMapping')
rgh_map_node.vector_type = 'TEXTURE'
rgh_map_node.inputs['Location'].default_value = [0.0, -1.0, 0.0]
rgh_map_node.inputs['Rotation'].default_value = [-0.0, -0.0, -0.0]
cube_mat.node_tree.links.new(texcoord.outputs['UV'], rgh_map_node.inputs['Vector'])

# get all texture paths
tex_paths = [x.image.filepath for x in cube_mat.node_tree.nodes if x.bl_idname == 'ShaderNodeTexImage']
folder_hints = {os.path.dirname(x.image.filepath) for x in cube_mat.node_tree.nodes if x.bl_idname == 'ShaderNodeTexImage'}

