import c4d
import os
from texture_mapping import get_texture_filenames, get_texture_type, get_directory_hints

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
    return [os.path.abspath(x[c4d.BITMAPSHADER_FILENAME]) for x in shaders]

def get_directory_hints_c4d():
    mats = get_all_materials_c4d()
    tf_list = []
    [tf_list.extend(get_material_texture_paths_c4d(m)) for m in mats]
    return get_directory_hints(tf_list)

def recursive_apply(obj, op):
    while (obj):
        op(obj)
        recursive_apply(obj.GetDown(), op)
        obj = obj.GetNext()

def get_all_objects(doc):
    objects = []
    a = lambda o: objects.append(o)
    for x in doc.GetObjects():
        recursive_apply(x, a)
    return objects

def replace_material(doc, oldmat, newmat):
    ID_MATERIAL_TAG = 5616
    objects = [x for x in get_all_objects(doc)]
    tags = []
    for o in objects:
        tags.extend([x for x in o.GetTags() if x.GetType() == ID_MATERIAL_TAG])
    filtered = [x for x in tags if x[c4d.TEXTURETAG_MATERIAL] == oldmat]
    for x in filtered:
        x[c4d.TEXTURETAG_MATERIAL] = newmat
    oldmat.Remove()
    newmat.SetName(newmat.GetName()[:-2]) # truncate .1 suffix

SCROLLGRP_MAIN=500
BTN_SCAN_MATERIALS=1000
GRP_CONTROL=1001
GRP_CHANGE_DIR=2000
EDITBOX_TEXTURE_DIR=2002
BTN_CHANGE_DIR=2003
STRPROPS_DIR=2100
BTNS_DELETE_DIR=2200
GRP_MATERIAL_SELECT=3000
CHKBOX_SELECT_ALL_MATS=3002
CHKBOXES_MATERIAL_SELECT=3200
GRP_MATERIAL_BINDINGS=5000
SCGRP_BINDINGS=5500
GRPS_BINDING=5100
BTN_UPGRADE=9000
SG_TEXTURE_DIR=10000
SG_TEXTURE_DIR_GRP=10001
SG_BINDINGS=11000
SG_BINDINGS_GRP=11001
CB_RENDERER=12000
SG_MSELECT=13000
SG_MBS=14000

