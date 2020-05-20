import c4d
from c4d import gui
import os
import re

TEXTURE_TYPE_DICT = {
    "emissive" : "Emission",
    "emission" : "Emission",
    
    "diffuse" : "Diffuse",
    "color" : "Diffuse",
    "basecolor" : "Diffuse",
    "albedo" : "Diffuse",
    
    "spec" : "Specular",
    
    "normal" : "Normal",
    
    "rough" : "Roughness",
    "roughness" : "Roughness",
    "gloss" : "Roughness", # add quirks too
    
    "metal" : "Metalness",
    "metallic" : "Metalness",
    "metalness" : "Metalness",
    
    "ao" : "AmbientOcclusion",
    
    "height" : "Height",
    
    "bump" : "Bump",
}

OCTANE_BINDINGS = {
#    "Emission" : "Emission",
    "Roughness" : "Roughness",
    "Diffuse" : "Diffuse",
    "Specular" : "Specular",
    "Normal" : "Normal",
    "Bump" : "Bump",
#    "Metalness" : "Metallic",
}

OCTANE_BINDING_IDS = {
    "Roughness" : c4d.OCT_MATERIAL_ROUGHNESS_LINK,
    "Diffuse" : c4d.OCT_MATERIAL_DIFFUSE_LINK,
    "Specular" : c4d.OCT_MATERIAL_SPECULAR_LINK,
    "Normal" : c4d.OCT_MATERIAL_NORMAL_LINK,
    "Bump" : c4d.OCT_MATERIAL_BUMP_LINK,
}

octane_link_types = ['Diffuse', 'Roughness', 'Reflection', 'Bump', 'Normal', 'Opacity', 'Transmission', 'Emission']

def get_texture_filenames(directories, material_name):
    files = []
    for dir in directories:
        files.extend([os.path.join(dir,f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir,f))])
    return [x for x in files if re.search(material_name, os.path.basename(x), flags=re.IGNORECASE)]

def get_texture_type(material_name, tex_filename):
    texname, ext = os.path.splitext(os.path.basename(tex_filename))
    i_cutoff = texname.find(material_name) + len(material_name)
    if texname[i_cutoff] == '_':
        i_cutoff += 1
    textype = texname[i_cutoff:]
    if textype.lower() in TEXTURE_TYPE_DICT:
        return TEXTURE_TYPE_DICT[textype.lower()]
    else:
        return textype

def get_directory_hints(texfile_list):
    if texfile_list == None:
        return []
    dir_hints = {os.path.dirname(x) for x in texfile_list}
    return [x for x in dir_hints]

def create_octane_texture(filename):
    ID_OCTANE_IMAGETEXTURE = 1029508
    #shd = c4d.BaseShader(ID_OCTANE_IMAGETEXTURE)
    #shd[c4d.IMAGETEXTURE_FILE] = filename
    shd = c4d.BaseShader(c4d.Xbitmap)
    shd[c4d.BITMAPSHADER_FILENAME] = filename
    return shd

def create_octane_material():
    ID_OCTANE_MATERIAL=1029501
    mat = c4d.BaseMaterial(ID_OCTANE_MATERIAL)
    return mat

def upgrade_material_octane(mat, directories):
    name = mat.GetName()
    texfiles = get_texture_filenames(directories, name)
    
    oct_mat = create_octane_material()
    oct_mat.SetName(name+"_octane")
    for tf in texfiles:
        textype = get_texture_type(name,tf)
        if textype not in OCTANE_BINDING_IDS:
            continue
        shd = create_octane_texture(tf)
        shd.SetName(textype)
        link = OCTANE_BINDING_IDS[textype]
        oct_mat.InsertShader(shd)
        oct_mat[link] = shd
        shd[c4d.IMAGETEXTURE_RELOADIMAGE]
    doc = c4d.documents.GetActiveDocument()
    doc.InsertMaterial(oct_mat)
    doc.SetActiveMaterial(oct_mat,c4d.SELECTION_NEW)
    doc.GetActiveMaterial()
    
def get_all_materials_c4d():
    doc = c4d.documents.GetActiveDocument()
    mats = doc.GetMaterials()
    return mats

