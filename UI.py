import c4d
import os
from TextureMapping import get_texture_filenames, get_texture_type, get_directory_hints

def get_all_materials_c4d():
    doc = c4d.documents.GetActiveDocument()
    mats = [x for x in doc.GetMaterials() if x.GetType() == c4d.Mmaterial]
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
SG_TEXTURE_DIR=10000
SG_TEXTURE_DIR_GRP=10001
SG_BINDINGS=11000
SG_BINDINGS_GRP=11001
CB_RENDERER=12000

class JDR_dialog(c4d.gui.GeDialog):
    materials = []
    directories = []
    renderers = dict()
    rnd = None

    texture_dir_sg = None
    texture_dir_hide = True

    bindings_sg = None
    bindings_hide = True

    def query_renderers(self):
        if c4d.plugins.FindPlugin(1041569) is not None:
            print "PBMC: Found octane plugin"
            import octane
            self.renderers["Octane"] = octane
            self.rnd = octane
        # self.rnd = 

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

    def draw_material_bindings(self):
        for mat_id in range(len(self.materials)):
            self.LayoutFlushGroup(id=GRPS_BINDING+mat_id)
            texture_files = get_texture_filenames(self.directories, self.materials[mat_id].GetName())
            for i in range(len(texture_files)):
                txt, ext = os.path.splitext(os.path.basename(texture_files[i]))
                if mat_id in self.selected_material_ids():
                    textype = get_texture_type(self.materials[mat_id].GetName(),txt)
                    binding = self.rnd.get_binding(textype)
                    bname = "NOT MAPPABLE" if binding is None else binding.name()
                    bname = "   " + bname
                    _txt =  "   " + txt
                    self.AddStaticText(91000+2*mat_id, c4d.BFH_SCALEFIT, name=_txt)
                    b_text = self.AddStaticText(91000+2*mat_id+1, c4d.BFH_SCALEFIT, name=bname, borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
                    self.Enable(b_text, False)
            self.LayoutChanged(id=GRPS_BINDING+mat_id)

    def redraw_bindings(self):
        # I have no idea why redrawing them is necessary, but c4d is retarded
        self.draw_material_bindings()

        for i in range(len(self.materials)):
            hide = i not in self.selected_material_ids()
            self.HideElement(GRPS_BINDING+i,hide)
        self.LayoutChanged(id=GRP_MATERIAL_BINDINGS)

    def CreateLayout(self):
        self.SetTitle("Photobash Material Converter")
        self.AddButton(BTN_SCAN_MATERIALS, c4d.BFH_SCALEFIT, name="Scan materials")

        self.GroupBegin(id=GRP_CONTROL,flags=c4d.BFH_SCALEFIT,cols=1)
        self.GroupEnd()

        return True

    def fill_control_group_layout(self):
        self.LayoutFlushGroup(id=GRP_CONTROL)

        self.AddSeparatorH(1)

        # materials selection 

        self.GroupBegin(id=99002, flags=c4d.BFH_SCALEFIT, cols=2)
        self.AddStaticText(id=99003,flags=c4d.BFH_LEFT,name="   "+str(len(self.materials)),borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        self.AddStaticText(id=99004,flags=c4d.BFH_SCALEFIT,name="Materials found")
        self.GroupEnd()

        self.GroupBegin(id=GRP_MATERIAL_SELECT_CONTROL,flags=c4d.BFH_SCALEFIT,cols=2)
        self.AddButton(id=BTN_SELECT_ALL_MATS,flags=c4d.BFH_SCALEFIT,name="Select all")
        self.AddButton(id=BTN_DESELECT_ALL_MATS,flags=c4d.BFH_SCALEFIT,name="Deselect all")
        self.GroupEnd()

        self.GroupBegin(id=GRP_MATERIAL_SELECT,flags=c4d.BFH_SCALEFIT,cols=2)
        self.GroupSpace(0,1)
        self.GroupEnd()

        self.AddSeparatorH(1)

        # materials expansion group

        bindings_bc = c4d.BaseContainer()
        bindings_bc.SetBool(c4d.QUICKTAB_BAR, 1)
        bindings_bc.SetString(c4d.QUICKTAB_BARTITLE, "   View Material Links")
        bindings_bc.SetBool(c4d.QUICKTAB_BARSUBGROUP, True)
        self.bindings_sg = self.AddCustomGui(SG_BINDINGS, c4d.CUSTOMGUI_QUICKTAB, '', c4d.BFH_SCALEFIT, 0, 0, bindings_bc)
        self.bindings_sg.Select(0, self.bindings_hide)

        self.GroupBegin(id=SG_BINDINGS_GRP,flags=c4d.BFH_SCALEFIT,cols=1)

        self.GroupBegin(id=GRP_MATERIAL_BINDINGS,flags=c4d.BFH_SCALEFIT,cols=1)
        self.GroupSpace(0,0)
        for i in range(len(self.materials)):
            self.GroupBegin(id=GRPS_BINDING+i,flags=c4d.BFH_SCALEFIT,cols=1, title=self.materials[i].GetName())
            self.GroupSpace(0,0)
            self.GroupBorder(c4d.BORDER_GROUP_TOP)
            self.GroupEnd()
        self.GroupEnd()

        self.GroupEnd()
        self.HideElement(SG_BINDINGS_GRP, self.bindings_hide)

        # texture directories subgroup

        tex_bc = c4d.BaseContainer()
        tex_bc.SetBool(c4d.QUICKTAB_BAR, 1)
        tex_bc.SetString(c4d.QUICKTAB_BARTITLE, "   Edit Texture Folder")
        tex_bc.SetBool(c4d.QUICKTAB_BARSUBGROUP, True)
        self.texture_dir_sg = self.AddCustomGui(SG_TEXTURE_DIR, c4d.CUSTOMGUI_QUICKTAB, '', c4d.BFH_SCALEFIT, 0, 0, tex_bc)
        self.texture_dir_sg.Select(0, self.texture_dir_hide)

        self.GroupBegin(id=SG_TEXTURE_DIR_GRP,flags=c4d.BFH_SCALEFIT,cols=1)

        self.GroupBegin(id=GRP_ADD_DIR,flags=c4d.BFH_SCALEFIT,cols=2)
        self.AddEditText(id=EDITBOX_ADD_DIR,flags=c4d.BFH_SCALEFIT)
        self.AddButton(id=BTN_ADD_DIR,flags=c4d.BFH_RIGHT,name="Add directory")
        self.GroupEnd()

        self.GroupBegin(id=GRP_TEXTURE_DIRS,flags=c4d.BFH_SCALEFIT,title="Textures",cols=2)
        self.GroupSpace(0,0)
        self.GroupEnd()

        self.GroupEnd()
        self.HideElement(SG_TEXTURE_DIR_GRP, self.texture_dir_hide)

        # choose renderer 

        self.GroupBegin(id=CB_RENDERER+1, flags=c4d.BFH_SCALEFIT, cols=2)
        self.AddStaticText(id=CB_RENDERER+2, flags=c4d.BFH_LEFT, name="Renderer")
        rnd_bc = c4d.BaseContainer()
        for i in range(len(self.renderers)):
            rnd_bc.SetString(i, self.renderers.keys()[i])
        self.AddComboBox(id=CB_RENDERER,flags=c4d.BFH_SCALEFIT)
        self.AddChildren(CB_RENDERER, rnd_bc)
        self.GroupEnd()

        # upgrade materials 

        self.AddButton(id=BTN_UPGRADE,flags=c4d.BFH_SCALEFIT,name="Convert Selected Materials")

        self.LayoutChanged(id=GRP_CONTROL)

    def Command(self, id, msg):
        if id == BTN_SCAN_MATERIALS:
            self.query_renderers()
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
                self.rnd.upgrade_material(m, self.directories)

        if id == SG_TEXTURE_DIR:
            self.texture_dir_hide = not self.texture_dir_hide
            self.HideElement(SG_TEXTURE_DIR_GRP, self.texture_dir_hide)
            self.LayoutChanged(GRP_CONTROL)

        if id == SG_BINDINGS:
            self.bindings_hide = not self.bindings_hide
            self.HideElement(SG_BINDINGS_GRP, self.bindings_hide)
            self.LayoutChanged(GRP_CONTROL)
        
        if id == CB_RENDERER:
            _id = self.GetInt32(CB_RENDERER)
            _name = self.renderers.keys()[_id]
            _rnd = self.renderers[_name]
            self.rnd = _rnd
            print "PBMC: Setting renderer to " + _name

        return True