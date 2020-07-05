import bpy
import os
import re
import sys

from . import texture_mapping as tm
from . import eevee
from . import octane

RENDERERS = [
    ("CYCLES", "Eevee/Cycles", ""),
    ("OCTANE", "Octane", ""),
]

RENDERER_BACKENDS = {
    "CYCLES" : eevee,
    "OCTANE" : octane,
}

def renderer_update(self, context):
    materials = [x.active_material for x in bpy.data.objects if x.active_material is not None]
    jdr_props = context.window_manager.jdr_props
    mat_props_list_update(context, materials)

def get_surface_shader(material):
    return material.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node

def is_octane_surface(surfaceShader):
    return surfaceShader.bl_idname == 'ShaderNodeOctUniversalMat'

def get_matching_textype(context, material, texname):
    renderer = RENDERER_BACKENDS[context.window_manager.jdr_props.renderer]
    textype = tm.get_texture_type(material.name, texname)
    return renderer.map_texture_type(textype)

class JDR_texture_binding(bpy.types.PropertyGroup):
    connected: bpy.props.BoolProperty(name = "", default=False)
    path: bpy.props.StringProperty(name = "Path")
    socket: bpy.props.StringProperty(name = "Socket")

class JDR_material_props(bpy.types.PropertyGroup):
    material: bpy.props.PointerProperty(name="Material", type=bpy.types.Material)
    selected: bpy.props.BoolProperty(name = "", default=True)
    bindings: bpy.props.CollectionProperty(type=JDR_texture_binding)
    show_bindings: bpy.props.BoolProperty(default=False)

    def draw(self, layout, context):
        m_col = layout.column(align=True)
        row = m_col.row(align=True)
        row.alignment = 'LEFT'
        row.emboss = 'PULLDOWN_MENU'
        row.prop(self,
                "show_bindings",
                text="    " + self.material.name,
                icon = "DOWNARROW_HLT" if self.show_bindings else "RIGHTARROW",
                emboss=False)
        if self.show_bindings:
            m_col.separator()
            _col = m_col.column(align=True)
            _col.alignment = 'LEFT'
            row = _col.row(align=True)
            row.alignment = 'LEFT'
            row.label(text="  ")
            col = row.column(align=True)
            col.alignment = 'LEFT'
            for x in self.bindings:
                texname = os.path.splitext(os.path.basename(x.path))[0]
                col.row().label(text=texname)
                r = col.row()
                r.enabled = False
                icon = "UNLINKED" if x.socket == tm.NOTMAPPED_STR else "LINKED"
                r.label(text="  " + x.socket, icon=icon)
                col.separator()
                #row.prop(x,"exclude")

class JDR_props(bpy.types.PropertyGroup):
    mat_props_list: bpy.props.CollectionProperty(type=JDR_material_props)
    directory: bpy.props.StringProperty(name="", subtype='DIR_PATH')
    scanned: bpy.props.BoolProperty(default=False)
    select_all: bpy.props.BoolProperty(default=False)
    show_dir: bpy.props.BoolProperty(default=False)
    show_bindings: bpy.props.BoolProperty(default=False)
    renderer: bpy.props.EnumProperty(items=RENDERERS, update=renderer_update)

def mat_props_list_update(context, materials):
    jdr_props = context.window_manager.jdr_props
    jdr_props.mat_props_list.clear()
    jdr_props.directory = ""
    jdr_props.scanned = False

    # fill out directory suggestions
    textures = []
    for mat in materials:
        textures.extend([x.image for x in mat.node_tree.nodes if x.bl_idname == 'ShaderNodeTexImage'])
    texture_paths = [os.path.abspath(x.filepath_from_user()) for x in textures]
    directory_hints = tm.get_directory_hints(texture_paths)
    if len(directory_hints) > 0:
        jdr_props.directory = directory_hints[0]

    # fill out material props
    for mat in materials:
        mprop = jdr_props.mat_props_list.add()
        mprop.material = mat
        mat_textures = [x.image for x in mat.node_tree.nodes if x.bl_idname == 'ShaderNodeTexImage']
        texnames = [x for x in tm.get_texture_filenames([jdr_props.directory], mat.name)]
        for tn in texnames:
            texname = os.path.splitext(os.path.basename(tn))[0]
            binding = mprop.bindings.add()
            binding.path = tn
            binding.socket = get_matching_textype(context,mat,texname)

    jdr_props.scanned = True
    return

def clear_material(context, material):
    jdr_props = context.window_manager.jdr_props
    renderer = RENDERER_BACKENDS[jdr_props.renderer]
    nodes = material.node_tree.nodes
    surface = get_surface_shader(material)

    if not renderer.is_surface_correct(surface):
        nodes.remove(surface)
        input_socket = nodes['Material Output'].inputs['Surface']
        surface = nodes.new(renderer.material_node())
        material.node_tree.links.new(surface.outputs[renderer.surface_output()], input_socket)

    to_remove = []
    to_remove.extend([x for x in nodes if x.bl_idname == 'ShaderNodeTexImage'])
    to_remove.extend([x for x in nodes if x.bl_idname == 'ShaderNodeMapping'])
    to_remove.extend([x for x in nodes if x.bl_idname == 'ShaderNodeNormalMap'])

    for n in to_remove:
        nodes.remove(n)