def get_material_texture_paths_c4d(material):
    beg = material.GetFirstShader()
    it = beg
    shaders = []
    while it != None:
        shaders.append(it)
        it = it.GetNext()
    return [x[c4d.BITMAPSHADER_FILENAME] for x in shaders]

def get_directory_hints_c4d():
    mats = get_all_materials_c4d()
    tf_list = []
    [tf_list.extend(get_material_texture_paths_c4d(m)) for m in mats]
    return get_directory_hints(tf_list)

# TODO: bloody dictionary
# TODO: bloody specs

BTN_SCAN_MATERIALS=1000
GRP_CONTROL=1001
GRP_TEXTURE_DIRS=2000
GRP_ADD_DIR=2001
EDITBOX_ADD_DIR=2002
BTN_ADD_DIR=2003
STRPROPS_DIR=2100
BTNS_DELETE_DIR=2200
GRP_MATERIAL_SELECT=3000
GRP_MATERIAL_SELECT_CONTROL=3001
BTN_SELECT_ALL_MATS=3002
BTN_DESELECT_ALL_MATS=3003
CHKBOXES_MATERIAL_SELECT=3200
GRP_MATERIAL_BINDINGS=5000
GRPS_BINDING=5100
BTN_UPGRADE=9000

class JDR_dialog(c4d.gui.GeDialog):
    materials = []
    directories = []

    def fill_materials(self, mats):
        self.materials = mats

    def fill_directories(self, dirs):
        self.directories = dirs
        
    def selected_material_ids(self):
        return [i for i in range(len(self.materials)) if self.GetBool(CHKBOXES_MATERIAL_SELECT+i)]

    def redraw_texture_dirs(self):
        self.LayoutFlushGroup(id=GRP_TEXTURE_DIRS)
        for i in range(len(self.directories)):
            self.AddStaticText(id=STRPROPS_DIR+i,flags=c4d.BFH_SCALEFIT, name=self.directories[i])
            self.AddButton(id=BTNS_DELETE_DIR+i,flags=c4d.BFH_RIGHT, name="X")
        self.LayoutChanged(id=GRP_TEXTURE_DIRS)

    def redraw_materials(self):
        self.LayoutFlushGroup(id=GRP_MATERIAL_SELECT)
        for i in range(len(self.materials)):
            self.AddStaticText(90000+i,c4d.BFH_SCALEFIT, name=self.materials[i].GetName())
            self.AddCheckbox(CHKBOXES_MATERIAL_SELECT+i, c4d.BFH_RIGHT, initw=5, inith=5, name="")
        self.LayoutChanged(id=GRP_MATERIAL_SELECT)
    
    def redraw_material_binding(self, mat_id):
        self.LayoutFlushGroup(id=GRPS_BINDING+mat_id)
        texture_files = get_texture_filenames(self.directories, self.materials[mat_id].GetName())
        for i in range(len(texture_files)):
            txt, ext = os.path.splitext(os.path.basename(texture_files[i]))
            if mat_id in self.selected_material_ids():
                self.AddStaticText(91000+mat_id, c4d.BFH_SCALEFIT, name=txt)
        self.LayoutChanged(id=GRPS_BINDING+mat_id)
        
    def redraw_bindings(self):
        for i in range(len(self.materials)):
            self.redraw_material_binding(i)