class PBMC_Dialog(c4d.gui.GeDialog):
    materials = []
    directory = ""
    renderers = dict()
    rnd_ids = dict()
    rnd = None

    texture_dir_sg = None
    texture_dir_hide = True

    mselect_sg = None
    mselect_hide = True

    bindings_sg = None
    bindings_hide = True

    mb_sgs = []
    mb_hides = []

    def query_renderers(self):
        i = 0
        import physical
        self.renderers["Physical/ProRender"] = physical
        self.rnd_ids[i] = "Physical/ProRender"
        self.rnd = physical
        i += 1

        if c4d.plugins.FindPlugin(1038954) is not None:
            print "PBMC: Found vray plugin"
            import vray
            self.renderers["VRay"] = vray
            self.rnd_ids[i] = "VRay"
            i += 1
        if c4d.plugins.FindPlugin(1041569) is not None:
            print "PBMC: Found octane plugin"
            import octane
            self.renderers["Octane"] = octane
            self.rnd_ids[i] = "Octane"
            i += 1
        if c4d.plugins.FindPlugin(1033991) is not None:
            print "PBMC: Found arnold plugin"
            import arnold
            self.renderers["Arnold"] = arnold
            self.rnd_ids[i] = "Arnold"
            i += 1

    def fill_materials(self, mats):
        self.materials = mats

    def fill_directory(self, dir):
        self.directory = dir

    def selected_material_ids(self):
        return [i for i in range(len(self.materials)) if self.GetBool(CHKBOXES_MATERIAL_SELECT+i)]

    def redraw_materials(self):
        self.LayoutFlushGroup(id=GRP_MATERIAL_SELECT)
        for i in range(len(self.materials)):
            self.AddStaticText(90000+i,c4d.BFH_SCALEFIT, name="  " + self.materials[i].GetName())
            self.AddCheckbox(CHKBOXES_MATERIAL_SELECT+i, c4d.BFH_RIGHT, initw=5, inith=5, name="")
            self.SetBool(CHKBOXES_MATERIAL_SELECT+i, True)
        self.LayoutChanged(id=GRP_MATERIAL_SELECT)

    def draw_material_bindings(self):
        for mat_id in range(len(self.materials)):
            self.LayoutFlushGroup(id=GRPS_BINDING+mat_id)
            texture_files = get_texture_filenames([self.directory], self.materials[mat_id].GetName())
            for i in range(len(texture_files)):
                txt, ext = os.path.splitext(os.path.basename(texture_files[i]))
                if mat_id in self.selected_material_ids():
                    textype = get_texture_type(self.materials[mat_id].GetName(),txt)
                    bname = "   " + self.rnd.get_binding_name(textype)
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
            self.HideElement(SG_MBS+i, hide)
            self.HideElement(GRPS_BINDING+i,hide or self.mb_hides[i])
        self.LayoutChanged(id=GRP_MATERIAL_BINDINGS)

    def CreateLayout(self):
        self.SetTitle("Photobash Material Converter")
        self.AddButton(BTN_SCAN_MATERIALS, c4d.BFH_SCALEFIT, name="Scan Materials")

        #self.ScrollGroupBegin(id=SCROLLGRP_MAIN, flags=c4d.BFH_SCALEFIT, inith=120, scrollflags=c4d.SCROLLGROUP_VERT)
        self.GroupBegin(id=GRP_CONTROL,flags=c4d.BFH_SCALEFIT,cols=1)
        self.GroupEnd()
        #self.GroupEnd()

        return True

    def fill_control_group_layout(self):
        self.LayoutFlushGroup(id=GRP_CONTROL)

        self.AddSeparatorH(1)

        # materials selection

        self.GroupBegin(id=99002, flags=c4d.BFH_SCALEFIT, cols=4)
        self.AddStaticText(id=99003,flags=c4d.BFH_LEFT,name="   "+str(len(self.materials)),borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        self.AddStaticText(id=99004,flags=c4d.BFH_SCALEFIT,name="Materials Found")
        self.AddStaticText(id=99005,flags=c4d.BFH_RIGHT,name="Select All")
        self.AddCheckbox(id=CHKBOX_SELECT_ALL_MATS,flags=c4d.BFH_RIGHT,initw=5,inith=5,name="")
        self.SetBool(CHKBOX_SELECT_ALL_MATS, True)
        self.GroupEnd()

        self.AddSeparatorH(1)

        mselect_bc = c4d.BaseContainer()
        mselect_bc.SetBool(c4d.QUICKTAB_BAR, 1)
        mselect_bc.SetString(c4d.QUICKTAB_BARTITLE, "   Material Selection")
        mselect_bc.SetBool(c4d.QUICKTAB_BARSUBGROUP, True)
        self.mselect_sg = self.AddCustomGui(SG_MSELECT, c4d.CUSTOMGUI_QUICKTAB, '', c4d.BFH_SCALEFIT, 0, 0, mselect_bc)
        self.mselect_sg.Select(0, self.mselect_hide)

        self.GroupBegin(id=GRP_MATERIAL_SELECT,flags=c4d.BFH_SCALEFIT,cols=2)
        self.GroupSpace(0,1)
        self.GroupEnd()
        self.HideElement(GRP_MATERIAL_SELECT, self.mselect_hide)

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
            mb_bc = c4d.BaseContainer()
            mb_bc.SetBool(c4d.QUICKTAB_BAR, 1)
            mb_bc.SetString(c4d.QUICKTAB_BARTITLE, "        " + self.materials[i].GetName())
            mb_bc.SetBool(c4d.QUICKTAB_BARSUBGROUP, True)
            mb_sg = self.AddCustomGui(SG_MBS+i, c4d.CUSTOMGUI_QUICKTAB, '', c4d.BFH_SCALEFIT, 0, 0, mb_bc)

            self.mb_sgs.append(mb_sg)
            self.mb_hides.append(True)
            self.mb_sgs[i].Select(0, self.mb_hides[i])

            self.GroupBegin(id=GRPS_BINDING+i,flags=c4d.BFH_SCALEFIT,cols=1)
            self.GroupSpace(0,0)
            self.GroupEnd()
            self.HideElement(GRPS_BINDING+i, self.mb_hides[i])
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

        self.GroupBegin(id=GRP_CHANGE_DIR,flags=c4d.BFH_SCALEFIT,cols=2)
        self.AddEditText(id=EDITBOX_TEXTURE_DIR,flags=c4d.BFH_SCALEFIT)
        self.Enable(EDITBOX_TEXTURE_DIR,False)
        self.SetString(EDITBOX_TEXTURE_DIR,self.directory)
        self.AddButton(id=BTN_CHANGE_DIR,flags=c4d.BFH_RIGHT,name="...")
        self.GroupEnd()

        self.GroupEnd()
        self.HideElement(SG_TEXTURE_DIR_GRP, self.texture_dir_hide)

        # choose renderer

        self.GroupBegin(id=CB_RENDERER+1, flags=c4d.BFH_SCALEFIT, cols=2)
        self.AddStaticText(id=CB_RENDERER+2, flags=c4d.BFH_LEFT, name="Renderer")
        rnd_bc = c4d.BaseContainer()
        for key in self.rnd_ids:
            rnd_bc.SetString(key, self.rnd_ids[key])
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
            self.fill_directory(get_directory_hints_c4d()[0])
            self.fill_control_group_layout()
            self.redraw_materials()
            self.redraw_bindings()

        if id == CHKBOX_SELECT_ALL_MATS:
            status = self.GetBool(id)
            for i in range(len(self.materials)):
                self.SetBool(CHKBOXES_MATERIAL_SELECT+i, status)
            self.redraw_bindings()

        if id == BTN_CHANGE_DIR:
            folder = c4d.storage.LoadDialog(flags=c4d.FILESELECT_DIRECTORY)
            self.SetString(EDITBOX_TEXTURE_DIR, folder)
            self.directory = folder
            self.redraw_bindings()

        if id >= CHKBOXES_MATERIAL_SELECT and id < CHKBOXES_MATERIAL_SELECT+len(self.materials):
            all_selected = all([self.GetBool(CHKBOXES_MATERIAL_SELECT+i) for i in range(len(self.materials))])
            self.SetBool(CHKBOX_SELECT_ALL_MATS, all_selected)
            self.redraw_bindings()

        if id == BTN_UPGRADE:
            ids = self.selected_material_ids()
            mats = [self.materials[i] for i in ids]
            doc = c4d.documents.GetActiveDocument()
            for m in mats:
                newmat = self.rnd.upgrade_material(m, [self.directory])
                replace_material(doc, m, newmat)
            c4d.EventAdd(c4d.EVENT_FORCEREDRAW)
            self.Close()

        if id == SG_TEXTURE_DIR:
            self.texture_dir_hide = not self.texture_dir_hide
            self.HideElement(SG_TEXTURE_DIR_GRP, self.texture_dir_hide)
            self.LayoutChanged(GRP_CONTROL)

        if id == SG_BINDINGS:
            self.bindings_hide = not self.bindings_hide
            self.HideElement(SG_BINDINGS_GRP, self.bindings_hide)
            self.LayoutChanged(GRP_CONTROL)

        if id == SG_MSELECT:
            self.mselect_hide = not self.mselect_hide
            self.HideElement(GRP_MATERIAL_SELECT, self.mselect_hide)
            self.LayoutChanged(GRP_CONTROL)

        if id >= SG_MBS and id < SG_MBS + len(self.materials):
            i = id - SG_MBS;
            self.mb_hides[i] = not self.mb_hides[i]
            hide = i not in self.selected_material_ids()
            hide = hide or self.mb_hides[i]
            self.HideElement(GRPS_BINDING+i, hide)
            self.LayoutChanged(GRP_CONTROL)

        if id == CB_RENDERER:
            _id = self.GetInt32(CB_RENDERER)
            _key = self.rnd_ids.keys()[_id]
            _name = self.rnd_ids[_key]
            _rnd = self.renderers[_name]
            self.rnd = _rnd
            self.redraw_bindings()
            print "PBMC: Setting renderer to " + _name

        return True
