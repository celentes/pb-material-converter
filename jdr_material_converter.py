bl_info = {
    "name":        "JDR Material Converter",
    "description": "Upgrade materials with missing texture nodes",
    "author":      "Tim Talashok, t.talashok@gmail.com",
    "version":     (0, 1, 0),
    "blender":     (2, 82, 0)
}

import bpy
import os
import re

def texture_directories(context):
    jdr_props = context.window_manager.jdr_props
    return [x.directory for x in jdr_props.directories_list]

def get_material_textures(context, material):
    files = []
    for dir in texture_directories(context):
        files.extend([os.path.join(dir,f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir,f))])
    return [x for x in files if re.search(material.name, os.path.basename(x), flags=re.IGNORECASE)]

def get_texture_type(context, material, texname):
    cutoff = texname.find(material.name) + len(material.name)
    if texname[cutoff] == '_':
        cutoff += 1
    type = texname[cutoff:]
    if type[-3:] == "ive":
        type = type[:-3]
    elif type[-4:] == "ness":
        type = type[:-4]
    return type

def get_matching_socket(context, material, texname):
    shader = material.node_tree.nodes['Principled BSDF']
    sockets = shader.inputs
    textype = get_texture_type(context, material, texname)
    for x in sockets:
        if re.search(textype, x.name):
            return x
    return None

class JDR_texture_binding(bpy.types.PropertyGroup):
    connected: bpy.props.BoolProperty(name = "", default=False)
    path: bpy.props.StringProperty(name = "Path")
    socket: bpy.props.StringProperty(name = "Socket")

class JDR_material_props(bpy.types.PropertyGroup):
    material: bpy.props.PointerProperty(name="Material", type=bpy.types.Material)
    show: bpy.props.BoolProperty(name = "Bindings", default=False)
    selected: bpy.props.BoolProperty(name = "", default=False)
    bindings: bpy.props.CollectionProperty(type=JDR_texture_binding)

    def draw(self, layout, context):
        box = layout.box()
        col = box.column(align=True)
        for x in self.bindings:
            row = col.row(align=True)
            texname = os.path.splitext(os.path.basename(x.path))[0]
            row.label(text=texname)
            row.label(text=x.socket)
            #row.prop(x,"exclude")

def delete_dirline(self, context):
    dirlist = context.window_manager.jdr_props.directories_list
    # bloody hack because blender collections are stupid
    i = 0
    for dir in dirlist:
        if dir.delete==True:
            dirlist.remove(i)
        i += 1
    return None

class JDR_directory_line(bpy.types.PropertyGroup):
    directory: bpy.props.StringProperty(name="")
    delete: bpy.props.BoolProperty(name="", default=False, update=delete_dirline)

class JDR_props(bpy.types.PropertyGroup):
    mat_props_list: bpy.props.CollectionProperty(type=JDR_material_props)
    directories_list: bpy.props.CollectionProperty(type=JDR_directory_line)
    scanned: bpy.props.BoolProperty(default=False)

class JDR_add_directory(bpy.types.Operator):
    bl_idname = "jdr.add_directory"
    bl_label = "Add directory"

    def execute(self, context):
        context.window_manager.jdr_props.directories_list.add()
        return {'FINISHED'}

def mat_props_list_update(context, materials):
    jdr_props = context.window_manager.jdr_props
    jdr_props.mat_props_list.clear()
    jdr_props.directories_list.clear()
    jdr_props.scanned = False

    # fill out directory suggestions
    textures = []
    for mat in materials:
        textures.extend([x.image for x in mat.node_tree.nodes if x.bl_idname == 'ShaderNodeTexImage'])
    directory_hints = {os.path.dirname(x.filepath_from_user()) for x in textures}
    for x in directory_hints:
        dir = jdr_props.directories_list.add()
        dir.directory = x

    # fill out material props
    for mat in materials:
        mprop = jdr_props.mat_props_list.add()
        mprop.material = mat
        mat_textures = [x.image for x in mat.node_tree.nodes if x.bl_idname == 'ShaderNodeTexImage']
        blacklist = [x.filepath_from_user() for x in mat_textures]
        texnames = [x for x in get_material_textures(context,mat) if x not in blacklist]
        for tn in texnames:
            texname = os.path.splitext(os.path.basename(tn))[0]
            socket = get_matching_socket(context,mat,texname)
            binding = mprop.bindings.add()
            binding.path = tn
            binding.socket = "" if socket == None else socket.name

    jdr_props.scanned = True
    return