def connect_binding(context, material, binding):
    if binding.socket == tm.NOTMAPPED_STR:
        return
    if binding.connected == True:
        return

    shader = get_surface_shader(material)

    # create uv mapping node
    tc_nodes = [x for x in material.node_tree.nodes if x.bl_idname == 'ShaderNodeTexCoord']
    texcoord = material.node_tree.nodes.new('ShaderNodeTexCoord') if len(tc_nodes) == 0 else tc_nodes[0]
    uv_node = material.node_tree.nodes.new('ShaderNodeMapping')
    uv_node.vector_type = 'TEXTURE'
    #uv_node.inputs['Location'].default_value = [0.0, -1.0, 0.0]
    #uv_node.inputs['Rotation'].default_value = [-0.0, -0.0, -0.0]
    material.node_tree.links.new(texcoord.outputs['UV'], uv_node.inputs['Vector'])

    # set up image
    img_node = material.node_tree.nodes.new('ShaderNodeTexImage')
    img_node.image = bpy.data.images.load(binding.path)
    material.node_tree.links.new(uv_node.outputs['Vector'], img_node.inputs['Vector'])

    # set up final link
    socket = shader.inputs[binding.socket]

    renderer = RENDERER_BACKENDS[context.window_manager.jdr_props.renderer]
    if socket.name == "Displacement":
        renderer.map_displacement(material, img_node)
    elif socket.name == "Normal":
        nm_node = material.node_tree.nodes.new('ShaderNodeNormalMap')
        material.node_tree.links.new(img_node.outputs['Color'], nm_node.inputs['Color'])
        material.node_tree.links.new(nm_node.outputs['Normal'], socket)
    else:
        material.node_tree.links.new(img_node.outputs['Color'], socket)

    binding.connected = True

class JDR_scan_materials(bpy.types.Operator):
    bl_idname = "jdr.scan_materials"
    bl_label = "Scan materials"

    def execute(self, context):
        materials = [x.active_material for x in bpy.data.objects if x.active_material is not None]
        jdr_props = context.window_manager.jdr_props
        mat_props_list_update(context, materials)
        return {'FINISHED'}

class JDR_upgrade_materials(bpy.types.Operator):
    bl_idname = "jdr.upgrade_materials"
    bl_label = "Upgrade selected materials"

    def execute(self, context):
        jdr_props = context.window_manager.jdr_props
        if len(jdr_props.mat_props_list) == 0:
            self.report({"WARNING"}, "No materials have been selected")
            return {'FINISHED'}
        for mprop in jdr_props.mat_props_list:
            clear_material(context, mprop.material)
            for binding in mprop.bindings:
                connect_binding(context, mprop.material, binding)
        return {'FINISHED'}

class JDR_select_all_materials(bpy.types.Operator):
    bl_idname = "jdr.select_all_materials"
    bl_label = "Select all"

    def execute(self, context):
        b = all([mprop.selected for mprop in context.window_manager.jdr_props.mat_props_list])
        for mprop in context.window_manager.jdr_props.mat_props_list:
            mprop.selected = not b
        return {'FINISHED'}

class JDR_PT_main_panel(bpy.types.Panel):
    bl_idname = "JDRMC_UI"
    bl_label = "Photobash Material Converter"
    bl_space_type = "PROPERTIES"
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        jdr_props = context.window_manager.jdr_props
        row = self.layout.row()
        row.operator("jdr.scan_materials", icon="VIEWZOOM")

        if (jdr_props.scanned is False):
            return

        nr_mats = len(jdr_props.mat_props_list)
        mats_row = self.layout.row(align=True)
        mats_row.label(text="  " + str(nr_mats) + " Materials Found")
        mm_row = mats_row.row(align=True)
        mm_row.alignment = 'RIGHT'
        sa_icon = "CHECKBOX_HLT" if all([mprop.selected for mprop in context.window_manager.jdr_props.mat_props_list]) else "CHECKBOX_DEHLT"
        mm_row.operator("jdr.select_all_materials", emboss=False)
        mm_row.operator("jdr.select_all_materials", text="", emboss=False, icon=sa_icon)

        matbox = self.layout.box()
        mb_col = matbox.column(align=True)
        mb_col.scale_y = 0.8
        for mprop in jdr_props.mat_props_list:
            mbc_row = mb_col.row()
            mbc_row.label(text = mprop.material.name)
            mbc_row.prop(mprop, "selected")
        selected_matprops = [x for x in jdr_props.mat_props_list if x.selected == True]

        col = self.layout.column()

        # material bindings
        mp_row = col.row()
        mp_row.emboss = 'PULLDOWN_MENU'
        mp_row.prop(jdr_props,
                "show_bindings",
                text="View Material Links",
                icon = "TRIA_DOWN" if jdr_props.show_bindings else "TRIA_RIGHT",
                emboss=True)
        if jdr_props.show_bindings:
            mp_box = col.box().column(align=True)
            mp_box.scale_y = 0.8
            for mprop in selected_matprops:
                mprop.draw(mp_box, context)

        # texture directory
        tex_row = col.row()
        tex_row.emboss = 'PULLDOWN_MENU'
        tex_row.prop(jdr_props,
                "show_dir",
                text="Edit Texture Folder",
                icon = "TRIA_DOWN" if jdr_props.show_dir else "TRIA_RIGHT",
                emboss=True)
        if jdr_props.show_dir:
            dirs_row = self.layout.row(align=True)
            dirs_row.prop(jdr_props, "directory")

        # choose renderer
        col.row().prop(jdr_props, "renderer", text = "Renderer")

        if len(selected_matprops) > 0:
            self.layout.row().operator("jdr.upgrade_materials", text="Convert Selected Materials", icon="MATERIAL")

classes = (
    JDR_texture_binding,
    JDR_material_props,
    JDR_props,
    JDR_scan_materials,
    JDR_select_all_materials,
    JDR_upgrade_materials,
    JDR_PT_main_panel
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.WindowManager.jdr_props = bpy.props.PointerProperty(type=JDR_props)

def unregister():
    del bpy.types.WindowManager.jdr_props

    for c in reversed(classes):
        bpy.utils.unregister_class(c)