#        self.LayoutFlushGroup(id=GRP_MATERIAL_BINDINGS)
#        for i in range(len(texture_files)):
#            txt, ext = os.path.splitext(os.path.basename(texture_files[i]))
#            self.AddStaticText(91000+i, c4d.BFH_SCALEFIT, name=txt)
#        self.LayoutChanged(id=GRP_MATERIAL_BINDINGS)

    def CreateLayout(self):
        self.SetTitle("JDR Material Converter")
        self.AddButton(BTN_SCAN_MATERIALS, c4d.BFH_SCALEFIT, name="Scan materials")

        self.GroupBegin(id=GRP_CONTROL,flags=c4d.BFH_SCALEFIT,cols=1)
        self.GroupEnd()

        return True

    def fill_control_group_layout(self):
        self.LayoutFlushGroup(id=GRP_CONTROL)

        self.AddSeparatorH(1)

        self.AddStaticText(id=99001,flags=c4d.BFH_CENTER,name="Texture directories")

        self.GroupBegin(id=GRP_ADD_DIR,flags=c4d.BFH_SCALEFIT,cols=2)
        self.AddEditText(id=EDITBOX_ADD_DIR,flags=c4d.BFH_SCALEFIT)
        self.AddButton(id=BTN_ADD_DIR,flags=c4d.BFH_RIGHT,name="Add directory")
        self.GroupEnd()

        # texture directories group
        self.GroupBegin(id=GRP_TEXTURE_DIRS,flags=c4d.BFH_SCALEFIT,title="Textures",cols=2)
        self.GroupSpace(0,0)
        self.GroupEnd()

        self.AddSeparatorH(1)

        self.AddStaticText(id=99002,flags=c4d.BFH_CENTER,name="Material Selection")

        self.GroupBegin(id=GRP_MATERIAL_SELECT_CONTROL,flags=c4d.BFH_SCALEFIT,cols=2)
        self.AddButton(id=BTN_SELECT_ALL_MATS,flags=c4d.BFH_SCALEFIT,name="Select all")
        self.AddButton(id=BTN_DESELECT_ALL_MATS,flags=c4d.BFH_SCALEFIT,name="Deselect all")
        self.GroupEnd()

        # materials selection group
        self.GroupBegin(id=GRP_MATERIAL_SELECT,flags=c4d.BFH_SCALEFIT,cols=2)
        self.GroupSpace(0,1)
        self.GroupEnd()

        # materials expansion group
        self.GroupBegin(id=GRP_MATERIAL_BINDINGS,flags=c4d.BFH_SCALEFIT,cols=1)
        self.GroupSpace(0,1)
        for i in range(len(self.materials)):
            self.GroupBegin(id=GRPS_BINDING+i,flags=c4d.BFH_SCALEFIT,cols=1)
            self.GroupEnd()
        self.GroupEnd()
        
        self.AddButton(id=BTN_UPGRADE,flags=c4d.BFH_SCALEFIT,name="Upgrade")

        self.LayoutChanged(id=GRP_CONTROL)

    def Command(self, id, msg):
        if id == BTN_SCAN_MATERIALS:
            self.fill_materials(get_all_materials_c4d())
            self.fill_directories(get_directory_hints_c4d())
            self.fill_control_group_layout()
            self.redraw_materials()
            self.redraw_texture_dirs()
            self.redraw_bindings()
        
        if id == BTN_SELECT_ALL_MATS:
            for i in range(len(self.materials)):
                self.SetBool(CHKBOXES_MATERIAL_SELECT+i, True)
            self.redraw_bindings()
        
        if id == BTN_DESELECT_ALL_MATS:
            for i in range(len(self.materials)):
                self.SetBool(CHKBOXES_MATERIAL_SELECT+i, False)
            self.redraw_bindings()
                
        if id >= BTNS_DELETE_DIR and id < BTNS_DELETE_DIR+len(self.directories):
            self.directories.pop(id-BTNS_DELETE_DIR)
            self.redraw_texture_dirs()
            
        if id == BTN_ADD_DIR:
            dir = self.GetString(EDITBOX_ADD_DIR)
            self.directories.append(dir)
            self.redraw_texture_dirs()
            
        if id >= CHKBOXES_MATERIAL_SELECT and id < CHKBOXES_MATERIAL_SELECT+len(self.materials):
            self.redraw_bindings()
            
        if id == BTN_UPGRADE:
            ids = self.selected_material_ids()
            mats = [self.materials[i] for i in ids]
            for m in mats:
                upgrade_material_octane(m, self.directories)

        return True

# Main function
def main():
    jdr = JDR_dialog()
    jdr.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=300, defaulth=500, xpos=-2, ypos=-2)
    #gui.MessageDialog('Hello World!')

# Execute main()
if __name__=='__main__':
    main()
#    mats = get_all_materials()
#    tpaths = []
#    [tpaths.extend(get_material_texture_paths(m)) for m in mats]
#    dir_hints = {os.path.dirname(tp) for tp in tpaths}
#    for d in dir_hints:
#        print d