def connect_binding(context, material, binding):
    if binding.socket == "":
        return
    if binding.connected == True:
        return

    shader = material.node_tree.nodes['Principled BSDF']

    # create uv mapping node
    texcoord = [x for x in material.node_tree.nodes if x.bl_idname == 'ShaderNodeTexCoord'][0]
    uv_node = material.node_tree.nodes.new('ShaderNodeMapping')
    uv_node.vector_type = 'TEXTURE'
    uv_node.inputs['Location'].default_value = [0.0, -1.0, 0.0]
    uv_node.inputs['Rotation'].default_value = [-0.0, -0.0, -0.0]
    material.node_tree.links.new(texcoord.outputs['UV'], uv_node.inputs['Vector'])

    # set up image
    img_node = material.node_tree.nodes.new('ShaderNodeTexImage')
    img_node.image = bpy.data.images.load(binding.path)
    material.node_tree.links.new(uv_node.outputs['Vector'], img_node.inputs['Vector'])

    # set up final link
    socket = shader.inputs[binding.socket]
    material.node_tree.links.new(img_node.outputs['Color'], socket)

    binding.connected = True
    pass

class JDR_scan_materials(bpy.types.Operator):
    bl_idname = "jdr.scan_materials"
    bl_label = "Scan materials"

    def execute(self, context):
        materials = [x.active_material for x in bpy.data.objects if x.active_material is not None]
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
            for binding in mprop.bindings:
                connect_binding(context, mprop.material, binding)
        return {'FINISHED'}

class JDR_select_all_materials(bpy.types.Operator):
    bl_idname = "jdr.select_all_materials"
    bl_label = "Select all"

    def execute(self, context):
        for mprop in context.window_manager.jdr_props.mat_props_list:
            mprop.selected = True
        return {'FINISHED'}

class JDR_deselect_all_materials(bpy.types.Operator):
    bl_idname = "jdr.deselect_all_materials"
    bl_label = "Deselect all"

    def execute(self, context):
        for mprop in context.window_manager.jdr_props.mat_props_list:
            mprop.selected = False
        return {'FINISHED'}

class JDR_PT_main_panel(bpy.types.Panel):
    bl_idname = "JDRMC_UI"
    bl_label = "JDR Material Converter"
    bl_space_type = "PROPERTIES"
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        jdr_props = context.window_manager.jdr_props
        row = self.layout.row()
        row.operator("jdr.scan_materials")

        if (jdr_props.scanned is False):
            return

        self.layout.separator()
        dirs_row = self.layout.row(align=True)
        dirs_row.label(text="Texture directories")
        dirs_row.operator("jdr.add_directory")

        dirbox = self.layout.box()
        db_col = dirbox.column(align=True)
        for dirline in jdr_props.directories_list:
            dbc_row = db_col.row()
            dbc_row.prop(dirline, "directory")
            dbc_row.prop(dirline, "delete", icon="X")

        self.layout.separator()
        mats_row = self.layout.row(align=True)
        mats_row.label(text="Materials")
        mats_row.operator("jdr.select_all_materials")
        mats_row.operator("jdr.deselect_all_materials")

        matbox = self.layout.box()
        mb_col = matbox.column(align=True)
        mb_col.scale_y = 0.8
        for mprop in jdr_props.mat_props_list:
            mbc_row = mb_col.row()
            mbc_row.label(text = mprop.material.name)
            mbc_row.prop(mprop, "selected")
        selected_matprops = [x for x in jdr_props.mat_props_list if x.selected == True]

        col = self.layout.column(align=True)
        col.scale_y = 0.8
        for mprop in selected_matprops:
            mat = mprop.material
            #mprops['material'] = mat
            #mprops.directory = directory_hints.pop()
            icon = "TRIA_DOWN" if mprop.show else "TRIA_RIGHT"
            row = col.row()
            row.column(align=True).prop(mprop, "show", icon=icon)
            row.column(align=True).label(text=mat.name)
            if mprop.show:
                mprop.draw(col.row(), context)
        if len(selected_matprops) > 0:
            self.layout.row().operator("jdr.upgrade_materials")

classes = (
    JDR_texture_binding,
    JDR_material_props,
    JDR_directory_line,
    JDR_props,
    JDR_add_directory,
    JDR_scan_materials,
    JDR_select_all_materials,
    JDR_deselect_all_materials,
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
